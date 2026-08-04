"""Pure selection policy for concise, state-transition GoMow audit events."""

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class AuditEvent:
    """A notable decision change for HA logs and the Logbook."""

    event_code: str
    severity: str
    primary_reason_code: str | None


def select_decision_audit_event(
    previous_trace: Mapping[str, Any] | None,
    current_trace: Mapping[str, Any],
) -> AuditEvent | None:
    """Emit only a meaningful recommendation/state/primary-reason transition."""
    if previous_trace is None:
        return None

    previous_recommendation = previous_trace.get("recommendation")
    current_recommendation = current_trace.get("recommendation")
    current_reason = current_trace.get("primary_reason_code")
    if previous_recommendation != current_recommendation:
        return AuditEvent(
            "DECISION_RECOMMENDATION_CHANGED", "info", current_reason
        )

    if previous_trace.get("primary_reason_code") != current_reason:
        severity = "warning" if current_trace.get("state") == "NOT_READY" else "info"
        return AuditEvent("DECISION_REASON_CHANGED", severity, current_reason)

    return None
