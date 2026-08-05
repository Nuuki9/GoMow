# GoMow Workboard

This is the canonical **execution tracker** for GoMow. It complements, rather than duplicates, the [implementation plan](implementation-plan.md):

- **Implementation plan**: stable architecture-level sequence and intended scope.
- **Workboard**: current actionable items, acceptance criteria, dependencies, and status.
- **Calibration log**: real-world observations and tuning evidence; it is not a task list.

Use only these states: **Not started**, **In progress**, **Blocked**, **Done**, or **Deferred**. A repository code change is not a Home Assistant deployment; mark those separately.

## Current delivery state

| Workstream | Status | Completion / next evidence |
|---|---|---|
| Architecture and decision register | Done | DEC-001–042 recorded; device-protection, decision-quality, verification, HA-recovery, tuning, capability-configuration, explainability, and audit-noise boundaries clarified. |
| Central PyScript configuration | Done in repository | `modules/gomow_config.py` and contract tests exist; core mandatory, optional/unbound, and feature-enabled soil capabilities are explicit. Live entity mapping remains pending. |
| Initial ET / wetness / dew baseline | Done in repository | Reviewed scripts and 15 deterministic tests; no HA deployment. |
| Verification plan | Done | Layered test plan defined in `test-plan.md`; future behaviour changes are test-first. |
| Tuning guide | Done | Evidence-led troubleshooting and calibration workflow defined in `tuning-guide.md`; parameter changes remain central, reversible, and test-backed. |
| Live Home Assistant discovery | Done | HA Core is running; PyScript and NaviMower are installed. `/config/pyscript/` contains three pre-existing legacy wetness scripts but not the reviewed repository module layout. No files were changed. |
| Stage 0 command lifecycle/tracking | In progress | Target-relative verifier and initial recovery branches are tested; implement persisted pending-job/audit/hold and HA runtime contracts without any dispatch call. |
| Stage 1 measured rain and `ground_dry` | Not started | Netatmo rolling-hour source selection is evidenced; implement timestamp-deduplicated accumulation and calibrated boolean gate. |
| WH52 onboarding | Blocked | Hardware/gateway firmware and actual HA entities required. |
| Growth model | Not started | Depends on validated temperature/soil-moisture inputs. |
| Automatic dispatch | Not started | Explicitly user-enabled only after useful decision-quality and command-tracking evidence. |

## Active tasks

| ID | Task | Status | Acceptance criteria | Dependencies |
|---|---|---|---|---|
| D-01 | Discover live HA / PyScript deployment context read-only. | Done | Recorded HA/PyScript runtime and the safe repository-to-HA deployment boundary in `integration-observations.md`; no live configuration changed. | None |
| D-02 | Record NaviMower entity IDs, state values, map/zone IDs, and completion semantics. | Done | Native Side `7` + Slope `6` run observed from start to dock: explicit task-zone list, 100% selected-task progress, two fresh per-zone completions, map completion unchanged, and unstable integration cycle IDs recorded. | D-01 |
| D-03 | Record Netatmo rain entity IDs, units, timestamps, and update/deduplication semantics. | Done | `..._rain_last_hour` was observed changing after rain and returning to `0`; bind it as a rolling-hour measured source with timestamp/dedup/reset handling. Direct `..._rain` and `binary_sensor.is_it_raining` are stale and excluded. | D-01 |
| I-01 | Implement Stage 0 input-health, manual hold, audit record, pending-job state model, and reboot reconciliation. | In progress | Unit-tested repository implementation: recovery blocks automatic dispatch until fresh inputs/job reconciliation; no dispatch service call. Target-relative terminal verification and initial recovery branches are implemented; persisted state, audit/hold, and HA contract remain. | D-02 |
| I-02 | Implement measured rain accumulation. | Not started | Unit-tested, handles stale/duplicate samples and exposes diagnostics. | D-03 |
| I-03 | Implement `binary_sensor.ground_dry` hysteresis and minimum dry duration. | Not started | Thresholds remain uncalibrated until observations are recorded; boolean contract is tested. | I-02 |

## Update protocol

1. Move an item only when its acceptance criteria are evidenced.
2. Link real-world observations in `integration-observations.md` and calibration changes in `calibration-and-validation.md`.
3. Keep design decisions in `decisions.md`; do not turn this document into an architecture narrative.
4. Record repository and Home Assistant deployment status independently.
