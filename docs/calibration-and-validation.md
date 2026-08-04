# Calibration and Validation Log

This is the evidence record for tuning whether GoMow recommends mowing sensibly in real lawn conditions, and for checking that its Home Assistant command tracking reflects what happened. It does not certify or replace the mower's built-in protections. Do not replace observations with assumed values.

## Calibration principles

- Tune against visible grass-surface condition and actual mower outcomes.
- Treat WH52 moisture as a locally calibrated trend, not universal volumetric water content.
- Tune wetness thresholds only after observing complete wet-to-dry cycles.
- Record the prior value, proposed value, reason, evidence, date, and decision ID for every change.

## Useful decision-quality and tracking scenarios

| Scenario | Decision-quality / tracking evidence |
|---|---|
| Dry all-zone mow | GoMow recommends mowing when the lawn looks suitable; where dispatched, the requested zones and canonical full-mow timestamp are tracked correctly. |
| Rain before start | GoMow recommends waiting while active rain or its wetness model indicates unsuitable conditions. |
| Rain during job | Existing reactive NaviMower/HA handling remains in control; GoMow classifies the job interrupted rather than complete. |
| Manual stop | GoMow records the incomplete job accurately and does not claim a full mow. |
| Failed start | GoMow reports failure without duplicate commands. |
| Restart during job | Pending state restores and resolves from fresh evidence without duplicate starts. |
| Near-complete zone | The integration's accepted completion behaviour is understood and documented. |
| Dew/dry-down cycle | `ground_dry` recommendation is compared with visible grass-surface condition. |
| WH52 rain/dry cycle | Moisture and soil-temperature trends are compared with known conditions before inclusion in scheduling. |

## Change log

| Date | Metric / threshold | Before | After | Evidence | DEC reference |
|---|---|---:|---:|---|---|
| — | — | — | — | — | — |
