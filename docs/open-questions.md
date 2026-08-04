# Open Questions and Required Evidence

## 14. Open Questions and Evidence Required

These are not implementation blockers until their relevant stage, but must be resolved before the feature that depends on them is enabled.

| Question | Required evidence / resolution |
|---|---|
| Does the selected soil-sensor gateway firmware expose the required values locally? | Confirm WH51 moisture (and, for WH52, soil temperature/EC), battery, and signal in gateway/app. |
| Does the installed HA release expose the selected sensor entities correctly? | Confirm real entity IDs, units, freshness, and statistics; update HA only under normal change control if needed. |
| What moisture values represent dry, healthy, and too-wet local turf? | Calibrated installation plus rain/dry-down observation history. |
| What soil-temperature curve best represents this lawn? | At least one spring/autumn transition and observed mowing demand. |
| Do Netatmo rain entities provide a reliable fresh event/cumulative signal? | Inspect exact entity semantics, timestamps, and duplicate behaviour before coding rain accumulation. |
| Which NaviMower entities are authoritative for docked, mowing, paused, error, and completion states on this mower/firmware? | Record normal, interrupted, and completed real jobs in shadow/assisted mode. |
| What constitutes a practical mowing window? | Measure real all-zone job duration, charge cycles, and daylight limits. |
| Is a direct leaf-wetness sensor justified later? | Compare `ground_dry` predictions with actual dew/wetness observations over multiple cycles. |
| Is selected-zone scheduling worthwhile? | Demonstrate persistent, meaningful growth differences and acceptable partial-job efficiency. |
| Does NaviMower later offer cutting-height write control? | Verify a supported writable HA entity/service and safe read-back behaviour. |

---
