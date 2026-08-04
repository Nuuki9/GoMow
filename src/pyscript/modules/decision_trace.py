"""Canonical, pure explainability trace for derived GoMow decisions."""

from datetime import datetime
from typing import Any, Mapping, Sequence


TRACE_SCHEMA_VERSION = "1"

# Lower number means a stronger explanation for the same false recommendation.
_REASON_PRECEDENCE = {
    "RECOVERY_UNCONFIRMED": 10,
    "INPUT_STALE": 20,
    "INPUT_INVALID": 21,
    "INPUT_UNAVAILABLE": 22,
    "MANUAL_HOLD": 30,
    "ACTIVE_RAIN": 40,
    "WET_SURFACE": 41,
    "FROST": 42,
    "HEAT": 43,
    "NOT_DUE": 50,
    "DISPATCHER_NOT_READY": 60,
}


def _ordered_reason_codes(reason_codes: Sequence[str]) -> tuple[str, ...]:
    """Deduplicate deterministically without discarding simultaneous blocks."""
    unique = dict.fromkeys(reason_codes)
    return tuple(
        sorted(unique, key=lambda code: (_REASON_PRECEDENCE.get(code, 999), code))
    )


def _state_for(recommendation: bool, reason_codes: tuple[str, ...]) -> str:
    if recommendation:
        return "RECOMMEND"
    if any(code.startswith("INPUT_") for code in reason_codes):
        return "NOT_READY"
    if "RECOVERY_UNCONFIRMED" in reason_codes:
        return "RECOVERY_UNCONFIRMED"
    if "MANUAL_HOLD" in reason_codes:
        return "HELD"
    if reason_codes == ("NOT_DUE",):
        return "NOT_DUE"
    return "BLOCKED"


def build_decision_trace(
    *,
    gates: Mapping[str, bool],
    blocking_reason_codes: Sequence[str],
    factors: Mapping[str, Mapping[str, Any]],
    model_version: str,
    evaluated_at: datetime,
) -> dict[str, Any]:
    """Build the immutable public trace for one final decision evaluation."""
    ordered_reasons = _ordered_reason_codes(blocking_reason_codes)
    recommendation = not ordered_reasons and all(gates.values())
    return {
        "state": _state_for(recommendation, ordered_reasons),
        "recommendation": recommendation,
        "primary_reason_code": ordered_reasons[0] if ordered_reasons else None,
        "blocking_reason_codes": ordered_reasons,
        "gates": dict(gates),
        "factors": {name: dict(factor) for name, factor in factors.items()},
        "model_version": model_version,
        "evaluated_at": evaluated_at.isoformat(),
        "trace_schema_version": TRACE_SCHEMA_VERSION,
    }
