# Calibration and Validation Log

This is the evidence record for threshold tuning and for advancing from shadow mode to assisted and unattended operation. Do not replace observations with assumed values.

## Calibration principles

- Tune against visible grass-surface condition and actual mower outcomes.
- Treat WH52 moisture as a locally calibrated trend, not universal volumetric water content.
- Tune wetness thresholds only after observing complete wet-to-dry cycles.
- Record the prior value, proposed value, reason, evidence, date, and decision ID for every change.

## Required validation scenarios

| Scenario | Required result before unattended operation |
|---|---|
| Dry all-zone mow | Pending job starts, all requested zones complete, and canonical full-mow timestamp updates once. |
| Rain before start | Active-rain or ground-wet gate blocks dispatch. |
| Rain during job | Existing reactive handling docks/pauses mower; job is classified interrupted, not complete. |
| Manual stop | Job remains incomplete and is auditable. |
| Failed start | Dispatcher times out/reports failure without duplicate commands. |
| Restart during job | Pending state restores; no duplicate start; completion is resolved from fresh evidence. |
| Near-complete zone | Integration's accepted completion behaviour is observed and documented. |
| Dew/dry-down cycle | `ground_dry` transition is compared with actual grass-surface condition. |
| WH52 rain/dry cycle | Moisture and soil temperature trends are compared with known conditions before inclusion in scheduling. |

## Change log

| Date | Metric / threshold | Before | After | Evidence | DEC reference |
|---|---|---:|---:|---|---|
| — | — | — | — | — | — |
