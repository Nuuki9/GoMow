# GoMow Architecture

## 1. Goal and Design Boundary

The system will decide **when it is suitable to mow**, **when mowing is due**, and **which zones form the job**. It will run in Home Assistant and dispatch the mower through NaviMower only after every required gate is satisfied.

The architecture separates three questions:

1. **Is mowing safe and suitable now?**
   Surface wetness, active rain, temperature, daylight/start window, data health, and mower readiness.
2. **Is mowing due?**
   A continuous global growth-potential model determines mowing demand and the derived target interval.
3. **What job should be sent?**
   Phase 1 requests all enabled zones. The state and tracking model is zone-aware from the outset so selected-zone jobs can be added later without redesign.

This is intentionally not a literal simulation of grass growth or surface physics. It is a conservative, observable decision system that uses direct measurements where available and simple calibrated models only where direct measurement is unavailable.

---

## 2. Core Design Principles

These principles are binding for future work.

- **Architecture before implementation.** Agree the design, implement in small stages, validate against real data, then proceed.
- **Central configuration and named constants.** Installation-specific source entity IDs and intentionally tunable values live in the version-controlled `gomow_config` module. Deployable scripts explicitly import only what they use. Mathematical invariants and implementation-private constants remain local to the owning file; UI-adjustable operating values remain Home Assistant helpers, whose entity IDs are centrally configured.
- **Measured over modelled.** Prefer direct, representative measurements where they exist. Models are fallbacks or interpolation layers, not a default substitute for a sensor.
- **Conservative tie-breaks.** If uncertain, wait rather than start mowing.
- **Separate measurement, model, decision, and dispatch.** Continuous scores feed simple booleans; automations consume booleans and an explicit job plan, never raw mechanics.
- **Fail closed.** `unknown`, `unavailable`, stale, invalid, or un-restored inputs must prevent an automatic start.
- **Event-driven state changes; elapsed-time-aware maths.** Sensor changes initiate calculation, while rate/accumulation calculations integrate actual elapsed time and protect against outages or clock jumps.
- **Diagnostics are first-class.** Calculated entities expose sub-scores, source freshness, thresholds, timestamps, model version, and decision reasons.
- **Pragmatism over theoretical purity.** Do not add a small theoretical improvement when it adds significant operational or diagnostic complexity.
- **Document simplifications.** Every deliberate approximation is recorded with its limitation and revision trigger.

---

## 3. Top-Level Architecture

```text
Measured weather, soil, and mower data
              │
              ├── Surface Wetness Model ──> binary_sensor.ground_dry
              │
              ├── Current Conditions ────> binary_sensor.mowing_allowed_now
              │
              ├── Growth Potential Model ─> sensor.growth_potential_score
              │                              └> sensor.derived_mowing_interval
              │
              ├── Zone Completion State ──> zone freshness / due state
              │
              └── Input Health ───────────> binary_sensor.mower_inputs_healthy

Mowing planner
  global growth due + Phase-1 all enabled zones
              │
              ▼
Mower dispatcher/state machine
  eligible → start requested → mowing → terminal verification
              │
              ▼
NaviMower command and per-zone completion evidence
```

### Public contracts

Downstream mower-control automation must consume only these contracts:

| Contract | Meaning |
|---|---|
| `binary_sensor.ground_dry` | Grass surface is judged dry enough to mow. |
| `binary_sensor.mowing_allowed_now` | All immediate environmental and operational safety gates pass. |
| `binary_sensor.mower_inputs_healthy` | Required source data is valid and fresh. |
| `sensor.growth_potential_score` | Diagnostic continuous estimate of current mowing demand potential. |
| `sensor.derived_mowing_interval` | Diagnostic target interval derived from growth potential. |
| `binary_sensor.mow_due` | A mowing job is due under the active scheduling policy. |
| `sensor.planned_mow_zone_list` | The immutable target-zone list for the next proposed job. |

The only component permitted to issue a `navimower.mow` command is the mower dispatcher.

---

## 4. Mower Control and Job Tracking — NaviMower

### 4.1 Integration boundary

NaviMower is the integration used to control and observe the Segway Navimow mower. It exposes mower controls, explicit zone mowing, task/map progress, map and per-zone coverage, mower activity, persistent route/session history, and optional per-zone completion timestamp entities.[NaviMower](references.md#navimower)

NaviMower uses an undocumented private-cloud protocol alongside official Smart Home OAuth/MQTT data and describes itself as experimental. Its commands and state handling therefore require a fail-closed health gate, explicit command acknowledgement, and validation in a safe shadow/assisted phase before unattended starts.[NaviMower](references.md#navimower)

### 4.2 Phase-1 all-zone policy

Automatic Phase-1 jobs always request:

```text
all enabled mowing zones
```

The `navimower.mow` service accepts an explicit ordered zone list; an empty list means all zones, but the system should resolve and record the explicit IDs before dispatch.[NaviMower](references.md#navimower)

This keeps the lawn visually consistent and avoids small, inefficient partial jobs. It also establishes the state model required for selected-zone scheduling later.

### 4.3 Why aggregate completion is not enough

NaviMower provides both **Last map mowed** and **Last map completed**. They are useful diagnostics but must not directly update the system's canonical `last_successful_full_mow` value.

- **Last map mowed** means recent mowing activity in at least one zone; it is not completion evidence.
- **Last map completed** is useful corroboration, but map completion can reflect retained individual-zone completion history. It does not by itself prove that all zones completed in the current HA-dispatched job.

A successful job is always relative to the job's immutable target-zone list.

### 4.4 Pending-job record

At dispatch, create a persisted `pending_mow_job` record:

```text
job_id
created_at
start_requested_at
accepted_start_at
target_zone_ids
map_identity_or_revision
reason_for_dispatch
model_version
outcome
completed_zone_ids
interrupted_zone_ids
failure_reason
```

The target-zone list must not change after dispatch.

### 4.5 Successful completion rule

For a Phase-1 full-map job, update `input_datetime.last_successful_full_mow` only when all conditions are true:

```text
- The job was started by this dispatcher.
- The mower entered a confirmed mowing state after the command.
- Every target zone has fresh completion evidence after the job began.
- The mower reached an acceptable terminal state (normally docked / vendor-ended).
- No error, manual cancellation, unsafe interruption, or unresolved stale-data state occurred.
- Completion evidence matches the pending job's map and zone list.
```

NaviMower treats vendor-ended cycles at 95% or above as practically completed. The system will use the integration's verified per-zone completion semantics, not impose a separate arbitrary 100% rule.[NaviMower](references.md#navimower)

### 4.6 Dispatcher state machine

```text
IDLE
  → ELIGIBLE
  → START_REQUESTED
  → MOWING
  → RETURNING
  → COMPLETION_VERIFYING
  → COMPLETED
  → COOLDOWN

Failure exits:
  START_FAILED
  INTERRUPTED
  ERROR
  MANUAL_HOLD
```

Required dispatcher behaviours:

- issue no duplicate start command;
- timeout if a start command is not acknowledged by a mowing state;
- retain the pending job through Home Assistant restart;
- distinguish a deliberately docked/paused mower from a failed job;
- write a concise audit event for every transition;
- never infer completion from elapsed duration alone.

### 4.7 Manual and safety controls

Create UI-adjustable helpers before enabling automatic dispatch:

```text
input_boolean.mower_automation_enabled
input_boolean.mower_manual_hold
input_boolean.mower_weather_override        # time-limited if enabled
input_button.mower_reset_decision_lock
input_button.mower_mark_job_complete        # assisted-phase fallback only
```

A manual hold always overrides all automatic logic.

---

## 5. Input Health Gate

`binary_sensor.mower_inputs_healthy` is a separate prerequisite for dispatch. It verifies the required sensor values are numeric, plausible, fresh enough, and restored after restart.

Minimum initial inputs:

| Input | Required for | Health requirement |
|---|---|---|
| Outdoor temperature | current conditions; air growth response | valid, fresh |
| Outdoor humidity | ET and dew model | valid, fresh |
| Solar radiation | ET model | valid, fresh |
| Wind source | ET and dew gate | valid, fresh; source labelled as measured or forecast |
| Pressure | ET model | valid, plausible |
| Rain source | active-rain gate and accumulation | valid, fresh, deduplicated |
| Reference ET | wetness decay | valid, non-negative |
| Wetness backing state | `ground_dry` | restored and internally consistent |
| NaviMower status | dispatch and completion | known and fresh enough |
| WH52 moisture/temperature | growth model once enabled | valid, calibrated, fresh |

If any required value is stale, `unknown`, `unavailable`, implausible, or absent after restart:

```text
mower_inputs_healthy = off
```

This prevents automatic dispatch. Diagnostics should state the precise failed input and age.

---

## 6. Surface Wetness Model

### 6.1 Goal

Produce `binary_sensor.ground_dry`: a conservative boolean answering:

> Is the grass surface likely dry enough to mow now?

It models **surface water on short grass**, not root-zone soil moisture. The score is a calibrated `mm-equivalent` wetness state, not a literal measurement of water depth.

### 6.2 Pipeline

```text
Fresh rain events ───┐
                      ├──> persisted wetness score ──> hysteresis ──> ground_dry
Conservative dew ────┤              ▲
                      │              │
Reference-ET drying ─┘              └── diagnostic rain/dew attribution
```

### 6.3 Existing wetness score engine

**Files:**

```text
/config/pyscript/reference_et.py
/config/pyscript/ground_wetness_score.py
```

**Entities:**

```text
pyscript.ground_wetness_score_backing     # persisted source of truth
sensor.ground_wetness_score                # public/statistical mirror
sensor.reference_et_hourly                 # mm/h
```

The persisted `pyscript.*` backing entity preserves state; the public `sensor.*` mirror supports Home Assistant statistics. The wetness engine has one score mutation entry point, preserves the invariant:

```text
rain_score + dew_score == total_score
```

and applies elapsed-time-aware ET decay with a maximum elapsed-time safety cap after outage or clock anomalies.

### 6.4 Reference ET

The existing `sensor.reference_et_hourly` uses hourly FAO-56 Penman–Monteith with available weather inputs. FAO-56 reference ET is an established reference-crop method, but it models a transpiring reference canopy rather than a free water film.[FAO-56](references.md#fao-56-reference-et)

**Accepted simplification:** decay derived from reference ET is a conservative drying proxy. A wet grass surface may dry faster than the model indicates; the bias is intentionally toward waiting longer.

Relevant existing choices retained:

- vapour pressure derived directly from relative humidity;
- shared saturation-vapour-pressure constants across ET and dew code;
- 10 m wind corrected to 2 m then reduced with a tunable garden shelter factor;
- real pressure reading used rather than elevation estimate;
- UTC solar geometry;
- ET clamped at zero; condensation is handled by dew separately;
- fixed night cloudiness fallback retained as a documented simplification.

**Data-quality note:** the current wind source is forecast-derived, not a local measurement. This is an explicitly labelled modelling input; replace it with measured local wind if such a sensor becomes available and proves reliable.

### 6.5 Rain accumulation — revised design

**File:** `/config/pyscript/rain_accumulation.py`

The model must respond to **fresh measured rain**, not merely a non-zero rolling “rain in the last hour” value.

```text
fresh rain delta / fresh deduplicated observation > noise floor
    → set wetness score to MAX_SCORE
```

Rationale:

- A short meaningful rain event wets a mown turf surface rapidly.
- Additional water runs off or drips through; a saturated surface-state score is sufficient.
- Continued fresh rain observations keep resetting the score.
- A rolling hourly total must not repeatedly reset the score after rain has stopped.

The implementation records a source observation timestamp and deduplication token. If a monotonic cumulative rain source is available, calculate a delta from the last accepted total. Otherwise, process a rolling-window value only once per fresh source observation.

No separate soil-firmness modifier is included initially. The lawn is sandy and the mower is lightweight; revisit only if slipping, rutting, or heavy-rain aftermath proves this assumption wrong.

### 6.6 Dew accumulation — revised Phase-1 design

No physical leaf-wetness sensor is planned for Phase 1.

The existing temperature–dew-point-spread-only implementation must be revised before use. A small air temperature/dew-point spread indicates moist air, but does not prove that the grass surface cooled to the dew point or accumulated dew.

Use a conservative **gated heuristic**:

```text
Dew may accumulate only when:
  - it is night / below a configurable sun-elevation threshold;
  - relative humidity is above a named threshold;
  - wind is below a named threshold;
  - active rain is not detected;
  - air temperature is above the frost safety regime.

Within that gate:
  dew-point spread is a rate modifier, not proof of dew.
```

The model retains one tunable overnight-dew target and derives an hourly maximum rate from it. It deliberately errs toward reporting wetness when cloud, wind, or radiative cooling are uncertain.

**Future optional upgrade:** a physical leaf-wetness sensor would be the preferred direct measurement of grass-surface wetness. It could lead `ground_dry` and demote the dew model to a fallback/diagnostic role. No such hardware is planned now.

### 6.7 `ground_dry` hysteresis — corrected polarity

Because a larger score means a wetter surface, hysteresis must operate as follows:

```text
If currently WET:
  turn DRY only when score <= DRY_ENTER_THRESHOLD

If currently DRY:
  turn WET when score >= WET_ENTER_THRESHOLD

WET_ENTER_THRESHOLD > DRY_ENTER_THRESHOLD
```

`ground_dry` should also require a configurable continuous dry duration before it turns on. This prevents one brief transition from triggering a job.

Thresholds remain empirical and will be tuned from observed wet/dry cycles; they must not be guessed as physical constants before data exists.

---

## 7. Growth Potential and Mowing-Demand Model

### 7.1 Goal

Estimate the conditions that favour production of mowable leaf growth and derive a target mowing interval. This is a **growth-potential model**, not a direct grass-height measurement.

It answers:

> Given the recent atmospheric and root-zone conditions, how much mowing demand is likely to have developed?

### 7.2 Inputs

All growth inputs are global in Phase 1:

| Input | Role | Status |
|---|---|---|
| Outdoor air temperature | Primary proxy for shoot/leaf growth and air heat stress | available |
| WH52 soil temperature | Root-zone thermal support and seasonal inertia | planned; enable after validation |
| WH52 soil moisture | Root-zone water availability | planned; enable after calibration |
| EC | Lawn-health / fertiliser-salinity diagnostic only | planned; excluded from scheduling |

No per-zone moisture, soil temperature, wetness, ET, or weather model is planned.

### 7.3 Air temperature: primary shoot-growth response

Air temperature remains the primary temperature signal for mowing demand because mowing removes leaf/shoot growth. Cool-season turf has strong shoot growth in mild conditions and reduced above-ground productivity under sustained heat.[UMass turf-water-deficit guidance](references.md#umass-turf-water-deficits)[University of Nebraska heat guidance](references.md#university-of-nebraska-heat-guidance)

Use a named trapezoidal response curve:

```text
AIR_BASE_C
AIR_OPTIMAL_LOW_C
AIR_OPTIMAL_HIGH_C
AIR_STRESS_HIGH_C
```

The existing initial values are retained as starting hypotheses only:

```text
BASE: 5°C
optimum plateau: 15–24°C
heat-stress onset: 30°C
```

They will be validated against observed lawn behaviour.

### 7.4 Soil temperature: root-support limiter

WH52 soil temperature does not replace air temperature. It adds a separate slower signal for root-zone activity and heat/cold stress.

Cool-season turf roots have a lower thermal optimum than shoots; root activity is strongest at roughly 10–18°C soil temperature and declines in persistently hot soil.[UMass turf-water-deficit guidance](references.md#umass-turf-water-deficits)[University of Nebraska heat guidance](references.md#university-of-nebraska-heat-guidance)

Use an independently named and empirically tuned response curve:

```text
SOIL_ROOT_BASE_C
SOIL_ROOT_OPTIMAL_LOW_C
SOIL_ROOT_OPTIMAL_HIGH_C
SOIL_ROOT_STRESS_HIGH_C
```

Do not reuse air-temperature thresholds for soil temperature.

The soil-temperature response is disabled until all conditions are satisfied:

```text
- WH52 is paired to a supported, current-firmware gateway.
- HA exposes a stable soil-temperature entity with correct units.
- Placement is representative of turf root-zone conditions.
- At least several weather cycles have been observed.
```

Until then, the model is explicitly two-factor: air temperature plus soil moisture.

### 7.5 Soil moisture: water-availability limiter

WH52 moisture replaces a second modelled soil-water-balance approach. It must be treated as a calibrated local trend, not universal volumetric water content.

Use named local calibration points:

```text
SOIL_MOISTURE_DRY_REFERENCE_PCT
SOIL_MOISTURE_HEALTHY_LOW_PCT
SOIL_MOISTURE_HEALTHY_HIGH_PCT
SOIL_MOISTURE_WET_REFERENCE_PCT
```

The initial `20%` and `60%` figures are placeholders only. The probe must be installed at representative turf root depth, allowed to settle, calibrated at dry/wet reference conditions, and observed through rain and dry-down cycles before its value influences automatic scheduling.

### 7.6 Combination rule

Once validated, combine the three normalized inputs using a simple limiting-factor model:

```text
growth_potential_score = min(
    air_shoot_growth_response,
    soil_root_temperature_response,
    soil_moisture_response
)
```

`min()` is selected for interpretability: the most limiting necessary condition caps potential growth. It is **not** mathematically more conservative than multiplication; multiplication would always be equal to or lower than the minimum for scores between zero and one.

### 7.7 Temporal aggregation

Do not apply a response curve only once to a 7-day raw mean temperature. The response curves are non-linear and normal day/night changes can cross their bend points.

Instead:

```text
Daily mean / daily representative input
  → apply each response curve for that day
  → calculate daily growth-potential score
  → smooth with a 7-day rolling mean or EWMA
```

The smoothing window is tunable and should be applied consistently to the air, soil, and moisture response history.

### 7.8 Derived mowing interval

Use a continuous formula rather than a lookup table:

```text
interval_days = max(MIN_INTERVAL_DAYS, K / growth_potential_score ^ EXPONENT)
```

A `GROWTH_DUE_THRESHOLD` prevents mowing at negligible growth potential. All constants are exposed for empirical tuning.

The formula is diagnostic and advisory until real completed-mow history and lawn observations demonstrate it produces sensible timing.

---

## 8. Current Conditions Gate

`binary_sensor.mowing_allowed_now` answers only whether starting mowing is suitable at this moment. It does not decide whether mowing is due.

```text
mowing_allowed_now =
    mower_inputs_healthy
    AND air_temperature_above_frost_floor
    AND air_temperature_below_heat_ceiling
    AND not_currently_raining
    AND ground_dry
    AND start_window_open
    AND mower_operationally_ready
    AND mower_automation_enabled
    AND not_manual_hold
```

| Gate | Initial source / rule | Rationale |
|---|---|---|
| Frost floor | outdoor temperature ≥ 4°C | Grass surface may be colder than screen-height air; retains a thawing buffer. |
| Heat ceiling | outdoor temperature ≤ 30°C | Protects cool-season turf and mower battery from peak heat operation. |
| Active rain | existing trusted `binary_sensor.is_it_raining` | Immediate reactive protection; separate from accumulated wetness. |
| Surface dryness | `binary_sensor.ground_dry` | Answers whether rain/dew residue has dried. |
| Start window | daylight plus sufficient remaining operating window | Avoids starting immediately before darkness or an impractical end-of-day window. |
| Mower readiness | NaviMower activity, dock, battery, errors, pause state | Prevents a command to an unavailable mower. |

### Forecast policy

Forecast awareness is **not** a safety prerequisite in Phase 1. Existing reactive rain handling returns/docks the mower if rain starts mid-job.

A short-horizon forecast check may later improve job quality by avoiding likely interruption, but it must never override current measured rain or wetness data.

---

## 9. Seasonal Block

Retain optional date-only `input_datetime` helpers for a no-mow window.

```text
input_datetime.mower_off_season_start
input_datetime.mower_off_season_end
```

If either helper is unset, the seasonal block is inactive.

The block belongs in the mowing-demand/dispatch layer, not the immediate conditions gate:

```text
“Should mowing be considered during this season?”
```

is distinct from:

```text
“Would mowing be suitable right now?”
```

The manual seasonal block remains a conservative backstop even after WH52 soil-temperature data is available. Revisit only after at least one seasonal cycle of observed data validates the growth model.

---

## 10. Mowing Planner and Dispatch Rules

### 10.1 Phase-1 all-zone plan

```text
mow_due =
    not_off_season
    AND growth_potential_score > threshold
    AND days_since_last_successful_full_mow >= derived_interval

planned_mow_zone_list = all enabled zones
```

An automatic job is dispatched only when:

```text
mow_due AND mowing_allowed_now
```

### 10.2 Shadow and assisted operation

Before unattended starts, use two validation modes:

```text
Shadow mode:
  calculate every score, gate, job plan, and completion outcome;
  notify/log only; do not send a mower command.

Assisted mode:
  present the proposed job and its reasons;
  require a deliberate manual confirmation to start;
  verify the job automatically afterwards.
```

Only enable unattended automatic starts after normal, interrupted, cancelled, and partial-job scenarios have been observed and correctly classified.

### 10.3 Later selected-zone scheduling

Per-zone automatic scheduling is deferred, not rejected.

If warranted by observed growth differences, introduce static, named zone policies only:

```text
zone_growth_multiplier
zone_min_interval_days
zone_max_interval_days
zone_enabled
```

Do not add separate per-zone weather, wetness, soil moisture, ET, or temperature models.

A later zone-specific plan must include:

- minimum practical job area or minimum due-zone count;
- maximum interval for every enabled zone;
- periodic all-zone refresh jobs;
- completion verified only against the job's requested zone list;
- persisted `last_successful_completed_at_by_zone` state.

---

## 11. Cutting Height

NaviMower currently reports global/effective cutting height on supported models but, at the reviewed version, does not expose a Home Assistant writable number, select, or service for changing it.[NaviMower](references.md#navimower)

Therefore cut-height automation is deferred.

When NaviMower exposes a verified writable height control, revisit in this order:

1. global height policy;
2. validated read-back and command refusal/error handling;
3. interaction with mowing frequency;
4. only then possible static zone policies, especially for shaded turf.

Shaded turf may benefit more from a higher cut height than simply a lower mowing frequency; this is a future horticultural policy question, not a Phase-1 automation feature.[UConn shade guidance](references.md#uconn-shaded-lawns)

---

---

See the [implementation plan](implementation-plan.md), [decision register](decisions.md), [open questions](open-questions.md), and [references](references.md).
