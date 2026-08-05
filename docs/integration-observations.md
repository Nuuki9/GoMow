# Integration Observations

This document holds **observed facts** about the installed mower, gateway, firmware, Home Assistant entities, and real job behaviour. Keep it separate from the intended architecture.

## Baseline reviewed before implementation

| Area | Observation | Evidence / follow-up |
|---|---|---|
| Mower integration | NaviMower (`vahesoo/NaviMower`) is the mower-control integration. | Confirm installed version before implementation. |
| Zone tracking | The reviewed integration provides map/zone activity, coverage, and completion-oriented data. | Record actual entity IDs and semantics from this installation. |
| Completion | Map-level timestamps are diagnostic/corroborating only; pending-job target-zone verification remains authoritative. | Validate normal, interrupted, cancelled, and near-complete jobs. |
| Cutting height | Height is reported but no verified HA write control was found in the reviewed integration. | Recheck only on a later NaviMower update. |
| Soil sensor | Select WH51 or WH52 after gateway/HA validation. Moisture is required for the later growth limiter; soil temperature is optional and EC remains diagnostic. | Record actual gateway, firmware, sensor IDs, units, and update cadence. |
| Home Assistant / PyScript runtime (2026-08-04) | `Home-Assistant-Core` is running, with `/config` mounted from its Unraid appdata path. The `pyscript` and `navimower` custom integrations are installed. | Read-only discovery via Dockhand; no HA configuration or container state was changed. |
| Existing PyScript deployment (2026-08-04) | `/config/pyscript/` contains pre-existing `reference_et.py`, `ground_wetness_score.py`, and `dew_accumulation.py`, dated before this repository work. It does **not** contain the reviewed repository's `modules/` layout. | Treat these as a legacy live baseline. Do not copy/reload the repository baseline until entity mapping and a deliberate deployment step are agreed. |

## To record when available

```text
NaviMower version: custom integration exposes `navimower.export_diagnostics`; installed version still to record.
Navimow firmware: not returned by current diagnostics.
Map ID and enabled zone IDs: map `2` (base `22330484`); Main `8`, Side `7`, Slope `6`.
Docked / mowing / paused / error entity IDs and values: `lawn_mower.navimow_i210_lidar_pro` currently docked (`0101`); active/terminal transitions still need observation.
Per-zone coverage and completion entity IDs: map coverage plus diagnostic `zone_states`; all zone `last_completed_at` currently null.
Soil-sensor gateway model and firmware:
Soil-sensor entity IDs:
Rain-source entity semantics and update behaviour:
```

## Observation log

Add dated entries below. Record the source entity, exact observed transition, job ID where relevant, and whether it confirmed or challenged an architectural assumption.

| Date | Component | Observation | Consequence / decision reference |
|---|---|---|---|
| — | — | — | — |
| 2026-08-04 | NaviMower live state | `lawn_mower.navimow_i210_lidar_pro` is `docked` (`state_code: 0101`), reports `current_zone: All`, `current_physical_zone: Side`, and exposes a map API path. The stale `lawn_mower.navimow_old` is unavailable. `select.navimow_i210_lidar_pro_mow_zone` reports `All zones`; cutting-height controls are currently unavailable. | Use the current i210 entity only. Continue read-only discovery of map/zone completion entities before implementing tracking. |
| 2026-08-04 | NaviMower completion and protection telemetry | `sensor.navimow_i210_lidar_pro_map_coverage` reports three zones, 0 completed zones, and `zone_states_revision: 196`. `last_map_mowed` is `2026-07-31T18:06:32+00:00`; `last_map_completed` is currently `unknown`. The mower's own rain sensor/detection, frost, snow, strong-wind, high-temperature, and rain-forecast controls are all enabled. | Retain the map timestamp as diagnostic only; do not infer a complete all-zone job from it. This confirms GoMow is additive to—not a replacement for—mower protections. |
| 2026-08-04 | Netatmo rain | `sensor.netatmo_home_rain_sensor_rain_last_hour` is `0 mm`, `state_class: total`; `sensor.netatmo_home_rain_sensor_rain` is `0 mm`, `state_class: measurement`. Both last changed at `2026-08-03T21:29:00Z`. | Candidate source identified, but its reset/update semantics still need an observed fresh rain event before `rain_accumulation.py` is bound to it. |
| 2026-08-05 | Netatmo light-rain check | User observed light rain. At 09:18Z both candidate Netatmo rain entities still reported `0 mm` and had not updated since `2026-08-03T21:29:00Z`; `binary_sensor.is_it_raining` was `off`. In contrast, reference ET updated at 09:13Z, so HA itself was alive. | This is not a usable rain-event observation. Do not bind either candidate to GoMow yet; re-check after a measurable event or investigate the Netatmo rain module/entity update path read-only. |
| 2026-08-05 | Netatmo rain update/reset confirmed | At 13:52Z, `sensor.netatmo_home_rain_sensor_rain_last_hour` was currently `0 mm` but its state had freshly changed at 10:03Z. Because its prior observed state was also `0 mm` from 2026-08-03, that transition proves an intervening non-zero rain value followed by a return to zero. The direct `..._rain` measurement and `binary_sensor.is_it_raining` remained stale. | Bind only `..._rain_last_hour` as the measured rolling-hour source. Treat it as a windowed value with timestamp-based deduplication/reset handling—not as a monotonic counter—and never use the stale direct-measurement or binary entity. |
| 2026-08-04 | NaviMower read-only diagnostic export | `navimower.export_diagnostics` completed with `commands_sent: false`. It resolved map `2` (base `22330484`) and three zones: Main `8` (439.55 m²), Side `7` (208.45 m²), and Slope `6` (28.01 m²). All `last_completed_at` values were null before the test; coverage was 4%, 8%, and 24% respectively. The existing schedule is Mon all zones (09:00–21:00) and Thu Main only (09:00–21:00). | Zone IDs and live map identity are evidenced. Coverage is diagnostic only. |
| 2026-08-04 | NaviMower two-zone run: start snapshot | User started a native restart mow of Side `7` + Slope `6`; no GoMow command was issued. At 13:22:09Z the mower transitioned to `mowing` (`0210`). `task_progress` exposed `task_zone_ids: [6, 7]`, area 236.46 m², active zone `7`, and initial cycle ID `1785849728406-2`; `target_zone` was Side via `mqtt_work_target`. `last_map_completed` remained `unknown`, while `last_map_mowed` advanced to `2026-08-04T13:22:07Z` at task start. | Critical distinction confirmed: `last_map_mowed` is a start/activity diagnostic, not completion evidence. Persist the explicit target-zone list in the later pending-job tracker; integration cycle IDs are diagnostic only until their lifecycle is proven stable. |
| 2026-08-04 | NaviMower two-zone run: terminal snapshot | Mower docked at 16:09:11Z. Selected-task progress reached 100%; map coverage reached 37.6% with `completed_zone_count: 2`; `last_map_completed` stayed `unknown`. Slope `6` and Side `7` each reached 100% with fresh `last_completed_at` values of 13:41:32Z and 16:08:01Z. Main `8` remained 4% and its July timestamps were unchanged. Diagnostics retained three sessions; the two intended zones appeared across rewritten session/cycle IDs and all session records had `completed: false`, despite the clean docked outcome. | This validates target-relative completion: docked + 100% selected-task progress + fresh per-target-zone completion, while Main and map completion remain unchanged. Do not use integration session `completed`, `cycle_id`, `last_map_mowed`, or `last_map_completed` as standalone job-success authority. |
