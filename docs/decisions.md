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
| DEC-008 | Wetness | On restore, preserve the persisted total but attribute it as `unattributed` with an explicit diagnostic reason; do not invent a rain/dew split. | Active | Immediate post-restart attribution needs a more authoritative source. |
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
| DEC-029 | Soil sensor | Require calibrated soil moisture, not a fixed model. WH51 is the lawn baseline; admit WH52 after a one-sensor pilot validates moisture, firmware and HA entities. Soil temperature is optional; EC is diagnostic only. | Active | The pilot or a later mature sensor materially changes the evidence. |
| DEC-030 | Soil model | Air temperature is the primary shoot-growth signal. Soil temperature, when available and validated, is an optional root-support limiter; a medium-term air-temperature response is the fallback. | Active after soil-sensor validation | Observed model performance contradicts this division. |
| DEC-031 | EC | Electrical conductivity, if supplied by a WH52, is diagnostic only and excluded from mowing decisions. | Active | Strong, validated lawn-health use case emerges. |
| DEC-032 | Leaf wetness | No leaf-wetness hardware in Phase 1; retain it as an optional accuracy upgrade. | Active | Modelled dew causes repeated wrong or over-conservative decisions. |
| DEC-033 | Cut height | Defer height automation until NaviMower provides safe verified write control. | Deferred | Writable control becomes available and validated. |
| DEC-034 | Rollout | Use shadow/assisted operation pragmatically to tune decision quality and verify command tracking. Automatic starts are an explicit user-controlled policy setting; repository changes never enable them by themselves. | Active | The scheduling/control boundary changes. |
| DEC-035 | Configuration | Installation-specific entity IDs and intentionally tunable values live in one explicit `gomow_config` PyScript module. Scripts import only their required constants; implementation-private mathematical constants remain local. | Active | Pyscript module semantics or the project’s configuration boundary changes. |
| DEC-036 | Protection boundary | GoMow supplements calendar scheduling only. It must not alter, bypass, or claim to replace Navimow/NaviMower built-in safeguards; calibration measures recommendation quality, not mower safety certification. | Active | A future integration exposes an explicit, user-approved safety-control interface. |
| DEC-037 | Verification | Use layered deterministic verification: unit tests, PyScript runtime contracts, timestamped multi-module replay fixtures, deployment checks, then live decision-quality observation. New behaviour and bug fixes are test-first. | Active | A materially different implementation platform or test harness is adopted. |
| DEC-038 | HA recovery | Treat HA start/reload as an explicit recovery state. Restore persisted model/job state, require fresh valid inputs, reconcile any pending job with current mower evidence, and never reissue a start or advance completion merely because state was restored. | Active | The state persistence or dispatcher platform changes materially. |
| DEC-039 | Tuning governance | Diagnose source/integration correctness before model parameters; record real-world evidence, change one centrally configured parameter at a time, and add a deterministic replay/boundary test for each behaviour change. | Active | A controlled calibration platform supersedes the documented observation process. |
| DEC-040 | Capability configuration | Separate core mandatory entities from optional/unbound hardware capabilities and feature-enabled requirements. Soil temperature is hardware-agnostic and optional; its fallback is smoothed air-temperature response plus the seasonal policy backstop. | Active | The growth model gains a mandatory independent soil-temperature requirement. |
| DEC-041 | Explainability | Every non-trivial derived decision must expose a stable reason-code/attribute contract. `binary_sensor.mow_recommended` is the final simple consumer boolean; `sensor.gomow_decision_trace` supplies factor snapshots, gate results, input freshness/validity, ordered blocking reasons, model/config versions, and trace timestamp. A final false result never hides additional failed gates. | Active | Trace volume/HA attribute limits make the contract unusable, or shadow operation proves a clearer representation is needed. |
| DEC-042 | Audit logging | Use HA system logs and Logbook only for meaningful decision, health/recovery, hold, and job-lifecycle transitions. No log for an unchanged evaluation or secondary-reason-only change. The decision trace remains the detailed diagnostic source; logs are concise navigational audit entries. | Active | Shadow use finds important transitions absent or normal model operation too noisy. |
| DEC-043 | Active-job interlock and resume | A confirmed continuous gate failure during a GoMow-owned job requests one dock action. Automatic NaviMower Resume is allowed only for that recorded GoMow gate abort after retained-task evidence, fresh healthy inputs, all continuous gates, resume-clear dwell, no manual/native/error ambiguity, and a bounded single attempt; it never recreates a job or retries indefinitely. | Active | Assisted i210 validation disproves retained-task Resume semantics or shadow evidence shows unsafe/unhelpful behaviour. |
| DEC-044 | Mowing frequency after interruption | Verified completion remains the successful-mow evidence timestamp. Next eligibility uses the hybrid maximum of the accepted job's nominal due time (`accepted_start_at + planned_interval_days`) and a minimum post-completion rest, rather than restarting the entire interval at late completion. | Active | Shadow data shows the anchor or rest floor causes systematically premature/late all-zone jobs. |

---
