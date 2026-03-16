"""Tests for AzureClient authentication setup."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from sre_agent.azure.client import AzureClient
from sre_agent.config import AgentConfig, AuthMethod


def _config(**kwargs) -> AgentConfig:
    defaults = {"subscription_id": "sub-test", "auth_method": AuthMethod.DEFAULT}
    defaults.update(kwargs)
    return AgentConfig.model_validate(defaults)


class TestAzureClientCredential:
    def test_default_credential(self) -> None:
        client = AzureClient(_config(auth_method=AuthMethod.DEFAULT))
        with patch("sre_agent.azure.client.DefaultAzureCredential") as mock_cls:
            mock_cls.return_value = MagicMock()
            cred = client.credential
            mock_cls.assert_called_once()
            assert cred is mock_cls.return_value

    def test_managed_identity_credential(self) -> None:
        client = AzureClient(_config(auth_method=AuthMethod.MANAGED_IDENTITY))
        with patch("sre_agent.azure.client.ManagedIdentityCredential") as mock_cls:
            mock_cls.return_value = MagicMock()
            cred = client.credential
            mock_cls.assert_called_once_with(client_id=None)
            assert cred is mock_cls.return_value

    def test_service_principal_credential(self) -> None:
        cfg = _config(
            auth_method=AuthMethod.SERVICE_PRINCIPAL,
            tenant_id="t1",
            client_id="c1",
            client_secret="s1",
        )
        client = AzureClient(cfg)
        with patch("sre_agent.azure.client.ClientSecretCredential") as mock_cls:
            mock_cls.return_value = MagicMock()
            cred = client.credential
            mock_cls.assert_called_once_with(tenant_id="t1", client_id="c1", client_secret="s1")
            assert cred is mock_cls.return_value

    def test_service_principal_missing_fields_raises(self) -> None:
        cfg = _config(auth_method=AuthMethod.SERVICE_PRINCIPAL)  # no tenant/client/secret
        client = AzureClient(cfg)
        with pytest.raises(ValueError, match="tenant_id"):
            _ = client.credential

    def test_credential_is_cached(self) -> None:
        client = AzureClient(_config())
        with patch("sre_agent.azure.client.DefaultAzureCredential") as mock_cls:
            mock_cls.return_value = MagicMock()
            first = client.credential
            second = client.credential
            assert first is second
            mock_cls.assert_called_once()  # Only instantiated once

    def test_subscription_id_property(self) -> None:
        client = AzureClient(_config(subscription_id="my-sub"))
        assert client.subscription_id == "my-sub"

    def test_resource_group_property(self) -> None:
        client = AzureClient(_config(resource_group="my-rg"))
        assert client.resource_group == "my-rg"

    def test_resource_group_none_by_default(self) -> None:
        client = AzureClient(_config())
        assert client.resource_group is None
