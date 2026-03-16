"""Tests for the core SREAgent."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from sre_agent.agent import SREAgent, _parse_resource_id
from sre_agent.azure.alerts import AlertHandler, AlertSeverity, SREAlert
from sre_agent.config import AgentConfig, AuthMethod


def _config(**kwargs) -> AgentConfig:
    defaults = {
        "subscription_id": "sub-test",
        "auth_method": AuthMethod.DEFAULT,
    }
    defaults.update(kwargs)
    return AgentConfig.model_validate(defaults)


# ---------------------------------------------------------------------------
# _parse_resource_id helper
# ---------------------------------------------------------------------------


class TestParseResourceId:
    def test_full_vm_resource_id(self) -> None:
        rid = "/subscriptions/sub/resourceGroups/my-rg/providers/Microsoft.Compute/virtualMachines/my-vm"
        result = _parse_resource_id(rid)
        assert result == ("my-rg", "my-vm")

    def test_malformed_id_returns_none(self) -> None:
        assert _parse_resource_id("/subscriptions/sub") is None
        assert _parse_resource_id("") is None
        assert _parse_resource_id("not/an/azure/id") is None


# ---------------------------------------------------------------------------
# SREAgent
# ---------------------------------------------------------------------------


class TestSREAgent:
    def _make_agent(self, **cfg_kwargs) -> SREAgent:
        config = _config(**cfg_kwargs)
        handler = AlertHandler(max_retries=1, dry_run=config.dry_run)
        agent = SREAgent(config=config, alert_handler=handler)
        # Inject a mock credential so the cached_property never contacts Azure
        agent.azure_client.__dict__["credential"] = MagicMock()
        return agent

    def test_agent_properties(self) -> None:
        agent = self._make_agent()
        assert agent.config.subscription_id == "sub-test"
        assert agent.alert_handler is not None
        assert agent.monitor is not None
        assert agent.resources is not None
        assert agent.is_running is False

    def test_run_once_calls_monitor_and_handler(self) -> None:
        agent = self._make_agent()

        mock_alerts = [
            SREAlert(
                alert_id="a1",
                name="test-alert",
                severity=AlertSeverity.CRITICAL,
                resource_id="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm",
                description="desc",
            )
        ]

        agent.alert_handler.register_fn(AlertSeverity.CRITICAL, lambda a: True)

        with patch.object(agent.monitor, "list_active_alerts", return_value=mock_alerts):
            summary = agent.run_once()

        assert summary["total"] == 1
        assert summary["resolved"] == 1
        assert summary["escalated"] == 0

    def test_run_once_empty_alerts(self) -> None:
        agent = self._make_agent()
        with patch.object(agent.monitor, "list_active_alerts", return_value=[]):
            summary = agent.run_once()
        assert summary["total"] == 0

    def test_dry_run_passed_to_resources(self) -> None:
        agent = self._make_agent(dry_run=True)
        assert agent.resources._dry_run is True
        assert agent.alert_handler.dry_run is True

    def test_register_default_remediations_populates_handlers(self) -> None:
        agent = self._make_agent()
        agent.register_default_remediations()
        assert AlertSeverity.CRITICAL in agent.alert_handler.registered_severities
        assert AlertSeverity.ERROR in agent.alert_handler.registered_severities
        assert AlertSeverity.WARNING in agent.alert_handler.registered_severities

    def test_stop_sets_running_false(self) -> None:
        agent = self._make_agent()
        agent._running = True
        agent.stop()
        assert agent.is_running is False
