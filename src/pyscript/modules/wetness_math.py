"""Pure maths shared by GoMow's PyScript wetness files.

This module deliberately has no Home Assistant/PyScript dependencies so its
invariants can be unit tested outside the live Home Assistant runtime.
"""

import math


MAGNUS_A = 17.27
MAGNUS_B_C = 237.3


def apportion_decay(rain_score, dew_score, decay_amount):
    """Subtract decay proportionally while preserving non-negative scores."""
    rain_score, dew_score = apportion_decay_components(
        (rain_score, dew_score), decay_amount
    )
    return rain_score, dew_score


def apportion_decay_components(component_scores, decay_amount):
    """Proportionally subtract decay from an arbitrary component tuple."""
    components = tuple(max(float(score), 0.0) for score in component_scores)
    decay_amount = max(float(decay_amount), 0.0)
    total = sum(components)
    if total == 0.0 or decay_amount >= total:
        return tuple(0.0 for _ in components)
    remaining_total = total - decay_amount
    return tuple(remaining_total * score / total for score in components)


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
