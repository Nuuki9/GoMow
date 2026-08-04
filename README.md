# GoMow

GoMow is a Home Assistant-based decision system for a Segway Navimow i210 LiDAR Pro. It determines whether mowing is operationally suitable now, whether mowing is due, and—initially—dispatches an all-enabled-zone job only when its decision and command-integrity conditions are satisfied.

> **Control boundary:** GoMow only decides whether to request a mow, much like a richer calendar schedule. It does not modify, replace, or bypass Navimow/NaviMower firmware, hardware, rain, collision, lift, boundary, battery, or other built-in protections. Shadow and assisted modes are decision-quality and integration checks; unattended operation remains an explicit user-controlled setting, not something enabled by a repository change.

## Status

Architecture agreed. The three supplied wetness-model scripts have been reviewed and imported as a **repository-only baseline**. Read-only discovery subsequently confirmed that Home Assistant already has pre-existing legacy versions in `/config/pyscript/`; the reviewed repository layout has not been copied or reloaded there.

## Documentation

- [Architecture](docs/architecture.md) — models, gates, state machine, and public entity contracts.
- [Decision register](docs/decisions.md) — agreed assumptions, decisions, status, and revisit triggers.
- [Implementation plan](docs/implementation-plan.md) — staged build and intended scope.
- [Workboard](docs/workboard.md) — current executable tasks, status, dependencies, and acceptance criteria.
- [Verification and test plan](docs/test-plan.md) — deterministic unit, contract, pipeline, deployment, and decision-quality checks.
- [Integration observations](docs/integration-observations.md) — real NaviMower, Ecowitt, and HA entity evidence.
- [Calibration and validation](docs/calibration-and-validation.md) — observed data, threshold tuning, and test results.
- [Initial PyScript review](docs/pyscript-review.md) — review findings, imported baseline, and explicit remaining gaps.
- [Open questions](docs/open-questions.md) — evidence required before later stages are enabled.
- [References](docs/references.md) — cited scientific, product, integration, and HA sources.

## Intended layout

```text
src/pyscript/            # reviewed deployable PyScript files
src/pyscript/modules/    # shared `gomow_config` and pure testable helpers
tests/                   # deterministic scenarios and fixtures
deploy/                  # explicit deployment/verification tooling; not populated yet
```

## Working rules

- Existing device integrations remain responsible for device protocols: **NaviMower** for mower control and **Ecowitt** for the WH52.
- GoMow is the policy/orchestration layer, implemented primarily in PyScript with thin HA UI helpers and notifications at the edges.
- Never commit secrets, Home Assistant `.storage`, database files, or raw credentials.
- Do not deploy or enable automatic mowing as part of a documentation or code change without explicit approval and verification.
