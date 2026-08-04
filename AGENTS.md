# GoMow Repository Instructions

## Safety

- This repository controls a real mower. Default to no action; fail closed on missing, stale, invalid, or ambiguous data.
- Do not enable unattended automatic starts, deploy live changes, alter a real mower schedule, or call a mower-control service unless the user explicitly requests that exact action.
- Preserve a shadow-mode then assisted-mode rollout. Do not skip completion verification.
- Do not put secrets, tokens, `.storage` content, or personal data in Git.

## Architecture

- Implement decision logic in PyScript; retain existing integrations for device protocol access.
- Keep installation-specific entity IDs and intentionally tunable values as named constants in `src/pyscript/modules/gomow_config.py`. Deployable scripts explicitly import only the constants they use. Keep mathematical invariants and implementation-private constants local to the owning file; keep day-to-day operator values in Home Assistant UI helpers, whose entity IDs are centrally configured.
- Keep measurement, continuous models, booleans, and dispatch separate. Downstream consumers use public boolean contracts, not raw scores.
- Maintain a fail-closed input-health gate and diagnostic attributes.
- Preserve the one dispatcher / explicit pending-job state-machine model.

## Change discipline

- Read `docs/architecture.md`, `docs/decisions.md`, and the relevant validation evidence before changing implementation.
- Update the decision register when an agreed architectural assumption changes.
- Update calibration/validation records after real-world observations change a threshold.
- When `gomow_config` or a shared module changes, reload the complete GoMow PyScript set and verify the public diagnostics before any later live use.
- Use scenario-based validation before live deployment.
- Inspect Git status and diffs before committing; never claim a push or deployment succeeded without verifying it.
