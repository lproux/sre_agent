"""Azure sub-package for SRE Agent.

Exposes the public API of the Azure integration layer.
"""

from sre_agent.azure.alerts import AlertHandler, AlertSeverity, SREAlert
from sre_agent.azure.client import AzureClient
from sre_agent.azure.monitor import AzureMonitor
from sre_agent.azure.resources import AzureResourceManager

__all__ = [
    "AzureClient",
    "AzureMonitor",
    "AzureResourceManager",
    "AlertHandler",
    "AlertSeverity",
    "SREAlert",
]
