# GoMow Verification and Test Plan

## Purpose

GoMow combines several PyScript models, live Home Assistant entities, and eventually a mower command lifecycle. A local defect can otherwise become a plausible-looking but wrong mowing recommendation. This plan makes verification explicit at four distinct levels:

1. **software correctness** — does a component implement its stated behaviour?
2. **model and configuration behaviour** — does the decision change sensibly at known boundaries and under bad data?
3. **integration correctness** — do the PyScripts, HA entities, persistence, and public boolean contracts work together?
4. **decision quality** — does a recommendation match observed lawn conditions and actual job outcomes?

The first three are engineering checks. The fourth is calibration. None replaces the mower's independent built-in protections.

## Test policy

- Every new production behaviour follows **RED → GREEN → REFACTOR**: first add a focused failing test, observe its expected failure, implement the minimum code, then run the full suite.
- A defect fix includes a regression test that first reproduces the defect.
- Tests must be deterministic: freeze time, use fixtures, and never depend on a live sensor value.
- Public contracts are tested by their observable entity state/attributes, not private helper internals.
- A repository test passing does not mean a live HA deployment is complete. Deployment verification is recorded separately.
- Tests must not call a mower-control service unless a separately approved, assisted live command test explicitly says so.

## Verification layers

### L1 — Pure unit tests

**Location:** `tests/test_*_math.py`

Test pure functions without HA, including:

- ET unit conversion, physical bounds, radiation edge cases, and non-finite inputs;
- wetness ceiling, elapsed-time clamps, proportional component decay, and restart attribution;
- rain-delta/reset/deduplication logic;
- dew point/intensity bounds and feature-disabled behaviour;
- growth response curves, smoothing, and `min()` limiter selection;
- hysteresis polarity and minimum dry-duration arithmetic.

Required cases for every numerical model: ordinary value, zero, threshold boundary, just either side of a boundary, invalid/NaN/infinite value, stale interval, and clock/restart discontinuity.

### L2 — PyScript runtime-contract tests

**Location:** `tests/test_pyscript_*_contract.py`

Load deployable PyScript with minimal `state`, `log`, decorators, time, and service doubles. Verify the contract visible to HA:

- expected entity IDs are centrally configured and public entities use expected units/attributes;
- module import boundaries work without reliance on top-level global/load order;
- persistence restore produces the correct public diagnostic state;
- invalid, unavailable, or stale source data pauses the affected model rather than emitting a misleading fresh result;
- a later valid sample creates a new baseline rather than applying decay across an unknown interval;
- feature switches, manual holds, and uncalibrated thresholds fail predictably;
- no wetness/growth/decision module can call a mower-control service;
- startup/reload enters recovery and has no automatic-dispatch path until its explicit recovery conditions are met.

### L3 — Decision-pipeline integration tests

**Location:** `tests/integration/` with version-controlled, anonymised fixtures.

Exercise multiple real modules together using sequences of timestamped input events. These tests use captured or hand-authored fixtures, never live HA.

Core scenarios:

| Scenario | Expected observable result |
|---|---|
| Dry weather sequence | ET dries the wetness model only while inputs remain valid; `ground_dry` changes only after configured hysteresis and dwell criteria. |
| Rain event followed by dry-down | Measured rain is added once; duplicate/replayed samples do not add water twice; later ET reduces the score. |
| Rain-source reset | Counter/window reset is recognised, not interpreted as negative or massive rain. |
| Dew-favourable night | Dew contribution occurs only if explicitly enabled and all gates are true; active rain does not double-count it. |
| Missing/stale source | Affected decision path becomes unavailable/not-ready; no fabricated dry or mow-due result appears. |
| Conflicting inputs | Public diagnostics identify the gating reason and input-health result. |
| Growth limiter | Air, soil temperature, and moisture response combine via the documented `min()` rule. |
| Hysteresis chatter | Oscillation near thresholds does not rapidly toggle `ground_dry` or create dispatch churn. |
| Restart/reload before inputs restore | Automatic dispatch remains inhibited; public diagnostics identify recovery/input freshness rather than emitting a false ready decision. |
| Restart/reload with wetness state | Persisted total is restored as unattributed; no drying is applied across the unknown interval until a valid ET baseline exists. |
| Restart/reload during rain | The deduplication checkpoint restores, so the next received sample is neither silently lost nor counted twice. |
| Restart/reload after `START_REQUESTED` | The persisted job is reconciled with fresh mower state; GoMow never retries the start command automatically. |
| Restart/reload while mowing/returning | The job monitor resumes observation only; its target-zone list and start identity remain immutable. |
| Restart/reload after terminal state | Completion is verified only from evidence fresh relative to the persisted job, never from restored state alone. |
| Persistence missing/corrupt | The affected model/job becomes `recovery_failed`/not-ready, preserves no invented history, and requires a manual resolution or new valid baseline. |
| Pending-job lifecycle | Start acknowledgement, normal completion, interruption, cancellation, and timeout are classified without advancing the canonical full-mow timestamp incorrectly. |

### L4 — Home Assistant deployment and live-contract checks

These checks occur only for an explicitly requested deployment, and begin read-only where possible:

1. Confirm repository revision, clean working tree, expected source list, and test results.
2. Back up each live GoMow file that will be replaced.
3. Verify actual entity IDs, units, availability, freshness, and update semantics against `gomow_config.py`.
4. Deploy only the reviewed file set—including shared modules—then reload PyScript.
5. Confirm expected public entities/services appear and logs contain no syntax/import/runtime errors.
6. Confirm legacy files are not mixed with a module-based revision.
7. Keep dispatch disabled unless the user explicitly chooses otherwise.

A live entity mismatch is a failed deployment check, not a reason to guess a substitute entity ID.

### L5 — Shadow and assisted decision-quality checks

Shadow mode records GoMow's recommendation beside observed lawn conditions. Assisted mode may be used to check command tracking for a real job. Record findings in:

- `integration-observations.md` for raw HA/mower facts;
- `calibration-and-validation.md` for threshold/model changes and supporting observation;
- `workboard.md` for task completion.

Calibration asks: **“Would this recommendation have been sensible?”** It does not attempt to retest Navimow's built-in safety features.

## Change-specific minimum evidence

| Change type | Minimum verification before commit | Additional evidence before a live deployment |
|---|---|---|
| Pure math/helper | New failing unit test, targeted green test, full suite | None unless consumed by deployed code. |
| PyScript source/module | L1 + L2 tests, syntax compilation, static no-control-call scan | L4 import/entity/log checks. |
| Configuration/entity mapping | Contract test plus fixture update | Read actual live state/attributes and freshness; do not infer names. |
| Threshold/model tuning | Boundary/replay test update | Recorded real-world evidence and calibration-log entry. |
| Rain/growth integration | L1–L3 scenario coverage | Fresh live-source semantics confirmed. |
| Dispatcher/job tracking | L1–L3 lifecycle coverage | Explicit user-approved assisted command observation. |

## Standard commands

```bash
# Full deterministic suite
python3 -m unittest discover -s tests -v

# Syntax verification
python3 -m py_compile $(git ls-files 'src/**/*.py' 'tests/**/*.py')

# Repository whitespace verification
git diff --check
```

Add a single command for the integration fixture suite when `tests/integration/` is introduced; it must remain runnable without Home Assistant.

## Test inventory and status

| Area | Current coverage | Next addition |
|---|---|---|
| Central configuration | Contract tests for common entity IDs, wetness ceiling, uncalibrated hysteresis, ET cadence, and disabled/unbound optional soil capabilities | Add every new configured source/helper ID and feature-enabled health rule. |
| ET/wetness/dew baseline | Pure math plus PyScript contracts: prior-rate integration, invalid ET fail-closed reset, twilight radiation, disabled dew, and restart attribution | Add measured rain sequence tests. |
| Rain accumulation | Not implemented | L1 counter/window reset and duplicate-event tests; L3 wet-to-dry replay fixture. |
| `ground_dry` | Not implemented | Hysteresis/dwell boundaries and stale-input contract. |
| Growth | Not implemented | Response-curve and global-limiter tests. |
| Dispatcher/job tracking | Not implemented | Pending-job lifecycle and HA-restart recovery matrix before any live assisted command. |

## Exit criteria for a workboard item

A task is **Done** only when its stated acceptance criteria, associated automated tests, and any required real-world evidence are recorded. “It seemed to work once” is not an exit criterion.
