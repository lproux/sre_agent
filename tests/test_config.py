"""Tests for AgentConfig."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from sre_agent.config import AgentConfig, AuthMethod, LogLevel


@pytest.fixture
def minimal_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set the minimum required environment variables for AgentConfig."""
    monkeypatch.setenv("SRE_AGENT_SUBSCRIPTION_ID", "sub-1234")
    # Clear any accidental leftover from earlier tests
    for key in ("SRE_AGENT_TENANT_ID", "SRE_AGENT_CLIENT_ID", "SRE_AGENT_CLIENT_SECRET"):
        monkeypatch.delenv(key, raising=False)


class TestAgentConfigDefaults:
    def test_loads_with_minimal_env(self, minimal_env: None) -> None:
        cfg = AgentConfig()
        assert cfg.subscription_id == "sub-1234"
        assert cfg.auth_method == AuthMethod.DEFAULT
        assert cfg.poll_interval_seconds == 60
        assert cfg.max_remediation_retries == 3
        assert cfg.dry_run is False
        assert cfg.log_level == LogLevel.INFO
        assert cfg.log_json is False
        assert cfg.resource_group is None

    def test_subscription_id_required(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("SRE_AGENT_SUBSCRIPTION_ID", raising=False)
        with pytest.raises(ValidationError, match="subscription_id"):
            AgentConfig()

    def test_poll_interval_minimum(self, minimal_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SRE_AGENT_POLL_INTERVAL_SECONDS", "5")
        with pytest.raises(ValidationError):
            AgentConfig()

    def test_dry_run_flag(self, minimal_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SRE_AGENT_DRY_RUN", "true")
        cfg = AgentConfig()
        assert cfg.dry_run is True

    def test_log_level_override(self, minimal_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SRE_AGENT_LOG_LEVEL", "DEBUG")
        cfg = AgentConfig()
        assert cfg.log_level == LogLevel.DEBUG

    def test_auth_method_service_principal(
        self, minimal_env: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SRE_AGENT_AUTH_METHOD", "service_principal")
        monkeypatch.setenv("SRE_AGENT_TENANT_ID", "tenant-abc")
        monkeypatch.setenv("SRE_AGENT_CLIENT_ID", "client-abc")
        monkeypatch.setenv("SRE_AGENT_CLIENT_SECRET", "secret-xyz")
        cfg = AgentConfig()
        assert cfg.auth_method == AuthMethod.SERVICE_PRINCIPAL
        assert cfg.tenant_id == "tenant-abc"
        assert cfg.client_id == "client-abc"
        assert cfg.client_secret == "secret-xyz"

    def test_resource_group_optional(
        self, minimal_env: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("SRE_AGENT_RESOURCE_GROUP", "my-rg")
        cfg = AgentConfig()
        assert cfg.resource_group == "my-rg"
