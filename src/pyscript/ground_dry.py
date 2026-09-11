"""Shadow-only public contract for GoMow's grass-surface dryness gate.

Thresholds remain deliberately unset until wet-to-dry observations establish
an empirical calibration. Until then the state is conservatively off and its
attributes explain that it must not be used to authorise a mowing command.
"""

import datetime

from gomow_config import (
    DRY_ENTER_THRESHOLD_MM,
    GOMOW_MODEL_VERSION,
    GROUND_DRY_ENTITY,
    GROUND_WETNESS_SCORE_ENTITY,
    MINIMUM_DRY_DURATION_MINUTES,
    WET_ENTER_THRESHOLD_MM,
)
from wetness_store import safe_float


def _base_attributes(score_mm):
    thresholds_configured = all(
        value is not None
        for value in (
            DRY_ENTER_THRESHOLD_MM,
            WET_ENTER_THRESHOLD_MM,
            MINIMUM_DRY_DURATION_MINUTES,
        )
    )
    return {
        "friendly_name": "Ground Dry",
        "device_class": "moisture",
        "model_version": GOMOW_MODEL_VERSION,
        "surface_model_entity": GROUND_WETNESS_SCORE_ENTITY,
        "wetness_score_mm": score_mm,
        "dry_enter_threshold_mm": DRY_ENTER_THRESHOLD_MM,
        "wet_enter_threshold_mm": WET_ENTER_THRESHOLD_MM,
        "minimum_dry_duration_minutes": MINIMUM_DRY_DURATION_MINUTES,
        "thresholds_configured": thresholds_configured,
        "calibrated": False,
        "calibration_status": "not_implemented",
        "shadow_only": True,
        "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@state_trigger(f"{GROUND_WETNESS_SCORE_ENTITY}")
@time_trigger("startup")
def evaluate_ground_dry_shadow():
    """Publish an explicitly uncalibrated, conservative public boolean."""
    score_mm = safe_float(GROUND_WETNESS_SCORE_ENTITY)
    attributes = _base_attributes(score_mm)
    if score_mm is None:
        attributes.update(
            {
                "primary_reason_code": "WETNESS_INPUT_INVALID",
                "blocking_reason_codes": ["WETNESS_INPUT_INVALID"],
                "evaluated_gates": {"wetness_score_valid": False, "calibrated": False},
            }
        )
    else:
        attributes.update(
            {
                "primary_reason_code": "WETNESS_UNCALIBRATED",
                "blocking_reason_codes": ["WETNESS_UNCALIBRATED"],
                "evaluated_gates": {"wetness_score_valid": True, "calibrated": False},
            }
        )
    state.set(GROUND_DRY_ENTITY, "off", attributes)
