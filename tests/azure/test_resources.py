"""Tests for AzureResourceManager."""

from __future__ import annotations

from unittest.mock import MagicMock

from sre_agent.azure.client import AzureClient
from sre_agent.azure.resources import AzureResourceManager
from sre_agent.config import AgentConfig, AuthMethod


def _make_client(resource_group: str = "rg-test") -> AzureClient:
    cfg = AgentConfig.model_validate(
        {
            "subscription_id": "sub-test",
            "auth_method": AuthMethod.DEFAULT,
            "resource_group": resource_group,
        }
    )
    client = AzureClient(cfg)
    client.__dict__["credential"] = MagicMock()
    return client


class TestRestartVM:
    def test_restart_vm_calls_sdk(self) -> None:
        client = _make_client()
        manager = AzureResourceManager(client, dry_run=False)

        mock_poller = MagicMock()
        mock_compute = MagicMock()
        mock_compute.virtual_machines.begin_restart.return_value = mock_poller
        manager._compute = mock_compute

        result = manager.restart_vm("my-rg", "my-vm")

        mock_compute.virtual_machines.begin_restart.assert_called_once_with("my-rg", "my-vm")
        mock_poller.result.assert_called_once()
        assert result is True

    def test_restart_vm_dry_run_skips_sdk(self) -> None:
        client = _make_client()
        manager = AzureResourceManager(client, dry_run=True)

        mock_compute = MagicMock()
        manager._compute = mock_compute

        result = manager.restart_vm("my-rg", "my-vm")

        mock_compute.virtual_machines.begin_restart.assert_not_called()
        assert result is False

    def test_restart_vm_returns_false_on_exception(self) -> None:
        client = _make_client()
        manager = AzureResourceManager(client, dry_run=False)

        mock_compute = MagicMock()
        mock_compute.virtual_machines.begin_restart.side_effect = Exception("network error")
        manager._compute = mock_compute

        result = manager.restart_vm("my-rg", "my-vm")

        assert result is False


class TestScaleVMSS:
    def test_scale_vmss_calls_sdk(self) -> None:
        client = _make_client()
        manager = AzureResourceManager(client, dry_run=False)

        mock_vmss = MagicMock()
        mock_vmss.sku = MagicMock()
        mock_vmss.sku.capacity = 1
        mock_poller = MagicMock()
        mock_compute = MagicMock()
        mock_compute.virtual_machine_scale_sets.get.return_value = mock_vmss
        mock_compute.virtual_machine_scale_sets.begin_create_or_update.return_value = mock_poller
        manager._compute = mock_compute

        result = manager.scale_vmss("my-rg", "my-vmss", capacity=5)

        assert mock_vmss.sku.capacity == 5
        mock_poller.result.assert_called_once()
        assert result is True

    def test_scale_vmss_dry_run(self) -> None:
        client = _make_client()
        manager = AzureResourceManager(client, dry_run=True)

        mock_compute = MagicMock()
        manager._compute = mock_compute

        result = manager.scale_vmss("my-rg", "my-vmss", capacity=3)

        mock_compute.virtual_machine_scale_sets.get.assert_not_called()
        assert result is False

    def test_scale_vmss_no_sku_returns_false(self) -> None:
        client = _make_client()
        manager = AzureResourceManager(client, dry_run=False)

        mock_vmss = MagicMock()
        mock_vmss.sku = None
        mock_compute = MagicMock()
        mock_compute.virtual_machine_scale_sets.get.return_value = mock_vmss
        manager._compute = mock_compute

        result = manager.scale_vmss("my-rg", "my-vmss", capacity=3)

        assert result is False


class TestListResources:
    def test_list_by_resource_group(self) -> None:
        client = _make_client(resource_group="rg-test")
        manager = AzureResourceManager(client)

        mock_resource_client = MagicMock()
        mock_resource_client.resources.list_by_resource_group.return_value = iter([MagicMock(), MagicMock()])
        manager._resource = mock_resource_client

        resources = manager.list_resources(resource_group="rg-test")

        mock_resource_client.resources.list_by_resource_group.assert_called_once_with(
            "rg-test", filter=None
        )
        assert len(resources) == 2

    def test_list_with_resource_type_filter(self) -> None:
        client = _make_client()
        manager = AzureResourceManager(client)

        mock_resource_client = MagicMock()
        mock_resource_client.resources.list_by_resource_group.return_value = iter([])
        manager._resource = mock_resource_client

        manager.list_resources(resource_group="rg", resource_type="Microsoft.Compute/virtualMachines")

        mock_resource_client.resources.list_by_resource_group.assert_called_once_with(
            "rg", filter="resourceType eq 'Microsoft.Compute/virtualMachines'"
        )
