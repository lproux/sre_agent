"""Tests for AzureMonitor."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import MagicMock, patch

from sre_agent.azure.alerts import AlertSeverity
from sre_agent.azure.client import AzureClient
from sre_agent.azure.monitor import AzureMonitor
from sre_agent.config import AgentConfig, AuthMethod


def _make_client() -> AzureClient:
    cfg = AgentConfig.model_validate(
        {
            "subscription_id": "sub-test",
            "auth_method": AuthMethod.DEFAULT,
        }
    )
    client = AzureClient(cfg)
    # Stub the credential so no real Azure call is made
    client.__dict__["credential"] = MagicMock()
    return client


class TestAzureMonitorParseAlert:
    """Unit-test the static _parse_alert method without Azure calls."""

    def _raw_with_essentials(
        self,
        severity: str = "Sev1",
        description: str = "disk full",
        resource_id: str = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1",
        name: str = "disk-alert",
        alert_id: str = "/subscriptions/sub/providers/microsoft.alertsManagement/alerts/123",
    ) -> Any:
        essentials = MagicMock()
        essentials.severity = severity
        essentials.target_resource = resource_id
        essentials.description = description
        essentials.start_date_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        raw = MagicMock()
        raw.id = alert_id
        raw.name = name
        raw.essentials = essentials
        return raw

    def test_parse_valid_alert(self) -> None:
        raw = self._raw_with_essentials(severity="Sev0")
        alert = AzureMonitor._parse_alert(raw)
        assert alert is not None
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.name == "disk-alert"

    def test_parse_alert_returns_none_on_error(self) -> None:
        # Pass a completely broken object
        alert = AzureMonitor._parse_alert(None)
        assert alert is None

    def test_parse_alert_unknown_severity(self) -> None:
        raw = self._raw_with_essentials(severity="SevX")
        alert = AzureMonitor._parse_alert(raw)
        assert alert is not None
        assert alert.severity == AlertSeverity.INFORMATIONAL

    def test_parse_alert_no_essentials(self) -> None:
        """Fallback path: raw object has no 'essentials' attribute."""
        # Test the non-essentials path with essentials=None
        raw2 = MagicMock()
        raw2.essentials = None
        alert = AzureMonitor._parse_alert(raw2)
        # Should succeed with defaults
        assert alert is not None


class TestAzureMonitorListAlerts:
    def test_list_active_alerts_filters_by_severity(self) -> None:
        client = _make_client()
        monitor = AzureMonitor(client)

        # Inject mock alerts directly via _fetch_raw_alerts
        sev0_raw = MagicMock()
        sev0_raw.id = "alert-1"
        sev0_raw.name = "critical-alert"
        sev0_ess = MagicMock()
        sev0_ess.severity = "Sev0"
        sev0_ess.target_resource = (
            "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm1"
        )
        sev0_ess.description = "cpu spike"
        sev0_ess.start_date_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        sev0_raw.essentials = sev0_ess

        sev3_raw = MagicMock()
        sev3_raw.id = "alert-2"
        sev3_raw.name = "info-alert"
        sev3_ess = MagicMock()
        sev3_ess.severity = "Sev3"
        sev3_ess.target_resource = (
            "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm2"
        )
        sev3_ess.description = "info event"
        sev3_ess.start_date_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
        sev3_raw.essentials = sev3_ess

        with patch.object(monitor, "_fetch_raw_alerts", return_value=iter([sev0_raw, sev3_raw])):
            alerts = monitor.list_active_alerts(severity=AlertSeverity.CRITICAL)

        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL

    def test_list_active_alerts_no_filter_returns_all(self) -> None:
        client = _make_client()
        monitor = AzureMonitor(client)

        raw_alerts = []
        for i, sev in enumerate(["Sev0", "Sev1", "Sev2"]):
            raw = MagicMock()
            raw.id = f"alert-{i}"
            raw.name = f"alert-{sev}"
            ess = MagicMock()
            ess.severity = sev
            ess.target_resource = (
                f"/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm{i}"
            )
            ess.description = "desc"
            ess.start_date_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
            raw.essentials = ess
            raw_alerts.append(raw)

        with patch.object(monitor, "_fetch_raw_alerts", return_value=iter(raw_alerts)):
            alerts = monitor.list_active_alerts()

        assert len(alerts) == 3
