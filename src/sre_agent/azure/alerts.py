"""Alert data-models and the SRE alert-handling pipeline.

The alert pipeline works as follows:

1. :class:`AzureMonitor` fetches raw alerts and normalises them into
   :class:`SREAlert` objects.
2. :class:`AlertHandler` receives a list of :class:`SREAlert` objects, applies
   severity-based routing, and delegates to registered remediation callables.
3. If no remediation is registered (or it fails), the alert is marked
   *escalated* so an on-call engineer can be paged.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Normalised alert severity levels (aligned with Azure Monitor Sev0-Sev4)."""

    CRITICAL = "Sev0"
    ERROR = "Sev1"
    WARNING = "Sev2"
    INFORMATIONAL = "Sev3"
    VERBOSE = "Sev4"

    @classmethod
    def from_azure_string(cls, value: str) -> AlertSeverity:
        """Parse an Azure severity string such as ``'Sev0'`` or ``'0'``."""
        normalised = value.strip()
        if normalised.isdigit():
            normalised = f"Sev{normalised}"
        try:
            return cls(normalised)
        except ValueError:
            logger.warning("Unknown severity '%s'; defaulting to INFORMATIONAL.", value)
            return cls.INFORMATIONAL

    @property
    def is_actionable(self) -> bool:
        """Return ``True`` for severities that warrant automated remediation."""
        return self in (AlertSeverity.CRITICAL, AlertSeverity.ERROR, AlertSeverity.WARNING)


@dataclass
class SREAlert:
    """Normalised representation of an Azure Monitor alert."""

    alert_id: str
    name: str
    severity: AlertSeverity
    resource_id: str
    description: str
    fired_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    resolved: bool = False
    remediation_attempts: int = 0
    escalated: bool = False

    def __str__(self) -> str:
        status = "ESCALATED" if self.escalated else ("RESOLVED" if self.resolved else "ACTIVE")
        return (
            f"[{self.severity.value}] {self.name} | {status} "
            f"| resource={self.resource_id!r}"
        )


# Type alias for a remediation callable: receives the alert, returns True on success.
RemediationFn = Callable[[SREAlert], bool]


class AlertHandler:
    """Routes alerts to registered remediation functions and tracks outcomes.

    Usage::

        handler = AlertHandler(max_retries=3, dry_run=False)

        @handler.register(AlertSeverity.CRITICAL)
        def restart_vm(alert: SREAlert) -> bool:
            ...  # perform restart, return True on success

        results = handler.process(alerts)

    Parameters
    ----------
    max_retries:
        Number of remediation attempts before marking an alert as escalated.
    dry_run:
        When ``True``, remediation callables are *not* invoked; alerts are
        logged and marked as if they were successfully remediated.
    """

    def __init__(self, max_retries: int = 3, dry_run: bool = False) -> None:
        self._max_retries = max_retries
        self._dry_run = dry_run
        self._handlers: dict[AlertSeverity, list[RemediationFn]] = {sev: [] for sev in AlertSeverity}

    # -------------------------------------------------------------- registration

    def register(self, severity: AlertSeverity) -> Callable[[RemediationFn], RemediationFn]:
        """Decorator that registers a remediation function for a given severity.

        Multiple functions can be registered for the same severity; they are
        tried in registration order until one returns ``True``.
        """

        def decorator(fn: RemediationFn) -> RemediationFn:
            self._handlers[severity].append(fn)
            logger.debug("Registered remediation '%s' for severity %s.", fn.__name__, severity)
            return fn

        return decorator

    def register_fn(self, severity: AlertSeverity, fn: RemediationFn) -> None:
        """Register a remediation function programmatically (non-decorator form)."""
        self._handlers[severity].append(fn)

    # ---------------------------------------------------------------- processing

    def process(self, alerts: list[SREAlert]) -> list[SREAlert]:
        """Process a list of alerts through the remediation pipeline.

        Parameters
        ----------
        alerts:
            List of :class:`SREAlert` objects to process.

        Returns
        -------
        list[SREAlert]
            The same list, mutated in-place with updated state
            (``resolved``, ``escalated``, ``remediation_attempts``).
        """
        for alert in alerts:
            if alert.resolved or alert.escalated:
                continue
            if not alert.severity.is_actionable:
                logger.info("Skipping non-actionable alert: %s", alert)
                continue
            self._handle_alert(alert)
        return alerts

    # ----------------------------------------------------------------- internals

    def _handle_alert(self, alert: SREAlert) -> None:
        handlers = self._handlers.get(alert.severity, [])

        if self._dry_run:
            logger.info("DRY RUN – would remediate: %s", alert)
            alert.resolved = True
            return

        if not handlers:
            logger.warning("No handler registered for %s; escalating: %s", alert.severity, alert)
            alert.escalated = True
            return

        for fn in handlers:
            if alert.remediation_attempts >= self._max_retries:
                logger.error(
                    "Max retries (%d) reached for alert %s; escalating.",
                    self._max_retries,
                    alert.name,
                )
                alert.escalated = True
                return

            alert.remediation_attempts += 1
            logger.info(
                "Attempting remediation '%s' for alert '%s' (attempt %d/%d).",
                fn.__name__,
                alert.name,
                alert.remediation_attempts,
                self._max_retries,
            )
            try:
                success = fn(alert)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Remediation '%s' raised an exception: %s", fn.__name__, exc)
                success = False

            if success:
                logger.info("Alert '%s' resolved by '%s'.", alert.name, fn.__name__)
                alert.resolved = True
                return

        # All handlers failed
        logger.error("All remediations failed for alert '%s'; escalating.", alert.name)
        alert.escalated = True

    # ------------------------------------------------------------------- stats

    def summary(self, alerts: list[SREAlert]) -> dict[str, int]:
        """Return a simple count-based summary for a processed alert list."""
        return {
            "total": len(alerts),
            "resolved": sum(1 for a in alerts if a.resolved),
            "escalated": sum(1 for a in alerts if a.escalated),
            "pending": sum(1 for a in alerts if not a.resolved and not a.escalated),
        }

    @property
    def dry_run(self) -> bool:
        return self._dry_run

    @property
    def max_retries(self) -> int:
        return self._max_retries

    @property
    def registered_severities(self) -> list[AlertSeverity]:
        """Return the severities that have at least one handler registered."""
        return [sev for sev, fns in self._handlers.items() if fns]

    def get_handlers(self, severity: AlertSeverity) -> list[RemediationFn]:
        """Return the list of handlers registered for *severity*."""
        return list(self._handlers.get(severity, []))
