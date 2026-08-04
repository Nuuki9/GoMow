# Changelog

All notable project decisions and implementation changes are recorded here.

## Unreleased

### Added

- Initial repository documentation baseline.
- Agreed architecture, decision register, implementation plan, integration-observation log, calibration log, and references.
- Explicit safety and repository working rules.
- Reviewed, repository-only PyScript baseline for reference ET, persisted surface-wetness decay, and gated modelled dew.
- Central `gomow_config` module, shared wetness modules, and deterministic unit/runtime-contract tests.
- ET validity/freshness safeguards, hourly recalculation, twilight radiation correction, and explicit unattributed restored wetness following independent review.
- Clarified GoMow as a decision-quality scheduling layer that leaves built-in mower protections untouched; calibration now measures recommendation quality and command tracking.
