"""Configuration management for the SRE Agent.

Settings are loaded from environment variables (with an optional `.env` file).
All Azure credentials are sourced from the environment; they are never stored in
code or configuration files.
"""

from __future__ import annotations

from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuthMethod(str, Enum):
    """Supported Azure authentication strategies."""

    SERVICE_PRINCIPAL = "service_principal"
    MANAGED_IDENTITY = "managed_identity"
    DEFAULT = "default"  # Uses DefaultAzureCredential (tries all methods in order)


class AgentConfig(BaseSettings):
    """All configurable parameters for the SRE Agent.

    Environment variable names are the field names uppercased and prefixed
    with ``SRE_AGENT_``.  For example, ``subscription_id`` maps to the
    environment variable ``SRE_AGENT_SUBSCRIPTION_ID``.
    """

    model_config = SettingsConfigDict(
        env_prefix="SRE_AGENT_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ------------------------------------------------------------------ Azure
    subscription_id: str = Field(
        ...,
        description="Azure subscription ID where monitored resources live.",
    )
    resource_group: str | None = Field(
        default=None,
        description="Limit monitoring to this resource group (None = all groups).",
    )
    auth_method: AuthMethod = Field(
        default=AuthMethod.DEFAULT,
        description="Azure authentication method.",
    )

    # Service-principal credentials (required only when auth_method=service_principal)
    tenant_id: str | None = Field(default=None, description="Azure AD tenant ID.")
    client_id: str | None = Field(default=None, description="Service principal client ID.")
    client_secret: str | None = Field(default=None, description="Service principal client secret.")

    # ---------------------------------------------------------- Agent behaviour
    poll_interval_seconds: int = Field(
        default=60,
        ge=10,
        description="How often the agent polls Azure Monitor for new alerts.",
    )
    max_remediation_retries: int = Field(
        default=3,
        ge=1,
        description="Maximum remediation attempts before escalating an alert.",
    )
    dry_run: bool = Field(
        default=False,
        description="When True, remediation actions are logged but not executed.",
    )

    # ----------------------------------------------------------------- Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log verbosity level.")
    log_json: bool = Field(
        default=False,
        description="Emit structured JSON logs (recommended for production).",
    )
