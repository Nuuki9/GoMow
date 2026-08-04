"""Reference evapotranspiration (FAO-56 hourly Penman-Monteith).

Produces ``sensor.reference_et_hourly`` in mm/h as a *calibrated drying-demand
heuristic* for the grass-surface wetness model. It is not treated as a literal
free-water-film evaporation measurement. It never dispatches or permits mowing.
"""

import datetime
import math

from gomow_config import (
    DEFAULT_NIGHT_CLOUDINESS_RATIO,
    GOMOW_MODEL_VERSION,
    HOME_ELEVATION_M,
    HOME_LOCATION_ENTITY,
    OUTDOOR_HUMIDITY_ENTITY,
    OUTDOOR_TEMPERATURE_ENTITY,
    PRESSURE_ENTITY,
    REFERENCE_ET_ENTITY,
    SOLAR_RADIATION_ENTITY,
    WIND_MEASUREMENT_HEIGHT_M,
    WIND_SHELTER_FACTOR,
    WIND_SPEED_ENTITY,
)

# FAO-56 mathematical invariants; these are not installation settings.
ET_ALBEDO = 0.23
ET_SOLAR_CONSTANT_MJ_M2_MIN = 0.0820
ET_STEFAN_BOLTZMANN_HOURLY = 2.043e-10


def et_safe_float(entity_id):
    """Return a finite float state or ``None`` for missing/invalid input."""
    value = state.get(entity_id)
    if value is None or str(value).lower() in ("unknown", "unavailable", ""):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


@time_trigger("startup")
@state_trigger(
    f"{OUTDOOR_TEMPERATURE_ENTITY}",
    f"{OUTDOOR_HUMIDITY_ENTITY}",
    f"{WIND_SPEED_ENTITY}",
    f"{SOLAR_RADIATION_ENTITY}",
    f"{PRESSURE_ENTITY}",
)
def update_reference_et():
    """Recalculate the current hourly ET0 whenever a source value changes."""
    air_temperature_c = et_safe_float(OUTDOOR_TEMPERATURE_ENTITY)
    relative_humidity_pct = et_safe_float(OUTDOOR_HUMIDITY_ENTITY)
    wind_mph = et_safe_float(WIND_SPEED_ENTITY)
    solar_w_m2 = et_safe_float(SOLAR_RADIATION_ENTITY)
    pressure_hpa = et_safe_float(PRESSURE_ENTITY)

    if None in (
        air_temperature_c,
        relative_humidity_pct,
        wind_mph,
        solar_w_m2,
        pressure_hpa,
    ):
        log.warning("reference_et: skipping update because one or more inputs are invalid")
        return
    if not 0.0 <= relative_humidity_pct <= 100.0 or pressure_hpa <= 0.0:
        log.warning("reference_et: skipping update because humidity or pressure is out of range")
        return

    location_attrs = state.getattr(HOME_LOCATION_ENTITY) or {}
    latitude = et_safe_float_attr(location_attrs, "latitude")
    longitude = et_safe_float_attr(location_attrs, "longitude")
    if latitude is None or longitude is None:
        log.warning("reference_et: home latitude/longitude unavailable")
        return

    solar_mj_m2_h = max(solar_w_m2, 0.0) * 0.0036
    wind_ms_raw = max(wind_mph, 0.0) * 0.44704
    log_term = math.log(67.8 * WIND_MEASUREMENT_HEIGHT_M - 5.42)
    wind_2m_open_ms = wind_ms_raw * (4.87 / log_term)
    wind_2m_ms = max(wind_2m_open_ms * WIND_SHELTER_FACTOR, 0.0)

    saturation_vapour_pressure_kpa = 0.6108 * math.exp(
        (17.27 * air_temperature_c) / (air_temperature_c + 237.3)
    )
    actual_vapour_pressure_kpa = (
        saturation_vapour_pressure_kpa * relative_humidity_pct / 100.0
    )
    vapour_pressure_curve_slope = (
        4098 * saturation_vapour_pressure_kpa / ((air_temperature_c + 237.3) ** 2)
    )
    pressure_kpa = pressure_hpa / 10.0
    psychrometric_constant = 0.000665 * pressure_kpa

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    day_of_year = now_utc.timetuple().tm_yday
    decimal_hour_utc = now_utc.hour + 0.5
    latitude_rad = math.radians(latitude)
    declination = 0.409 * math.sin((2 * math.pi / 365) * day_of_year - 1.39)
    seasonal_angle = (2 * math.pi * (day_of_year - 81)) / 364
    seasonal_correction = (
        0.1645 * math.sin(2 * seasonal_angle)
        - 0.1255 * math.cos(seasonal_angle)
        - 0.025 * math.sin(seasonal_angle)
    )
    longitude_west = -longitude
    solar_time_angle = (math.pi / 12) * (
        decimal_hour_utc + 0.06667 * (0.0 - longitude_west) + seasonal_correction - 12
    )
    solar_time_start = solar_time_angle - math.pi / 24
    solar_time_end = solar_time_angle + math.pi / 24
    inverse_relative_distance = 1 + 0.033 * math.cos((2 * math.pi / 365) * day_of_year)
    extraterrestrial_radiation = (12 * 60 / math.pi) * ET_SOLAR_CONSTANT_MJ_M2_MIN
    extraterrestrial_radiation *= inverse_relative_distance * (
        (solar_time_end - solar_time_start) * math.sin(latitude_rad) * math.sin(declination)
        + math.cos(latitude_rad)
        * math.cos(declination)
        * (math.sin(solar_time_end) - math.sin(solar_time_start))
    )
    extraterrestrial_radiation = max(extraterrestrial_radiation, 0.0)
    clear_sky_radiation = (0.75 + 2e-5 * HOME_ELEVATION_M) * extraterrestrial_radiation
    if clear_sky_radiation > 0.05:
        cloudiness_ratio = max(0.0, min(solar_mj_m2_h / clear_sky_radiation, 1.0))
    else:
        cloudiness_ratio = DEFAULT_NIGHT_CLOUDINESS_RATIO

    net_shortwave_radiation = (1 - ET_ALBEDO) * solar_mj_m2_h
    air_temperature_k = air_temperature_c + 273.16
    net_longwave_radiation = ET_STEFAN_BOLTZMANN_HOURLY * (air_temperature_k**4)
    net_longwave_radiation *= 0.34 - 0.14 * math.sqrt(actual_vapour_pressure_kpa)
    net_longwave_radiation *= 1.35 * cloudiness_ratio - 0.35
    net_radiation = net_shortwave_radiation - net_longwave_radiation
    soil_heat_flux = 0.1 * net_radiation if net_radiation > 0 else 0.5 * net_radiation

    aerodynamic_term = psychrometric_constant * (37 / (air_temperature_c + 273))
    aerodynamic_term *= wind_2m_ms * (saturation_vapour_pressure_kpa - actual_vapour_pressure_kpa)
    numerator = 0.408 * vapour_pressure_curve_slope * (net_radiation - soil_heat_flux)
    numerator += aerodynamic_term
    denominator = vapour_pressure_curve_slope + psychrometric_constant * (1 + 0.34 * wind_2m_ms)
    et0_mm_h = max(numerator / denominator, 0.0)

    state.set(
        REFERENCE_ET_ENTITY,
        round(et0_mm_h, 4),
        {
            "friendly_name": "Reference ET (Hourly, Penman-Monteith)",
            "unit_of_measurement": "mm/h",
            "icon": "mdi:water-percent",
            "state_class": "measurement",
            "model_version": GOMOW_MODEL_VERSION,
            "model_interpretation": "calibrated grass-surface drying-demand heuristic",
            "net_radiation_mj_m2_h": round(net_radiation, 4),
            "wind_speed_2m_ms": round(wind_2m_ms, 3),
            "wind_speed_2m_open_ms": round(wind_2m_open_ms, 3),
            "vapour_pressure_deficit_kpa": round(
                saturation_vapour_pressure_kpa - actual_vapour_pressure_kpa, 4
            ),
            "cloudiness_ratio": round(cloudiness_ratio, 3),
            "psychrometric_constant": round(psychrometric_constant, 5),
            "pressure_kpa": round(pressure_kpa, 3),
            "last_calculated": now_utc.isoformat(),
        },
    )


def et_safe_float_attr(attributes, key):
    """Return a finite float attribute or ``None``."""
    value = attributes.get(key)
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None
