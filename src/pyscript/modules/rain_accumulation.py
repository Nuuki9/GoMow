"""Pure policy for ingesting a non-monotonic rolling-hour rain source."""

from dataclasses import dataclass
from datetime import datetime, timedelta
import math


@dataclass(frozen=True)
class RollingHourRainOutcome:
    """One auditable response to a rolling-hour source observation."""

    action: str
    reason: str
    source_healthy: bool
    next_checkpoint: datetime | None


def ingest_rolling_hour_observation(
    *,
    observation_mm: float,
    observed_at: datetime,
    prior_checkpoint: datetime | None,
    evaluated_at: datetime,
    maximum_age: timedelta,
) -> RollingHourRainOutcome:
    """Deduplicate source timestamps; any fresh positive window saturates wetness."""
    try:
        value = float(observation_mm)
    except (TypeError, ValueError):
        return RollingHourRainOutcome("none", "rain_value_invalid", False, prior_checkpoint)
    if not math.isfinite(value) or value < 0.0:
        return RollingHourRainOutcome("none", "rain_value_invalid", False, prior_checkpoint)
    if evaluated_at - observed_at > maximum_age:
        return RollingHourRainOutcome("none", "rain_source_stale", False, prior_checkpoint)
    if prior_checkpoint is not None and observed_at <= prior_checkpoint:
        return RollingHourRainOutcome("none", "rain_observation_duplicate", True, prior_checkpoint)
    if value == 0.0:
        return RollingHourRainOutcome(
            "none", "rolling_hour_window_expired", True, observed_at
        )
    del evaluated_at, maximum_age
    return RollingHourRainOutcome(
        "saturate", "fresh_positive_rolling_hour_rain", True, observed_at
    )
