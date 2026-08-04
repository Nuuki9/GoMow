# Changelog

All notable project decisions and implementation changes are recorded here.

## Unreleased

- Add DEC-041 and the canonical `binary_sensor.mow_recommended` / `sensor.gomow_decision_trace` explainability contract: retain all concurrent blocks, expose stable reason codes, gates, factor snapshots, versions, and evaluation time.
- Add a pure, deterministic decision-trace builder and test that stale input remains the primary reason without hiding simultaneous wetness failure.

### Added

- Initial repository documentation baseline.
- Agreed architecture, decision register, implementation plan, integration-observation log, calibration log, and references.
- Explicit safety and repository working rules.
- Reviewed, repository-only PyScript baseline for reference ET, persisted surface-wetness decay, and gated modelled dew.
- Central `gomow_config` module, shared wetness modules, and deterministic unit/runtime-contract tests.
- ET validity/freshness safeguards, hourly recalculation, twilight radiation correction, and explicit unattributed restored wetness following independent review.
- Clarified GoMow as a decision-quality scheduling layer that leaves built-in mower protections untouched; calibration now measures recommendation quality and command tracking.
- Added a layered verification/test plan (DEC-037): deterministic unit, PyScript-contract, integration replay, deployment, and live decision-quality checks.
- Added explicit HA/PyScript restart-recovery requirements and test matrix (DEC-038): fresh-input recovery, persisted-state reconciliation, and no automatic command replay.
- Added evidence-led tuning governance and scenario guide (DEC-039), covering model diagnosis, one-at-a-time centrally configured changes, and test-backed calibration.
- Made the soil-sensor architecture capability-based: WH51 moisture-only is fully supported; WH52 soil temperature is an optional validated growth limiter and EC stays diagnostic.
- Separated core mandatory entities from optional/unbound and feature-enabled soil capabilities (DEC-040), allowing soil temperature from WH52, WN34S, or future supported hardware.
