# Implementation Plan

## 12. Implementation Sequence

### Stage 0 — Configuration and operational foundation

- Establish the central `gomow_config` module before importing any deployable PyScript. It owns installation-specific entity IDs and intentionally tunable values; scripts import only their required constants. A change to it or any shared module requires a full GoMow PyScript reload and diagnostic verification.
- Establish helpers, `mower_inputs_healthy`, manual hold, audit log, pending-job persistence, and dispatcher state machine.
- Enable NaviMower per-zone coverage and completion entities needed for verification.
- Run no automatic starts.

### Stage 1 — Complete and validate wetness model

- Keep existing reference ET and score engine.
- Implement fresh/deduplicated rain accumulation.
- Refactor dew into the conservative gated heuristic.
- Implement correctly polarised `ground_dry` hysteresis plus minimum dry duration.
- Run wet/dry shadow observation and tune only against actual lawn condition.

### Stage 2 — WH52 onboarding and calibration

- Verify gateway firmware, WH52 pairing, and Home Assistant entities for moisture, soil temperature, EC, and battery.
- Install at representative turf root depth using a pilot hole; avoid roots, hard objects, irrigation outflow, and unusual drainage locations.
- Calibrate moisture dry/wet references and observe stabilization after installation.
- Use moisture only as a diagnostic initially; then enable it as the growth water limiter.
- Add soil temperature only after adequate trend history exists.
- Retain EC as diagnostics only.

### Stage 3 — Growth model shadow mode

- Implement daily response calculation plus 7-day smoothing.
- Begin with air-temperature plus validated soil-moisture responses.
- Add soil-root-temperature response once validated.
- Compare derived intervals against visible grass growth and completed mowing outcomes.

### Stage 4 — Assisted then unattended all-zone operation

- Validate successful completion, rain interruption, manual stop, failed start, and 95–99% practical-completion cases.
- Use assisted mode first.
- Enable automatic all-zone starts only after tracking is reliable.

### Deferred Phase 2

- Selected-zone automatic scheduling via static zone policies.
- Forecast-based start optimisation.
- Direct leaf-wetness hardware if the modelled-dew approach proves insufficient.
- Cut-height automation only after NaviMower exposes safe write support.

---

---

This plan does not authorise unattended mower starts. The mandatory progression is **shadow mode → assisted mode → explicitly approved unattended operation**.
