"""Tests for SREAlert, AlertSeverity, and AlertHandler."""

from __future__ import annotations

from datetime import datetime, timezone

from sre_agent.azure.alerts import AlertHandler, AlertSeverity, SREAlert

# ---------------------------------------------------------------------------
# AlertSeverity
# ---------------------------------------------------------------------------


class TestAlertSeverity:
    def test_from_sev_string(self) -> None:
        assert AlertSeverity.from_azure_string("Sev0") == AlertSeverity.CRITICAL
        assert AlertSeverity.from_azure_string("Sev1") == AlertSeverity.ERROR
        assert AlertSeverity.from_azure_string("Sev2") == AlertSeverity.WARNING
        assert AlertSeverity.from_azure_string("Sev3") == AlertSeverity.INFORMATIONAL
        assert AlertSeverity.from_azure_string("Sev4") == AlertSeverity.VERBOSE

    def test_from_numeric_string(self) -> None:
        assert AlertSeverity.from_azure_string("0") == AlertSeverity.CRITICAL
        assert AlertSeverity.from_azure_string("2") == AlertSeverity.WARNING

    def test_unknown_severity_defaults_to_informational(self) -> None:
        sev = AlertSeverity.from_azure_string("UnknownValue")
        assert sev == AlertSeverity.INFORMATIONAL

    def test_is_actionable(self) -> None:
        assert AlertSeverity.CRITICAL.is_actionable is True
        assert AlertSeverity.ERROR.is_actionable is True
        assert AlertSeverity.WARNING.is_actionable is True
        assert AlertSeverity.INFORMATIONAL.is_actionable is False
        assert AlertSeverity.VERBOSE.is_actionable is False


# ---------------------------------------------------------------------------
# SREAlert
# ---------------------------------------------------------------------------


def make_alert(
    severity: AlertSeverity = AlertSeverity.CRITICAL,
    name: str = "test-alert",
    resource_id: str = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Compute/virtualMachines/vm",
) -> SREAlert:
    return SREAlert(
        alert_id="alert-001",
        name=name,
        severity=severity,
        resource_id=resource_id,
        description="test description",
        fired_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


class TestSREAlert:
    def test_default_state(self) -> None:
        alert = make_alert()
        assert alert.resolved is False
        assert alert.escalated is False
        assert alert.remediation_attempts == 0

    def test_str_representation(self) -> None:
        alert = make_alert(severity=AlertSeverity.CRITICAL)
        text = str(alert)
        assert "Sev0" in text
        assert "ACTIVE" in text

    def test_str_resolved(self) -> None:
        alert = make_alert()
        alert.resolved = True
        assert "RESOLVED" in str(alert)

    def test_str_escalated(self) -> None:
        alert = make_alert()
        alert.escalated = True
        assert "ESCALATED" in str(alert)


# ---------------------------------------------------------------------------
# AlertHandler
# ---------------------------------------------------------------------------


class TestAlertHandlerRegistration:
    def test_register_decorator(self) -> None:
        handler = AlertHandler()

        @handler.register(AlertSeverity.CRITICAL)
        def my_fn(alert: SREAlert) -> bool:
            return True

        assert my_fn in handler.get_handlers(AlertSeverity.CRITICAL)

    def test_register_fn(self) -> None:
        handler = AlertHandler()
        fn = lambda alert: True  # noqa: E731
        handler.register_fn(AlertSeverity.ERROR, fn)
        assert fn in handler.get_handlers(AlertSeverity.ERROR)

    def test_registered_severities(self) -> None:
        handler = AlertHandler()
        handler.register_fn(AlertSeverity.CRITICAL, lambda a: True)
        handler.register_fn(AlertSeverity.WARNING, lambda a: True)
        assert AlertSeverity.CRITICAL in handler.registered_severities
        assert AlertSeverity.WARNING in handler.registered_severities
        assert AlertSeverity.ERROR not in handler.registered_severities


class TestAlertHandlerProcessing:
    def _make_handler(self, max_retries: int = 3, dry_run: bool = False) -> AlertHandler:
        return AlertHandler(max_retries=max_retries, dry_run=dry_run)

    def test_resolves_alert_when_handler_returns_true(self) -> None:
        handler = self._make_handler()
        handler.register_fn(AlertSeverity.CRITICAL, lambda a: True)
        alert = make_alert(severity=AlertSeverity.CRITICAL)

        handler.process([alert])

        assert alert.resolved is True
        assert alert.escalated is False
        assert alert.remediation_attempts == 1

    def test_escalates_when_no_handler_registered(self) -> None:
        handler = self._make_handler()
        alert = make_alert(severity=AlertSeverity.CRITICAL)

        handler.process([alert])

        assert alert.escalated is True
        assert alert.resolved is False

    def test_escalates_after_max_retries(self) -> None:
        handler = self._make_handler(max_retries=2)
        handler.register_fn(AlertSeverity.CRITICAL, lambda a: False)  # always fails
        alert = make_alert(severity=AlertSeverity.CRITICAL)

        handler.process([alert])

        assert alert.escalated is True
        assert alert.resolved is False

    def test_skips_non_actionable_alerts(self) -> None:
        handler = self._make_handler()
        call_count = 0

        def counting_fn(alert: SREAlert) -> bool:
            nonlocal call_count
            call_count += 1
            return True

        handler.register_fn(AlertSeverity.INFORMATIONAL, counting_fn)
        alert = make_alert(severity=AlertSeverity.INFORMATIONAL)
        handler.process([alert])
        assert call_count == 0  # should not have been called
        assert alert.resolved is False
        assert alert.escalated is False

    def test_skips_already_resolved_alerts(self) -> None:
        handler = self._make_handler()

        handler.register_fn(AlertSeverity.CRITICAL, lambda a: True)
        alert = make_alert(severity=AlertSeverity.CRITICAL)
        alert.resolved = True

        handler.process([alert])
        assert alert.remediation_attempts == 0  # untouched

    def test_dry_run_resolves_without_calling_handler(self) -> None:
        handler = self._make_handler(dry_run=True)
        call_count = 0

        def counting_fn(alert: SREAlert) -> bool:
            nonlocal call_count
            call_count += 1
            return True

        handler.register_fn(AlertSeverity.CRITICAL, counting_fn)
        alert = make_alert(severity=AlertSeverity.CRITICAL)

        handler.process([alert])
        assert call_count == 0
        assert alert.resolved is True

    def test_handler_exception_counts_as_failure(self) -> None:
        handler = self._make_handler(max_retries=1)

        def raising_fn(alert: SREAlert) -> bool:
            raise RuntimeError("boom")

        handler.register_fn(AlertSeverity.CRITICAL, raising_fn)
        alert = make_alert(severity=AlertSeverity.CRITICAL)

        handler.process([alert])
        assert alert.escalated is True

    def test_summary(self) -> None:
        handler = self._make_handler()
        handler.register_fn(AlertSeverity.CRITICAL, lambda a: True)
        handler.register_fn(AlertSeverity.ERROR, lambda a: False)

        a1 = make_alert(severity=AlertSeverity.CRITICAL)
        a2 = make_alert(severity=AlertSeverity.ERROR, name="error-alert")

        processed = handler.process([a1, a2])
        summary = handler.summary(processed)

        assert summary["total"] == 2
        assert summary["resolved"] == 1
        assert summary["escalated"] == 1
        assert summary["pending"] == 0

    def test_multiple_handlers_tried_in_order(self) -> None:
        handler = self._make_handler(max_retries=3)
        called: list[str] = []

        def first_fn(alert: SREAlert) -> bool:
            called.append("first")
            return False

        def second_fn(alert: SREAlert) -> bool:
            called.append("second")
            return True

        handler.register_fn(AlertSeverity.CRITICAL, first_fn)
        handler.register_fn(AlertSeverity.CRITICAL, second_fn)
        alert = make_alert(severity=AlertSeverity.CRITICAL)

        handler.process([alert])

        assert "first" in called
        assert "second" in called
        assert alert.resolved is True
