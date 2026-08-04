"""Pure maths shared by GoMow's PyScript wetness files.

This module deliberately has no Home Assistant/PyScript dependencies so its
invariants can be unit tested outside the live Home Assistant runtime.
"""

import math


MAGNUS_A = 17.27
MAGNUS_B_C = 237.3


def apportion_decay(rain_score, dew_score, decay_amount):
    """Subtract decay proportionally while preserving non-negative scores.

    The returned component scores always sum to the remaining total. If decay
    exceeds the total, both components become zero.
    """
    rain_score = max(float(rain_score), 0.0)
    dew_score = max(float(dew_score), 0.0)
    decay_amount = max(float(decay_amount), 0.0)
    total = rain_score + dew_score

    if total == 0.0 or decay_amount >= total:
        return 0.0, 0.0

    remaining_total = total - decay_amount
    return (
        remaining_total * (rain_score / total),
        remaining_total * (dew_score / total),
    )


def dew_point_celsius(air_temperature_c, relative_humidity_pct):
    """Return Magnus-Tetens dew point in degrees Celsius."""
    relative_humidity_pct = min(max(float(relative_humidity_pct), 0.1), 100.0)
    air_temperature_c = float(air_temperature_c)
    alpha = math.log(relative_humidity_pct / 100.0) + (
        MAGNUS_A * air_temperature_c / (MAGNUS_B_C + air_temperature_c)
    )
    return MAGNUS_B_C * alpha / (MAGNUS_A - alpha)


def dew_intensity(spread_c, full_spread_c, zero_spread_c):
    """Return a 0..1 linear dew-potential scale for a dew-point spread."""
    if full_spread_c >= zero_spread_c:
        raise ValueError("full_spread_c must be lower than zero_spread_c")
    spread_c = float(spread_c)
    if spread_c <= full_spread_c:
        return 1.0
    if spread_c >= zero_spread_c:
        return 0.0
    return (zero_spread_c - spread_c) / (zero_spread_c - full_spread_c)
