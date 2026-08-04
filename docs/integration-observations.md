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
Home Assistant version:
NaviMower version:
Navimow firmware:
Map ID and enabled zone IDs:
Docked / mowing / paused / error entity IDs and values:
Per-zone coverage and completion entity IDs:
WH52 gateway model and firmware:
WH52 moisture / soil-temperature / EC entity IDs:
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
