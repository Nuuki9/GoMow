"""Conservative, gated modelled-dew input for GoMow surface wetness.

This is an intentionally calibrated heuristic pending shadow-mode validation.
It never substitutes for a future leaf-wetness measurement and never makes a
mowing decision by itself.
"""

import datetime

from gomow_config import (
    DEW_MAXIMUM_SUN_ELEVATION_DEG,
    DEW_MAXIMUM_WIND_MPH,
    DEW_MINIMUM_AIR_TEMPERATURE_C,
    DEW_MINIMUM_RH_PCT,
    DEW_NIGHT_DURATION_HOURS,
    DEW_SPREAD_FULL_C,
    DEW_SPREAD_ZERO_C,
    ENABLE_MODELLED_DEW,
    GROUND_WETNESS_SCORE_ENTITY,
    OUTDOOR_HUMIDITY_ENTITY,
    OUTDOOR_TEMPERATURE_ENTITY,
    RAINING_ENTITY,
    SUN_ENTITY,
    TARGET_DEW_PER_NIGHT_MM,
    WIND_SPEED_ENTITY,
    WETNESS_MAX_ELAPSED_HOURS,
)
from wetness_math import dew_intensity, dew_point_celsius
from wetness_store import apply_delta, parse_timestamp, safe_float


DEW_MAX_RATE_MM_H = TARGET_DEW_PER_NIGHT_MM / DEW_NIGHT_DURATION_HOURS


def dew_is_active_binary_sensor(entity_id):
    return str(state.get(entity_id)).lower() in ("on", "true", "1")


def dew_gate(air_temperature_c, relative_humidity_pct, wind_mph):
    """Return a boolean and audit-friendly reason for the dew heuristic gate."""
    if not ENABLE_MODELLED_DEW:
        return False, "feature_disabled"
    if dew_is_active_binary_sensor(RAINING_ENTITY):
        return False, "rain_active"
    if air_temperature_c < DEW_MINIMUM_AIR_TEMPERATURE_C:
        return False, "air_temperature_below_frost_gate"
    if relative_humidity_pct < DEW_MINIMUM_RH_PCT:
        return False, "relative_humidity_below_gate"
    if wind_mph > DEW_MAXIMUM_WIND_MPH:
        return False, "wind_above_gate"
    sun_attrs = state.getattr(SUN_ENTITY) or {}
    try:
        sun_elevation_deg = float(sun_attrs.get("elevation"))
    except (TypeError, ValueError):
        return False, "sun_elevation_unavailable"
    if sun_elevation_deg > DEW_MAXIMUM_SUN_ELEVATION_DEG:
        return False, "sun_above_gate"
    return True, "favourable"


@state_trigger(
    f"{OUTDOOR_TEMPERATURE_ENTITY}",
    f"{OUTDOOR_HUMIDITY_ENTITY}",
    f"{WIND_SPEED_ENTITY}",
    f"{RAINING_ENTITY}",
    f"{SUN_ENTITY}",
)
def apply_dew_accumulation():
    """Integrate the prior dew rate over elapsed time, then calculate the next."""
    air_temperature_c = safe_float(OUTDOOR_TEMPERATURE_ENTITY)
    relative_humidity_pct = safe_float(OUTDOOR_HUMIDITY_ENTITY)
    wind_mph = safe_float(WIND_SPEED_ENTITY)
    now = datetime.datetime.now(datetime.timezone.utc)

    if None in (air_temperature_c, relative_humidity_pct, wind_mph):
        apply_delta(
            reason="dew_input_invalid",
            extra_attributes={"dew_rate_mm_h": 0.0, "dew_last_calculated": now.isoformat()},
        )
        log.warning("dew_accumulation: invalid input; dew accumulation paused fail-closed")
        return
    if not 0.0 <= relative_humidity_pct <= 100.0:
        apply_delta(
            reason="dew_humidity_out_of_range",
            extra_attributes={"dew_rate_mm_h": 0.0, "dew_last_calculated": now.isoformat()},
        )
        return

    allowed, gate_reason = dew_gate(air_temperature_c, relative_humidity_pct, wind_mph)
    if not ENABLE_MODELLED_DEW:
        apply_delta(
            reason="dew_feature_disabled",
            extra_attributes={
                "dew_rate_mm_h": 0.0,
                "dew_last_calculated": now.isoformat(),
                "dew_gate": gate_reason,
            },
        )
        return

    dew_point_c = dew_point_celsius(air_temperature_c, relative_humidity_pct)
    spread_c = air_temperature_c - dew_point_c
    current_rate_mm_h = (
        DEW_MAX_RATE_MM_H * dew_intensity(spread_c, DEW_SPREAD_FULL_C, DEW_SPREAD_ZERO_C)
        if allowed
        else 0.0
    )

    attributes = state.getattr(GROUND_WETNESS_SCORE_ENTITY) or {}
    prior_rate_mm_h = attributes.get("dew_rate_mm_h")
    last_calculated = parse_timestamp(attributes.get("dew_last_calculated"))
    if prior_rate_mm_h is None or last_calculated is None:
        apply_delta(
            reason="dew_baseline_initialised",
            extra_attributes={
                "dew_rate_mm_h": round(current_rate_mm_h, 4),
                "dew_last_calculated": now.isoformat(),
                "dew_gate": gate_reason,
                "dew_point_c": round(dew_point_c, 2),
                "dew_point_spread_c": round(spread_c, 2),
            },
        )
        return

    elapsed_hours = max(0.0, (now - last_calculated).total_seconds() / 3600.0)
    elapsed_hours = min(elapsed_hours, WETNESS_MAX_ELAPSED_HOURS)
    dew_delta_mm = max(float(prior_rate_mm_h), 0.0) * elapsed_hours
    apply_delta(
        dew_delta_mm=dew_delta_mm,
        reason="modelled_dew_accumulation" if dew_delta_mm else "dew_gate_closed",
        extra_attributes={
            "dew_delta_mm": round(dew_delta_mm, 4),
            "dew_rate_mm_h": round(current_rate_mm_h, 4),
            "dew_last_calculated": now.isoformat(),
            "dew_gate": gate_reason,
            "dew_point_c": round(dew_point_c, 2),
            "dew_point_spread_c": round(spread_c, 2),
        },
    )
