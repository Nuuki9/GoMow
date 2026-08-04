"""Shared PyScript state access for the grass-surface wetness model.

This module is the only writer for the persisted backing state and public
wetness sensor. It is imported explicitly by wetness-model scripts; no script
relies on implicit top-level namespace sharing.
"""

import datetime
import math

from gomow_config import (
    GOMOW_MODEL_VERSION,
    GROUND_WETNESS_BACKING_ENTITY,
    GROUND_WETNESS_SCORE_ENTITY,
    WETNESS_MAX_SCORE_MM,
)


def safe_float(entity_id):
    value = state.get(entity_id)
    if value is None or str(value).lower() in ("unknown", "unavailable", ""):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def parse_timestamp(value):
    if not value:
        return None
    try:
        parsed = datetime.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    return parsed.replace(tzinfo=datetime.timezone.utc) if parsed.tzinfo is None else parsed


def _nonnegative_float(value):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(value, 0.0) if math.isfinite(value) else 0.0


def components():
    attributes = state.getattr(GROUND_WETNESS_SCORE_ENTITY) or {}
    return (
        _nonnegative_float(attributes.get("rain_score_mm")),
        _nonnegative_float(attributes.get("dew_score_mm")),
    )


def write_components(rain_score_mm, dew_score_mm, reason, extra_attributes=None):
    rain_score_mm = _nonnegative_float(rain_score_mm)
    dew_score_mm = _nonnegative_float(dew_score_mm)
    total_score_mm = rain_score_mm + dew_score_mm
    if total_score_mm > WETNESS_MAX_SCORE_MM:
        scale = WETNESS_MAX_SCORE_MM / total_score_mm
        rain_score_mm *= scale
        dew_score_mm *= scale
        total_score_mm = WETNESS_MAX_SCORE_MM

    attributes = dict(state.getattr(GROUND_WETNESS_SCORE_ENTITY) or {})
    attributes.update(
        {
            "friendly_name": "Ground Wetness Score",
            "unit_of_measurement": "mm",
            "icon": "mdi:water-alert-outline",
            "state_class": "measurement",
            "model_version": GOMOW_MODEL_VERSION,
            "model_interpretation": "grass-surface water heuristic; not soil moisture",
            "rain_score_mm": round(rain_score_mm, 4),
            "dew_score_mm": round(dew_score_mm, 4),
            "max_score_mm": WETNESS_MAX_SCORE_MM,
            "last_update_reason": reason,
            "last_calculated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    )
    if extra_attributes:
        attributes.update(extra_attributes)
    state.set(GROUND_WETNESS_BACKING_ENTITY, round(total_score_mm, 4))
    state.set(GROUND_WETNESS_SCORE_ENTITY, round(total_score_mm, 4), attributes)


def apply_delta(rain_delta_mm=0.0, dew_delta_mm=0.0, reason="model_update", extra_attributes=None):
    rain_score_mm, dew_score_mm = components()
    write_components(
        rain_score_mm + _nonnegative_float(rain_delta_mm),
        dew_score_mm + _nonnegative_float(dew_delta_mm),
        reason,
        extra_attributes,
    )
