"""Measured-rain input for GoMow's shadow-only surface-wetness model.

The Netatmo source is a non-monotonic rolling-hour window, not a cumulative
counter. Each accepted source change may therefore saturate the surface score
once; repeated values, zeros, and invalid readings never add water.
"""

import datetime

from gomow_config import (
    RAIN_CHECKPOINT_ENTITY,
    RAIN_LAST_HOUR_ENTITY,
    RAIN_MAXIMUM_AGE_MINUTES,
    WETNESS_MAX_SCORE_MM,
)
from rain_accumulation import ingest_rolling_hour_observation
from wetness_store import components, parse_timestamp, safe_float, write_components


CHECKPOINT_TIMESTAMP_ORIGIN = "home_assistant_last_changed"


def _source_last_changed():
    """Return Pyscript's virtual, UTC source-state timestamp if valid."""
    value = state.get(f"{RAIN_LAST_HOUR_ENTITY}.last_changed")
    return value if isinstance(value, datetime.datetime) else None


def _checkpoint():
    return parse_timestamp(state.get(RAIN_CHECKPOINT_ENTITY))


def _diagnostics(outcome, observation_mm, observed_at):
    return {
        "rain_source_entity": RAIN_LAST_HOUR_ENTITY,
        "rain_source_healthy": outcome.source_healthy,
        "rain_source_reason": outcome.reason,
        "rain_action": outcome.action,
        "rain_observation_mm": observation_mm,
        "rain_observation_timestamp": observed_at.isoformat(),
        "rain_observation_timestamp_origin": CHECKPOINT_TIMESTAMP_ORIGIN,
        "rain_last_accepted_checkpoint": (
            outcome.next_checkpoint.isoformat() if outcome.next_checkpoint else None
        ),
    }


@time_trigger("startup")
def restore_rain_observation_checkpoint():
    """Restore only the deduplication checkpoint; never replay a static value."""
    state.persist(RAIN_CHECKPOINT_ENTITY, default_value=None)


@state_trigger(f"{RAIN_LAST_HOUR_ENTITY}")
def ingest_rain_observation():
    """Accept one fresh rolling-window observation and publish its provenance."""
    observed_at = _source_last_changed()
    observation_mm = safe_float(RAIN_LAST_HOUR_ENTITY)
    if observed_at is None:
        rain_score_mm, dew_score_mm, unattributed_score_mm = components()
        write_components(
            rain_score_mm,
            dew_score_mm,
            unattributed_score_mm,
            "rain_source_timestamp_invalid",
            {
                "rain_source_entity": RAIN_LAST_HOUR_ENTITY,
                "rain_source_healthy": False,
                "rain_source_reason": "rain_source_timestamp_invalid",
                "rain_action": "none",
                "rain_observation_mm": observation_mm,
                "rain_observation_timestamp": None,
                "rain_observation_timestamp_origin": CHECKPOINT_TIMESTAMP_ORIGIN,
            },
        )
        return
    outcome = ingest_rolling_hour_observation(
        observation_mm=observation_mm,
        observed_at=observed_at,
        prior_checkpoint=_checkpoint(),
        evaluated_at=datetime.datetime.now(datetime.timezone.utc),
        maximum_age=datetime.timedelta(minutes=RAIN_MAXIMUM_AGE_MINUTES),
    )
    if outcome.next_checkpoint is not None:
        state.set(RAIN_CHECKPOINT_ENTITY, outcome.next_checkpoint.isoformat())

    if outcome.action == "saturate":
        write_components(
            WETNESS_MAX_SCORE_MM,
            0.0,
            0.0,
            outcome.reason,
            _diagnostics(outcome, observation_mm, observed_at),
        )
        return

    rain_score_mm, dew_score_mm, unattributed_score_mm = components()
    write_components(
        rain_score_mm,
        dew_score_mm,
        unattributed_score_mm,
        outcome.reason,
        _diagnostics(outcome, observation_mm, observed_at),
    )
