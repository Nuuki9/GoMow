# Decision Register

## 13. Assumptions and Decisions Register

| ID | Category | Decision / Assumption | Status | Revisit trigger |
|---|---|---|---|---|
| DEC-001 | Wetness | `MAX_SCORE = 1.5 mm` is conservative surface-film headroom, not soil water. | Active | Lawn visibly dry at high score or visibly wet at low score. |
| DEC-002 | ET | Use FAO-56 hourly Penman–Monteith reference ET as the drying-demand proxy. | Active | Drying calibration shows systematic error. |
| DEC-003 | ET | Wind is corrected 10 m → 2 m then reduced with a garden shelter factor. | Active | Local observed dry-down differs persistently. |
| DEC-004 | ET | Fixed night cloudiness fallback remains acceptable initially. | Active | Night drying materially affects decisions. |
| DEC-005 | ET | Reference ET underestimates free-water-film drying; accept conservative delay. | Active | Lawn consistently dries materially earlier than score. |
| DEC-006 | Wetness | Persisted `pyscript.*` backing entity plus public `sensor.*` mirror. | Active | HA/pyscript persistence or statistics behaviour changes. |
| DEC-007 | Wetness | Cap elapsed decay after restart/outage/clock anomaly. | Active | Recovery behaviour proves problematic. |
| DEC-008 | Wetness | Restored unattributed score is assigned to dew attribution with explicit diagnostic reason. | Active | Immediate post-restart rain/dew split becomes operationally important. |
| DEC-009 | Wetness | Manual test seed is attributed to dew unless a test-specific source is introduced. | Active | Rain-specific testing requires a separate seed mechanism. |
| DEC-010 | Dew | Dew point is self-derived using the shared Magnus–Tetens constants. | Active | ET formula constants change. |
| DEC-011 | Dew | Use one tunable target overnight dew amount to derive the maximum rate. | Active | Observation demonstrates persistent scale error. |
| DEC-012 | Dew | Replace spread-only dew accumulation with a conservative night/RH/wind/rain-gated heuristic. | Active | Direct leaf-wetness sensor added or data shows unreliable behaviour. |
| DEC-013 | Rain | Fresh measured rain saturates surface score; do not repeatedly act on stale rolling hourly totals. | Active | Netatmo source semantics prove different. |
| DEC-014 | Rain | Prefer measured accumulation over tip-to-tip inferred instantaneous rate. | Active | Fresh accumulation cannot be deduplicated reliably. |
| DEC-015 | Ground firmness | No soil-firmness modifier initially; sandy lawn and lightweight mower reduce rutting risk. | Active | Ruts, slip, or saturated-ground damage observed. |
| DEC-016 | Hysteresis | Dry occurs at low score; wet occurs at high score; `WET_ENTER > DRY_ENTER`. Require a minimum dry duration. | Active | Observation data supports threshold changes. |
| DEC-017 | Growth | Use bounded response curves, not cumulative GDD. | Active | Observed mowing demand is poorly represented. |
| DEC-018 | Growth | Use `min()` as an interpretable limiting-factor combination. It is not more conservative than multiplication. | Active | Data supports a different combination method. |
| DEC-019 | Growth | Apply response curves to daily inputs, then smooth response history; do not curve only a 7-day raw mean. | Active | Validation shows no material gain over simpler averaging. |
| DEC-020 | Growth | Use continuous interval formula with a floor and exponent, not a lookup table. | Active | Empirical tuning shows a table is clearer/better. |
| DEC-021 | Conditions | Frost floor remains air temperature ≥ 4°C. | Active | Winter observations show false blocks or frost risk. |
| DEC-022 | Conditions | Heat ceiling remains air temperature ≤ 30°C. | Active | Mower thermal behaviour or turf observations differ. |
| DEC-023 | Forecast | Forecast is not a Phase-1 safety gate; reactive rain handling remains independent. | Active | Excessive interruption cycles observed. |
| DEC-024 | Seasonal | Optional UI-configurable off-season block remains a backstop. | Active | A full seasonal validation cycle shows it unnecessary. |
| DEC-025 | Zone policy | Phase 1 sends all enabled zones but records explicit per-job target zones. | Active | Evidence shows static zone timing materially improves outcomes. |
| DEC-026 | Zone policy | Later zone scheduling uses static growth profiles only, not per-zone weather/soil models. | Deferred | Phase-1 data supports a worthwhile benefit. |
| DEC-027 | Completion | Canonical successful-mow state is updated only from a verified pending job and fresh per-target-zone completion evidence. | Active | NaviMower changes completion semantics. |
| DEC-028 | Integration | NaviMower map timestamps are diagnostics/corroboration, not standalone completion authority. | Active | Integration introduces an authoritative job-completion ID. |
| DEC-029 | Soil sensor | Use Ecowitt WH52 subject to gateway/HA compatibility validation. | Planned | Required HA entities unavailable or unreliable. |
| DEC-030 | Soil model | Air temperature is the primary shoot-growth signal; soil temperature is a root-support limiter, not a replacement. | Active after WH52 validation | Observed model performance contradicts this division. |
| DEC-031 | EC | WH52 electrical conductivity is diagnostic only and excluded from mowing decisions. | Active | Strong, validated lawn-health use case emerges. |
| DEC-032 | Leaf wetness | No leaf-wetness hardware in Phase 1; retain it as an optional accuracy upgrade. | Active | Modelled dew causes repeated wrong or over-conservative decisions. |
| DEC-033 | Cut height | Defer height automation until NaviMower provides safe verified write control. | Deferred | Writable control becomes available and validated. |
| DEC-034 | Rollout | Use shadow/assisted operation pragmatically to tune decision quality and verify command tracking. Automatic starts are an explicit user-controlled policy setting; repository changes never enable them by themselves. | Active | The scheduling/control boundary changes. |
| DEC-035 | Configuration | Installation-specific entity IDs and intentionally tunable values live in one explicit `gomow_config` PyScript module. Scripts import only their required constants; implementation-private mathematical constants remain local. | Active | Pyscript module semantics or the project’s configuration boundary changes. |
| DEC-036 | Protection boundary | GoMow supplements calendar scheduling only. It must not alter, bypass, or claim to replace Navimow/NaviMower built-in safeguards; calibration measures recommendation quality, not mower safety certification. | Active | A future integration exposes an explicit, user-approved safety-control interface. |

---
