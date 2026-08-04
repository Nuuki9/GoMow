# Integration Observations

This document holds **observed facts** about the installed mower, gateway, firmware, Home Assistant entities, and real job behaviour. Keep it separate from the intended architecture.

## Baseline reviewed before implementation

| Area | Observation | Evidence / follow-up |
|---|---|---|
| Mower integration | NaviMower (`vahesoo/NaviMower`) is the mower-control integration. | Confirm installed version before implementation. |
| Zone tracking | The reviewed integration provides map/zone activity, coverage, and completion-oriented data. | Record actual entity IDs and semantics from this installation. |
| Completion | Map-level timestamps are diagnostic/corroborating only; pending-job target-zone verification remains authoritative. | Validate normal, interrupted, cancelled, and near-complete jobs. |
| Cutting height | Height is reported but no verified HA write control was found in the reviewed integration. | Recheck only on a later NaviMower update. |
| Soil sensor | WH52 is planned, subject to gateway firmware and Home Assistant entity validation. | Record actual gateway, firmware, sensor IDs, units, and update cadence. |

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
