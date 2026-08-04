"""Reference-ET drying integration for GoMow's persisted surface-wetness state.

This public sensor is diagnostic only. A future ``binary_sensor.ground_dry``
will be the sole wetness contract exposed to mower decision logic.
"""

import datetime

from gomow_config import (
    GROUND_WETNESS_BACKING_ENTITY,
    GROUND_WETNESS_SCORE_ENTITY,
    GROUND_WETNESS_SEED_SERVICE,
    REFERENCE_ET_ENTITY,
    WETNESS_MAX_ELAPSED_HOURS,
)
from wetness_math import apportion_decay_components
from wetness_store import components, parse_timestamp, safe_float, write_components


@time_trigger("startup")
def restore_ground_wetness_score():
    """Restore persisted total conservatively; provenance is unavailable on restart."""
    state.persist(GROUND_WETNESS_BACKING_ENTITY, default_value=0.0)
    restored_total_mm = safe_float(GROUND_WETNESS_BACKING_ENTITY)
    write_components(
        0.0,
        0.0,
        restored_total_mm if restored_total_mm is not None else 0.0,
        "startup_restore",
        {
            "decay_rate_mm_h": 0.0,
            "decay_last_calculated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        },
    )


@state_trigger(f"{REFERENCE_ET_ENTITY}")
def apply_reference_et_decay():
    """Integrate prior ET rate over real elapsed time, then retain the new rate."""
    et0_mm_h = safe_float(REFERENCE_ET_ENTITY)
    reference_attrs = state.getattr(REFERENCE_ET_ENTITY) or {}
    reference_is_valid = reference_attrs.get("input_valid") is True
    now = datetime.datetime.now(datetime.timezone.utc)
    rain_score_mm, dew_score_mm, unattributed_score_mm = components()
    attributes = state.getattr(GROUND_WETNESS_SCORE_ENTITY) or {}
    last_calculated = parse_timestamp(attributes.get("decay_last_calculated"))
    prior_rate_mm_h = attributes.get("decay_rate_mm_h")

    if et0_mm_h is None or not reference_is_valid:
        write_components(
            rain_score_mm,
            dew_score_mm,
            unattributed_score_mm,
            "decay_input_invalid",
            {"decay_rate_mm_h": 0.0, "decay_last_calculated": now.isoformat()},
        )
        log.warning("ground_wetness_score: ET input invalid; drying paused fail-closed")
        return

    if last_calculated is None or prior_rate_mm_h is None:
        write_components(
            rain_score_mm,
            dew_score_mm,
            unattributed_score_mm,
            "decay_baseline_initialised",
            {"decay_rate_mm_h": et0_mm_h, "decay_last_calculated": now.isoformat()},
        )
        return

    elapsed_hours = max(0.0, (now - last_calculated).total_seconds() / 3600.0)
    elapsed_hours = min(elapsed_hours, WETNESS_MAX_ELAPSED_HOURS)
    rain_score_mm, dew_score_mm, unattributed_score_mm = apportion_decay_components(
        (rain_score_mm, dew_score_mm, unattributed_score_mm),
        max(float(prior_rate_mm_h), 0.0) * elapsed_hours,
    )
    write_components(
        rain_score_mm,
        dew_score_mm,
        unattributed_score_mm,
        "reference_et_decay",
        {
            "decay_amount_mm": round(max(float(prior_rate_mm_h), 0.0) * elapsed_hours, 4),
            "decay_rate_mm_h": et0_mm_h,
            "decay_last_calculated": now.isoformat(),
        },
    )


@service(GROUND_WETNESS_SEED_SERVICE)
def seed_ground_wetness_score(value=None):
    """Set total wetness for shadow-mode validation; never a mower-control action."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        log.warning("seed_ground_wetness_score: numeric value required")
        return
    write_components(0.0, value, 0.0, "manual_seed")
