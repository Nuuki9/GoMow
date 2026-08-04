"""GoMow installation configuration.

This is the single source for installation-specific entity IDs and values that
are intended to be calibrated or changed during setup. Every deployable
PyScript imports only the constants it needs from this module.

Do not place credentials here. Home Assistant UI-helper values remain editable
in HA; only their entity IDs belong here.
"""

# ---------------------------------------------------------------------
# Version and feature switches
# ---------------------------------------------------------------------
GOMOW_MODEL_VERSION = "0.1.0-shadow"
ENABLE_MODELLED_DEW = False

# Soil-growth capabilities are intentionally independent of a particular
# hardware model. They remain disabled until the selected device is installed,
# calibrated and its live HA entities are validated. A soil-moisture limiter is
# required only when that later growth capability is enabled; soil temperature
# is always an optional additional limiter.
ENABLE_SOIL_MOISTURE_LIMITER = False
ENABLE_SOIL_TEMPERATURE_LIMITER = False

# ---------------------------------------------------------------------
# Shared Home Assistant entity IDs
# ---------------------------------------------------------------------
OUTDOOR_TEMPERATURE_ENTITY = "sensor.outdoor_temperature"
OUTDOOR_HUMIDITY_ENTITY = "sensor.netatmo_home_outside_humidity"
WIND_SPEED_ENTITY = "sensor.met_office_bagshot_wind_speed_3_hourly"
SOLAR_RADIATION_ENTITY = "sensor.solar_radiation"
PRESSURE_ENTITY = "sensor.netatmo_home_indoor_pressure"
RAINING_ENTITY = "binary_sensor.is_it_raining"
SUN_ENTITY = "sun.sun"
HOME_LOCATION_ENTITY = "zone.home"

REFERENCE_ET_ENTITY = "sensor.reference_et_hourly"
REFERENCE_ET_RECALCULATION_TRIGGER = "period(1h)"
GROUND_WETNESS_BACKING_ENTITY = "pyscript.ground_wetness_score_backing"
GROUND_WETNESS_SCORE_ENTITY = "sensor.ground_wetness_score"
GROUND_WETNESS_SEED_SERVICE = "pyscript.seed_ground_wetness_score"

# Final public decision contract. The boolean remains intentionally simple for
# consumers; the paired trace exposes the full explainability envelope.
MOW_RECOMMENDED_ENTITY = "binary_sensor.mow_recommended"
DECISION_TRACE_ENTITY = "sensor.gomow_decision_trace"

# Optional soil-sensor capability entities. Set a discovered, validated entity
# ID before enabling its matching limiter. None means the capability is absent,
# not an unhealthy required input. WH51 supplies moisture only; WH52 may supply
# all three; a dedicated soil-temperature device (such as WN34S) may supply
# temperature independently.
SOIL_MOISTURE_ENTITY = None
SOIL_TEMPERATURE_ENTITY = None
SOIL_EC_ENTITY = None

# ---------------------------------------------------------------------
# Site and reference-ET calibration
# ---------------------------------------------------------------------
# TODO: verify from a reliable elevation source before enabling automatic use.
HOME_ELEVATION_M = 100.0
WIND_MEASUREMENT_HEIGHT_M = 10.0
WIND_SHELTER_FACTOR = 0.4
DEFAULT_NIGHT_CLOUDINESS_RATIO = 0.7

# ---------------------------------------------------------------------
# Surface-wetness model
# ---------------------------------------------------------------------
WETNESS_MAX_SCORE_MM = 1.5
WETNESS_MAX_ELAPSED_HOURS = 6.0

# Deliberately unset until observed wet/dry cycles are recorded. Ground-dry
# logic must refuse to enable while either threshold is None.
DRY_ENTER_THRESHOLD_MM = None
WET_ENTER_THRESHOLD_MM = None
MINIMUM_DRY_DURATION_MINUTES = None

# ---------------------------------------------------------------------
# Conservative modelled-dew heuristic
# ---------------------------------------------------------------------
# Keep disabled until the rain/dew/wetness pipeline is validated in shadow mode.
DEW_SPREAD_FULL_C = 1.0
DEW_SPREAD_ZERO_C = 3.5
TARGET_DEW_PER_NIGHT_MM = 0.2
DEW_NIGHT_DURATION_HOURS = 8.0
DEW_MINIMUM_RH_PCT = 85.0
DEW_MAXIMUM_WIND_MPH = 5.0
DEW_MAXIMUM_SUN_ELEVATION_DEG = -4.0
DEW_MINIMUM_AIR_TEMPERATURE_C = 4.0
