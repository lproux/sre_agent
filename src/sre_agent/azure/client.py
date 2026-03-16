"""Azure authentication client.

Provides a single, lazily-initialised credential object that is shared
across all Azure SDK management clients created by the SRE Agent.
"""

from __future__ import annotations

import logging
from functools import cached_property

from azure.core.credentials import TokenCredential
from azure.identity import (
    ClientSecretCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
)

from sre_agent.config import AgentConfig, AuthMethod

logger = logging.getLogger(__name__)


class AzureClient:
    """Factory that creates and caches the Azure SDK credential object.

    The credential is chosen based on :attr:`AgentConfig.auth_method`:

    * ``default``            – :class:`~azure.identity.DefaultAzureCredential`
      (tries environment variables, managed identity, Azure CLI, etc.)
    * ``managed_identity``   – :class:`~azure.identity.ManagedIdentityCredential`
      (use when running inside Azure – VMs, ACI, AKS, App Service, …)
    * ``service_principal``  – :class:`~azure.identity.ClientSecretCredential`
      (requires ``tenant_id``, ``client_id``, and ``client_secret``
      to be set in :class:`AgentConfig`)
    """

    def __init__(self, config: AgentConfig) -> None:
        self._config = config

    # ---------------------------------------------------------------- credential

    @cached_property
    def credential(self) -> TokenCredential:
        """Return a cached credential object appropriate for the configured auth method."""
        method = self._config.auth_method

        if method == AuthMethod.MANAGED_IDENTITY:
            logger.info("Azure auth: ManagedIdentityCredential")
            return ManagedIdentityCredential(client_id=self._config.client_id)

        if method == AuthMethod.SERVICE_PRINCIPAL:
            self._validate_sp_config()
            logger.info("Azure auth: ClientSecretCredential (service principal)")
            return ClientSecretCredential(
                tenant_id=self._config.tenant_id,  # type: ignore[arg-type]
                client_id=self._config.client_id,  # type: ignore[arg-type]
                client_secret=self._config.client_secret,  # type: ignore[arg-type]
            )

        # Default: let the SDK try all available credential sources in order
        logger.info("Azure auth: DefaultAzureCredential")
        return DefaultAzureCredential()

    # ----------------------------------------------------------------- helpers

    @property
    def subscription_id(self) -> str:
        return self._config.subscription_id

    @property
    def resource_group(self) -> str | None:
        return self._config.resource_group

    def _validate_sp_config(self) -> None:
        missing: list[str] = []
        for field in ("tenant_id", "client_id", "client_secret"):
            if not getattr(self._config, field):
                missing.append(field)
        if missing:
            raise ValueError(
                f"auth_method=service_principal requires the following config "
                f"fields: {', '.join(missing)}"
            )
