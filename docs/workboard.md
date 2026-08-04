# GoMow Workboard

This is the canonical **execution tracker** for GoMow. It complements, rather than duplicates, the [implementation plan](implementation-plan.md):

- **Implementation plan**: stable architecture-level sequence and intended scope.
- **Workboard**: current actionable items, acceptance criteria, dependencies, and status.
- **Calibration log**: real-world observations and tuning evidence; it is not a task list.

Use only these states: **Not started**, **In progress**, **Blocked**, **Done**, or **Deferred**. A repository code change is not a Home Assistant deployment; mark those separately.

## Current delivery state

| Workstream | Status | Completion / next evidence |
|---|---|---|
| Architecture and decision register | Done | DEC-001–037 recorded; device-protection, decision-quality, and verification boundaries clarified. |
| Central PyScript configuration | Done in repository | `modules/gomow_config.py` and contract tests exist; live entity mapping remains pending. |
| Initial ET / wetness / dew baseline | Done in repository | Reviewed scripts and 15 deterministic tests; no HA deployment. |
| Verification plan | Done | Layered test plan defined in `test-plan.md`; future behaviour changes are test-first. |
| Live Home Assistant discovery | Done | HA Core is running; PyScript and NaviMower are installed. `/config/pyscript/` contains three pre-existing legacy wetness scripts but not the reviewed repository module layout. No files were changed. |
| Stage 0 command lifecycle/tracking | Not started | Define real NaviMower state/entity mapping and then implement pending-job/audit/hold layer. |
| Stage 1 measured rain and `ground_dry` | Not started | Map Netatmo source semantics first; then implement deduplicated accumulation and calibrated boolean gate. |
| WH52 onboarding | Blocked | Hardware/gateway firmware and actual HA entities required. |
| Growth model | Not started | Depends on validated temperature/soil-moisture inputs. |
| Automatic dispatch | Not started | Explicitly user-enabled only after useful decision-quality and command-tracking evidence. |

## Active tasks

| ID | Task | Status | Acceptance criteria | Dependencies |
|---|---|---|---|---|
| D-01 | Discover live HA / PyScript deployment context read-only. | Done | Recorded HA/PyScript runtime and the safe repository-to-HA deployment boundary in `integration-observations.md`; no live configuration changed. | None |
| D-02 | Record NaviMower entity IDs, state values, map/zone IDs, and completion semantics. | In progress | Live mower entity identified; populate remaining map/zone/completion evidence without issuing a control action. | D-01 |
| D-03 | Record Netatmo rain entity IDs, units, timestamps, and update/deduplication semantics. | In progress | Candidate hourly entity is identified; observe a fresh update/reset before choosing it for `rain_accumulation.py`. | D-01 |
| I-01 | Implement Stage 0 input-health, manual hold, audit record, and pending-job state model. | Not started | Unit-tested repository implementation with no dispatch service call. | D-02 |
| I-02 | Implement measured rain accumulation. | Not started | Unit-tested, handles stale/duplicate samples and exposes diagnostics. | D-03 |
| I-03 | Implement `binary_sensor.ground_dry` hysteresis and minimum dry duration. | Not started | Thresholds remain uncalibrated until observations are recorded; boolean contract is tested. | I-02 |

## Update protocol

1. Move an item only when its acceptance criteria are evidenced.
2. Link real-world observations in `integration-observations.md` and calibration changes in `calibration-and-validation.md`.
3. Keep design decisions in `decisions.md`; do not turn this document into an architecture narrative.
4. Record repository and Home Assistant deployment status independently.
