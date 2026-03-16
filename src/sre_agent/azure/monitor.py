"""Azure Monitor integration.

Wraps the ``azure-mgmt-monitor`` SDK to expose the subset of functionality
that the SRE Agent needs:

* Retrieve fired alert instances (``AlertsManagementClient``)
* Query metric values for a given resource
* List and acknowledge active alerts
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any

from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.monitor.models import MetricValue

from sre_agent.azure.alerts import AlertSeverity, SREAlert
from sre_agent.azure.client import AzureClient

logger = logging.getLogger(__name__)


class AzureMonitor:
    """High-level interface to Azure Monitor for SRE operations.

    Parameters
    ----------
    client:
        Authenticated :class:`AzureClient` instance.
    """

    def __init__(self, client: AzureClient) -> None:
        self._client = client
        self._mgmt: MonitorManagementClient | None = None

    # ----------------------------------------------------------------- SDK client

    @property
    def _monitor(self) -> MonitorManagementClient:
        """Lazily initialised Azure Monitor management client."""
        if self._mgmt is None:
            self._mgmt = MonitorManagementClient(
                credential=self._client.credential,  # type: ignore[arg-type]
                subscription_id=self._client.subscription_id,
            )
        return self._mgmt

    # ------------------------------------------------------------------ alerts

    def list_active_alerts(
        self,
        resource_group: str | None = None,
        severity: AlertSeverity | None = None,
    ) -> list[SREAlert]:
        """Return all currently *Fired* Azure Monitor alerts.

        Parameters
        ----------
        resource_group:
            If provided, only alerts in this resource group are returned.
            Falls back to :attr:`AzureClient.resource_group` if ``None``.
        severity:
            Optional filter; ``None`` returns all severities.
        """
        rg = resource_group or self._client.resource_group
        raw_alerts = self._fetch_raw_alerts(resource_group=rg)

        alerts: list[SREAlert] = []
        for raw in raw_alerts:
            alert = self._parse_alert(raw)
            if alert is None:
                continue
            if severity is not None and alert.severity != severity:
                continue
            alerts.append(alert)

        logger.info("Found %d active alert(s).", len(alerts))
        return alerts

    # ----------------------------------------------------------------- metrics

    def get_metric(
        self,
        resource_id: str,
        metric_name: str,
        aggregation: str = "Average",
        timespan: str = "PT1H",
    ) -> list[MetricValue]:
        """Query a single metric for an Azure resource.

        Parameters
        ----------
        resource_id:
            Full Azure resource ID string.
        metric_name:
            Name of the metric to retrieve (e.g. ``"Percentage CPU"``).
        aggregation:
            Aggregation type: ``"Average"``, ``"Total"``, ``"Minimum"``,
            ``"Maximum"``, or ``"Count"``.
        timespan:
            ISO 8601 duration string (default ``"PT1H"`` = last hour).

        Returns
        -------
        list[MetricValue]
            Ordered list of :class:`~azure.mgmt.monitor.models.MetricValue`
            data-points for the requested metric and time range.
        """
        response = self._monitor.metrics.list(
            resource_uri=resource_id,
            metricnames=metric_name,
            aggregation=aggregation,
            timespan=timespan,
        )
        values: list[MetricValue] = []
        for metric in response.value or []:
            for ts in metric.timeseries or []:
                values.extend(ts.data or [])
        return values

    # ----------------------------------------------------------------- internals

    def _fetch_raw_alerts(self, resource_group: str | None) -> Iterator[Any]:
        """Yield raw alert objects from the Azure Monitor Alerts API.

        Uses the ``AlertsManagementClient`` when available, otherwise falls
        back to the activity log.
        """
        # The alerts management plane is a separate extension client.
        # We use the monitor client's activity log as a universal fallback.
        try:
            from azure.mgmt.alertsmanagement import AlertsManagementClient  # type: ignore[import]

            alerts_client = AlertsManagementClient(
                credential=self._client.credential,  # type: ignore[arg-type]
                subscription_id=self._client.subscription_id,
            )
            filter_kwargs: dict[str, Any] = {"alert_state": "Fired"}
            if resource_group:
                filter_kwargs["resource_group_name"] = resource_group
            yield from alerts_client.alerts.get_all(**filter_kwargs)
        except ImportError:
            logger.warning(
                "azure-mgmt-alertsmanagement is not installed; "
                "falling back to activity log. Install the package for full alert support."
            )
            yield from self._fetch_activity_log_alerts(resource_group=resource_group)

    def _fetch_activity_log_alerts(self, resource_group: str | None) -> Iterator[Any]:
        """Yield alert-like objects from the Azure Activity Log (fallback)."""
        now = datetime.now(tz=timezone.utc)
        filter_str = f"eventTimestamp ge '{now.strftime('%Y-%m-%dT%H:%M:%SZ')}'"
        if resource_group:
            filter_str += f" and resourceGroupName eq '{resource_group}'"
        yield from self._monitor.activity_logs.list(filter=filter_str)

    @staticmethod
    def _parse_alert(raw: Any) -> SREAlert | None:
        """Convert a raw SDK alert object into a normalised :class:`SREAlert`."""
        if raw is None:
            return None
        try:
            alert_id: str = getattr(raw, "id", "") or ""
            name: str = getattr(raw, "name", "") or ""

            # Try to extract severity from the essentials (AlertsManagement format)
            essentials = getattr(raw, "essentials", None)
            if essentials:
                sev_str: str = str(getattr(essentials, "severity", "Sev3") or "Sev3")
                resource_id: str = str(getattr(essentials, "target_resource", "") or "")
                description: str = str(getattr(essentials, "description", "") or "")
                fired_at: datetime | None = getattr(essentials, "start_date_time", None)
            else:
                # Activity-log fallback: properties differ
                sev_str = "Sev3"
                resource_id = str(getattr(raw, "resource_id", "") or "")
                description = str(getattr(raw, "description", "") or "")
                fired_at = getattr(raw, "event_timestamp", None)

            severity = AlertSeverity.from_azure_string(sev_str)
            return SREAlert(
                alert_id=alert_id,
                name=name,
                severity=severity,
                resource_id=resource_id,
                description=description,
                fired_at=fired_at or datetime.now(tz=timezone.utc),
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to parse alert object: %s", exc)
            return None
