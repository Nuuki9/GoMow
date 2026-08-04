# GoMow Repository Instructions

## Safety

- This repository controls a real mower. Default to no action; fail closed on missing, stale, invalid, or ambiguous data.
- Do not enable unattended automatic starts, deploy live changes, alter a real mower schedule, or call a mower-control service unless the user explicitly requests that exact action.
- Preserve a shadow-mode then assisted-mode rollout. Do not skip completion verification.
- Do not put secrets, tokens, `.storage` content, or personal data in Git.

## Architecture

- Implement decision logic in PyScript; retain existing integrations for device protocol access.
- Keep source entity IDs and tunable values as named constants at the top of each deployable file.
- Keep measurement, continuous models, booleans, and dispatch separate. Downstream consumers use public boolean contracts, not raw scores.
- Maintain a fail-closed input-health gate and diagnostic attributes.
- Preserve the one dispatcher / explicit pending-job state-machine model.

## Change discipline

- Read `docs/architecture.md`, `docs/decisions.md`, and the relevant validation evidence before changing implementation.
- Update the decision register when an agreed architectural assumption changes.
- Update calibration/validation records after real-world observations change a threshold.
- Use scenario-based validation before live deployment.
- Inspect Git status and diffs before committing; never claim a push or deployment succeeded without verifying it.
