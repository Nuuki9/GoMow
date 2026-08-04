# GoMow

GoMow is a conservative, Home Assistant-based decision system for a Segway Navimow i210 LiDAR Pro. It determines whether mowing is suitable now, whether mowing is due, and—initially—dispatches an all-enabled-zone job only after verifiable completion and safety conditions are satisfied.

> **Safety boundary:** GoMow must remain in shadow mode, then assisted mode, until the documented validation criteria are met. Nothing in this repository authorises an unattended start by itself.

## Status

Architecture agreed. Existing wetness-model PyScript work has not yet been imported or modified in this repository.

## Documentation

- [Architecture](docs/architecture.md) — models, gates, state machine, and public entity contracts.
- [Decision register](docs/decisions.md) — agreed assumptions, decisions, status, and revisit triggers.
- [Implementation plan](docs/implementation-plan.md) — staged build and safe rollout process.
- [Integration observations](docs/integration-observations.md) — real NaviMower, Ecowitt, and HA entity evidence.
- [Calibration and validation](docs/calibration-and-validation.md) — observed data, threshold tuning, and test results.
- [Open questions](docs/open-questions.md) — evidence required before later stages are enabled.
- [References](docs/references.md) — cited scientific, product, integration, and HA sources.

## Intended layout

```text
src/pyscript/    # reviewed deployable PyScript files; not populated yet
tests/           # deterministic scenarios and fixtures; not populated yet
deploy/          # explicit deployment/verification tooling; not populated yet
```

## Working rules

- Existing device integrations remain responsible for device protocols: **NaviMower** for mower control and **Ecowitt** for the WH52.
- GoMow is the policy/orchestration layer, implemented primarily in PyScript with thin HA UI helpers and notifications at the edges.
- Never commit secrets, Home Assistant `.storage`, database files, or raw credentials.
- Do not deploy or enable automatic mowing as part of a documentation or code change without explicit approval and verification.
