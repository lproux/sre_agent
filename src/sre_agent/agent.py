"""Core SRE Agent.

The agent runs a continuous poll-and-remediate loop:

1. Authenticate with Azure using the configured credential strategy.
2. Fetch active alerts from Azure Monitor.
3. Pass alerts through the :class:`AlertHandler` pipeline.
4. Log a summary of outcomes.

The loop continues until stopped or a fatal error occurs.
"""

from __future__ import annotations

import logging
import time

from sre_agent.azure.alerts import AlertHandler, AlertSeverity, SREAlert
from sre_agent.azure.client import AzureClient
from sre_agent.azure.monitor import AzureMonitor
from sre_agent.azure.resources import AzureResourceManager
from sre_agent.config import AgentConfig

logger = logging.getLogger(__name__)


class SREAgent:
    """Main SRE Agent that ties together configuration, Azure clients, and alert handling.

    Parameters
    ----------
    config:
        Agent configuration object.  Defaults to loading settings from the
        environment (see :class:`~sre_agent.config.AgentConfig`).
    alert_handler:
        Optional pre-configured :class:`AlertHandler`.  When ``None`` a new
        handler is created using the settings in *config*.
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        alert_handler: AlertHandler | None = None,
    ) -> None:
        self._config = config or AgentConfig()  # type: ignore[call-arg]
        self._azure_client = AzureClient(self._config)
        self._monitor = AzureMonitor(self._azure_client)
        self._resources = AzureResourceManager(
            self._azure_client,
            dry_run=self._config.dry_run,
        )
        self._handler = alert_handler or AlertHandler(
            max_retries=self._config.max_remediation_retries,
            dry_run=self._config.dry_run,
        )

        self._running = False

    # ----------------------------------------------------------------- properties

    @property
    def config(self) -> AgentConfig:
        return self._config

    @property
    def azure_client(self) -> AzureClient:
        return self._azure_client

    @property
    def monitor(self) -> AzureMonitor:
        return self._monitor

    @property
    def resources(self) -> AzureResourceManager:
        return self._resources

    @property
    def alert_handler(self) -> AlertHandler:
        return self._handler

    @property
    def is_running(self) -> bool:
        return self._running

    # ------------------------------------------------------------------- loop

    def run_once(self) -> dict[str, int]:
        """Execute a single poll-and-remediate cycle.

        Returns
        -------
        dict[str, int]
            Summary statistics with keys ``total``, ``resolved``,
            ``escalated``, and ``pending``.
        """
        logger.info("SRE Agent: starting poll cycle.")
        alerts = self._monitor.list_active_alerts()
        processed = self._handler.process(alerts)
        summary = self._handler.summary(processed)
        logger.info("Cycle complete: %s", summary)
        return summary

    def run(self) -> None:
        """Start the continuous polling loop.

        The loop runs until :meth:`stop` is called from another thread or an
        unhandled exception propagates.  Inter-cycle sleep duration is
        controlled by :attr:`AgentConfig.poll_interval_seconds`.
        """
        self._running = True
        logger.info(
            "SRE Agent started (subscription=%s, poll_interval=%ds, dry_run=%s).",
            self._config.subscription_id,
            self._config.poll_interval_seconds,
            self._config.dry_run,
        )
        try:
            while self._running:
                try:
                    self.run_once()
                except Exception as exc:  # noqa: BLE001
                    logger.error("Error during poll cycle: %s", exc, exc_info=True)
                time.sleep(self._config.poll_interval_seconds)
        finally:
            self._running = False
            logger.info("SRE Agent stopped.")

    def stop(self) -> None:
        """Signal the polling loop to stop after the current cycle finishes."""
        logger.info("SRE Agent: stop requested.")
        self._running = False

    # ------------------------------------------------------------ default remediations

    def register_default_remediations(self) -> None:
        """Register sensible default remediation handlers.

        The defaults implement a simple restart strategy:
        - Sev0 / Sev1: attempt to restart the VM identified in the alert's resource ID.
        - Sev2: log a warning (no automated action taken; suitable for human review).

        Override or supplement these by calling
        :meth:`AlertHandler.register_fn` directly on :attr:`alert_handler`.
        """

        def _restart_vm_from_alert(alert: SREAlert) -> bool:
            parts = _parse_resource_id(alert.resource_id)
            if parts is None:
                logger.warning("Cannot parse resource ID '%s'; skipping restart.", alert.resource_id)
                return False
            rg, name = parts
            return self._resources.restart_vm(resource_group=rg, vm_name=name)

        def _warn_on_sev2(alert: SREAlert) -> bool:
            logger.warning(
                "Sev2 alert '%s' requires human review: %s",
                alert.name,
                alert.description,
            )
            return True  # Mark as handled so it doesn't escalate

        self._handler.register_fn(AlertSeverity.CRITICAL, _restart_vm_from_alert)
        self._handler.register_fn(AlertSeverity.ERROR, _restart_vm_from_alert)
        self._handler.register_fn(AlertSeverity.WARNING, _warn_on_sev2)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_resource_id(resource_id: str) -> tuple[str, str] | None:
    """Parse an Azure resource ID and return ``(resource_group, resource_name)``.

    Returns ``None`` if the ID cannot be parsed.

    Example resource ID::

        /subscriptions/00000000-0000-0000-0000-000000000000
        /resourceGroups/my-rg/providers/Microsoft.Compute/virtualMachines/my-vm
    """
    parts = resource_id.strip("/").split("/")
    try:
        rg_idx = [p.lower() for p in parts].index("resourcegroups")
        resource_group = parts[rg_idx + 1]
        name = parts[-1]
        return resource_group, name
    except (ValueError, IndexError):
        return None
