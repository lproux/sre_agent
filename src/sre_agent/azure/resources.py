"""Azure Resource Manager integration.

Provides high-level helpers for the most common SRE remediation actions:

* Restarting a virtual machine
* Scaling a VM scale-set
* Restarting a node pool in an AKS cluster
* Listing resources in a subscription / resource group
"""

from __future__ import annotations

import logging

from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import GenericResourceExpanded

from sre_agent.azure.client import AzureClient

logger = logging.getLogger(__name__)


class AzureResourceManager:
    """Thin wrapper around Azure management clients for SRE remediations.

    Parameters
    ----------
    client:
        Authenticated :class:`AzureClient` instance.
    dry_run:
        When ``True``, mutating operations are logged but not executed.
    """

    def __init__(self, client: AzureClient, dry_run: bool = False) -> None:
        self._client = client
        self._dry_run = dry_run
        self._compute: ComputeManagementClient | None = None
        self._resource: ResourceManagementClient | None = None
        self._container_service: ContainerServiceClient | None = None

    # -------------------------------------------------------- SDK client helpers

    @property
    def _compute_client(self) -> ComputeManagementClient:
        if self._compute is None:
            self._compute = ComputeManagementClient(
                credential=self._client.credential,  # type: ignore[arg-type]
                subscription_id=self._client.subscription_id,
            )
        return self._compute

    @property
    def _resource_client(self) -> ResourceManagementClient:
        if self._resource is None:
            self._resource = ResourceManagementClient(
                credential=self._client.credential,  # type: ignore[arg-type]
                subscription_id=self._client.subscription_id,
            )
        return self._resource

    @property
    def _aks_client(self) -> ContainerServiceClient:
        if self._container_service is None:
            self._container_service = ContainerServiceClient(
                credential=self._client.credential,  # type: ignore[arg-type]
                subscription_id=self._client.subscription_id,
            )
        return self._container_service

    # ---------------------------------------------------------------- resources

    def list_resources(
        self,
        resource_group: str | None = None,
        resource_type: str | None = None,
    ) -> list[GenericResourceExpanded]:
        """List resources in the subscription, optionally filtered.

        Parameters
        ----------
        resource_group:
            When provided, only resources in this group are returned.
        resource_type:
            Filter by resource type (e.g. ``"Microsoft.Compute/virtualMachines"``).
        """
        rg = resource_group or self._client.resource_group
        filter_expr: str | None = None
        if resource_type:
            filter_expr = f"resourceType eq '{resource_type}'"

        if rg:
            items = self._resource_client.resources.list_by_resource_group(
                rg,
                filter=filter_expr,
            )
        else:
            items = self._resource_client.resources.list(filter=filter_expr)

        return list(items)

    # -------------------------------------------------------------- VM actions

    def restart_vm(self, resource_group: str, vm_name: str) -> bool:
        """Restart an Azure Virtual Machine.

        Parameters
        ----------
        resource_group:
            Resource group that owns the VM.
        vm_name:
            Name of the virtual machine.

        Returns
        -------
        bool
            ``True`` on success, ``False`` if the operation failed or was
            skipped because *dry_run* is ``True``.
        """
        logger.info("Restarting VM '%s' in resource group '%s'.", vm_name, resource_group)
        if self._dry_run:
            logger.info("DRY RUN – skipping actual restart of VM '%s'.", vm_name)
            return False

        try:
            poller = self._compute_client.virtual_machines.begin_restart(resource_group, vm_name)
            poller.result()  # block until complete
            logger.info("VM '%s' restarted successfully.", vm_name)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to restart VM '%s': %s", vm_name, exc)
            return False

    # --------------------------------------------------------- VMSS actions

    def scale_vmss(self, resource_group: str, vmss_name: str, capacity: int) -> bool:
        """Set the instance count for a VM Scale Set.

        Parameters
        ----------
        resource_group:
            Resource group that owns the VMSS.
        vmss_name:
            Name of the scale set.
        capacity:
            Desired number of VM instances.

        Returns
        -------
        bool
            ``True`` on success.
        """
        logger.info(
            "Scaling VMSS '%s' (rg=%s) to %d instance(s).",
            vmss_name,
            resource_group,
            capacity,
        )
        if self._dry_run:
            logger.info("DRY RUN – skipping scale of VMSS '%s'.", vmss_name)
            return False

        try:
            vmss = self._compute_client.virtual_machine_scale_sets.get(resource_group, vmss_name)
            if vmss.sku is None:
                logger.error("VMSS '%s' has no SKU; cannot scale.", vmss_name)
                return False
            vmss.sku.capacity = capacity
            poller = self._compute_client.virtual_machine_scale_sets.begin_create_or_update(
                resource_group, vmss_name, vmss
            )
            poller.result()
            logger.info("VMSS '%s' scaled to %d instance(s).", vmss_name, capacity)
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to scale VMSS '%s': %s", vmss_name, exc)
            return False

    # ---------------------------------------------------------------- AKS actions

    def restart_aks_node_pool(
        self, resource_group: str, cluster_name: str, node_pool_name: str
    ) -> bool:
        """Trigger a node image upgrade on an AKS node pool (equivalent to a rolling restart).

        Parameters
        ----------
        resource_group:
            Resource group that contains the AKS cluster.
        cluster_name:
            AKS cluster name.
        node_pool_name:
            Name of the agent/node pool to restart.

        Returns
        -------
        bool
            ``True`` on success.
        """
        logger.info(
            "Restarting AKS node pool '%s' in cluster '%s' (rg=%s).",
            node_pool_name,
            cluster_name,
            resource_group,
        )
        if self._dry_run:
            logger.info("DRY RUN – skipping restart of AKS node pool '%s'.", node_pool_name)
            return False

        try:
            poller = self._aks_client.agent_pools.begin_upgrade_node_image_version(
                resource_group, cluster_name, node_pool_name
            )
            poller.result()
            logger.info(
                "AKS node pool '%s' in cluster '%s' restarted successfully.",
                node_pool_name,
                cluster_name,
            )
            return True
        except Exception as exc:  # noqa: BLE001
            logger.error(
                "Failed to restart AKS node pool '%s' in cluster '%s': %s",
                node_pool_name,
                cluster_name,
                exc,
            )
            return False
