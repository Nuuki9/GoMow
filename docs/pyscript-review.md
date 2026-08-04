# Initial PyScript Review and Import

**Status:** repository-only baseline; not copied to Home Assistant; no mowing action is enabled.

## Scope reviewed

The following user-supplied Stage 1–3 files were reviewed and imported:

- `reference_et.py`
- `ground_wetness_score.py`
- `dew_accumulation.py`

The imported baseline deliberately does **not** include rain accumulation, the
`binary_sensor.ground_dry` contract, growth/due logic, mower readiness, pending-job
tracking, or dispatch. Those remain later stages.

## Changes made during import

| Topic | Original state | Imported baseline |
|---|---|---|
| Configuration | Entity IDs and tunables duplicated in each file. | One explicit `modules/gomow_config.py`; scripts import only required values. |
| Cross-file state access | Dew assumed an implicit shared top-level `apply_delta()` function. | Explicit `modules/wetness_store.py` API; no load-order/global-namespace dependency. |
| Wetness ceiling | `15.0 mm`. | Agreed `1.5 mm` grass-surface interception ceiling. |
| ET timing | Newly arrived ET rate was retrospectively applied to the preceding elapsed interval. | Prior ET rate is integrated over real elapsed time, then the new rate is stored. |
| Component accounting | Dew expected a missing function; public attributes did not retain all timestamps. | Rain/dew component totals, rates, timestamps, reasons, and diagnostics are retained through the shared writer. |
| Dew model | Accumulated whenever dew-point spread was favourable. | Conservative gates for feature enablement, active rain, frost-temperature floor, RH, wind, and sun elevation. Disabled by default pending shadow-mode validation. |
| Reference ET framing | Presented as the decay driver. | Explicitly documented as a calibrated drying-demand heuristic, not a literal wet-surface evaporation observation. |
| Safety boundary | No mower-control code in these files. | Retained: no mower service calls or dispatch logic exist in the imported baseline. |

## Configuration status

`gomow_config.py` contains the known entity IDs and model settings. The following
must remain unresolved until actual Home Assistant evidence is recorded:

- `HOME_ELEVATION_M` is a setup TODO, not a verified site measurement.
- Ground-dry hysteresis thresholds and minimum dry duration are deliberately `None`.
- `ENABLE_MODELLED_DEW` is `False`.
- WH52 entity IDs are not yet added; they require installed-version and entity
  validation first.

## Test evidence

The repository includes deterministic tests for:

- proportional, non-negative rain/dew drying;
- dew-point and dew-intensity maths;
- central configuration contract and the 1.5 mm ceiling;
- prior-rate ET integration; and
- no dew addition while the modelled-dew feature is disabled.

These are software-level checks only. They are not calibration evidence and do not
permit deployment or automatic mowing.

## Required next implementation work

1. Confirm all configured input entity IDs, units, update cadence, and freshness in
   the actual HA installation.
2. Build measured, deduplicated Netatmo rain accumulation.
3. Validate the wetness model in shadow mode across observed wet/dry cycles.
4. Calibrate hysteresis and minimum-dry thresholds; only then build
   `binary_sensor.ground_dry`.
5. Complete input-health, job tracking, and assisted-mode verification before any
   automatic-start work.
