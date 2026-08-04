# GoMow Tuning Guide

## Purpose

GoMow's models are deliberately simple, observable approximations of lawn conditions. Tuning is how we align them with the actual lawn **after** the input data, model behaviour, and recommendation have been observed together.

This guide is for situations such as:

> “GoMow recommended mowing while the grass was still wet following rainfall.”

It explains the intended model behaviour, evidence to collect, likely causes, and the smallest appropriate adjustment. Tuning aims for a more sensible mowing recommendation; it does not change, disable, or compensate for Navimow/NaviMower's own protections.

## Rules for every tuning change

1. **Fix an input/integration fault before changing a model value.** A missed rain event, stale sensor, incorrect unit, duplicate sample, or failed recovery is not a calibration problem.
2. **Record evidence first.** Capture the time, observed lawn condition, GoMow public entities/diagnostics, relevant source values and ages, and the resulting mower/job outcome.
3. **Change one intentional parameter at a time.** Preserve the prior value, rationale, expected directional effect, and observation period in `calibration-and-validation.md`.
4. **Make the adjustment in `gomow_config.py` or the relevant HA helper only.** Do not create per-script hidden overrides.
5. **Add or amend a deterministic boundary/replay test before committing a behavioural change.** A calibration change should be reproducible from its recorded scenario.
6. **Use shadow or assisted evidence before enabling an altered automatic policy.** Repository changes never enable automatic dispatch by themselves.
7. **Do not tune around missing data.** An unavailable, invalid, stale, uncalibrated, or recovering input should leave the decision not-ready rather than lead to a guessed result.

## Observation record

Use this compact record in `calibration-and-validation.md` for every meaningful mismatch:

```text
Observed at (UTC/local):
Scenario / actual lawn condition:
What GoMow recommended or did:
Expected sensible recommendation:
Ground-dry state, score, rain/dew/unattributed components, reason:
ET validity/rate and source input ages:
Rain source value, event timestamp, deduplication diagnostics:
Growth/due diagnostics (if relevant):
Mower status and pending-job/audit state (if relevant):
Photos/notes (optional):
Root-cause hypothesis:
Change made (old → new):
Expected directional effect:
Replay/unit test added or updated:
Review date and result:
```

## Tuning order

Apply this order; it prevents a poor sensor/integration assumption becoming a permanent model bias.

1. **Source contract:** right entity, units, timestamps, update/reset semantics, freshness, and availability.
2. **Pipeline correctness:** event deduplication, persistence/recovery, feature switches, state transitions, and diagnostic reason.
3. **Physical/model assumptions:** wind shelter factor, rain representation, conservative dew gates, and later soil response curves.
4. **Decision thresholds/dwell:** `ground_dry` hysteresis and minimum dry duration.
5. **Scheduling policy:** growth-to-interval mapping, elapsed-time policy, and later static zone cadence multipliers.

Never start at step 4 or 5 when steps 1–3 have not been verified.

## Scenario guide

### 1. Mowing was recommended while grass was still wet after rainfall

**Intended behaviour**

A fresh measured rain event should increase `sensor.ground_wetness_score`. `binary_sensor.ground_dry` should remain off until the wetness score dries below the calibrated dry-entry threshold for the configured dwell duration. ET only dries the model while its inputs are valid and fresh.

**Check before tuning**

- Did the selected Netatmo rain entity change for the actual event, with the expected unit and timestamp?
- Did `rain_accumulation.py` record one positive addition, rather than reject it as stale/duplicate or miss it following a counter/window reset?
- Was the rain event within the model's freshness window?
- Did ET/wetness diagnostics show `input_valid: true` throughout the following dry-down?
- Was the grass actually surface-wet, rather than soil-moist but dry at the leaf/grass surface?

**Likely correction**

| Evidence | Correct response |
|---|---|
| Rain event absent/wrong/stale/duplicated | Repair mapping or accumulation logic; do **not** alter thresholds. |
| Score stayed low despite a confirmed added rain event | Review rain-event representation/ceiling with a replay fixture before changing a parameter. |
| Score reflects rain but `ground_dry` turned on too early | Lower `DRY_ENTER_THRESHOLD_MM` so a lower wetness score is required before dry entry. Keep `WET_ENTER_THRESHOLD_MM > DRY_ENTER_THRESHOLD_MM`. |
| A dry state was not revoked promptly as rain began | Review event freshness/deduplication first; only then consider lowering `WET_ENTER_THRESHOLD_MM`, while retaining it above `DRY_ENTER_THRESHOLD_MM`. |
| Score dried much faster than visibly observed under otherwise valid inputs | Re-check weather source exposure and `WIND_SHELTER_FACTOR`; a lower factor reduces the modelled drying demand. Change only after a recorded dry-down replay. |

Do not compensate by changing NaviMower's native rain settings; those are outside GoMow's boundary.

### 2. GoMow kept the lawn wet/not-ready long after it was visibly dry

**Intended behaviour**

The score should decay using ET only over valid intervals. Hysteresis and a minimum dry duration prevent noisy flips but should not create an unexplained permanent hold.

**Check before tuning**

- Is a required input unavailable/stale, leaving `mower_inputs_healthy` off? That is an input-health issue, not excessive caution.
- Is the score dominated by `unattributed_score_mm` after a reboot? Confirm a valid new ET baseline has since been established.
- Are rain/dew additions continuing unexpectedly? Check their reasons and timestamps.
- Is the observed surface dry at the planned cutting time, not only at a different time/exposure?

**Likely correction**

| Evidence | Correct response |
|---|---|
| Input-health/recovery block | Fix data availability/freshness or recovery state; never tune around it. |
| Rain/dew is repeatedly added without matching conditions | Correct the source/model rule and add a regression fixture. |
| Score is realistic but dry state enters later than observations | Raise `DRY_ENTER_THRESHOLD_MM` modestly, then test the boundary replay. |
| Wet state is asserted too readily for minor additions | Raise `WET_ENTER_THRESHOLD_MM`, retaining `WET_ENTER_THRESHOLD_MM > DRY_ENTER_THRESHOLD_MM`. |
| Score remains high because drying demand is persistently too weak | Verify sensor units/exposure before considering a carefully documented increase to `WIND_SHELTER_FACTOR`. |

Do not reduce `MINIMUM_DRY_DURATION_MINUTES` until the score and hysteresis already match real observations; dwell is anti-chatter, not a substitute for wetness calibration.

### 3. Dew appears to make recommendations too conservative or not conservative enough

**Intended behaviour**

Modelled dew is disabled initially (`ENABLE_MODELLED_DEW = False`). If later enabled, it may add wetness only under all documented gates: no active rain, sufficient humidity, low wind, suitable sun elevation, and above the frost floor.

**Check before tuning**

- Confirm whether the feature is enabled at all.
- Confirm that active rain is not the true explanation.
- Compare actual visible dew/grass dampness at dawn with the model's dew diagnostics over several nights.

**Likely correction**

- Repeated false dew additions: correct the gating condition or keep the feature disabled; do not merely shrink the amount.
- Magnitude consistently wrong with gates otherwise correct: adjust `TARGET_DEW_PER_NIGHT_MM` in small, evidence-supported steps.
- Only borderline dawn recommendations disagree: use wetness hysteresis/dwell evidence before adjusting the dew model.

### 4. GoMow recommends mowing too often or not often enough as growth changes

**Intended behaviour**

Growth is a global decision input. Air temperature drives shoot response; later soil temperature and measured soil moisture act as limiting signals. It does not infer local per-zone microclimates in Phase 1.

**Check before tuning**

- Is a mow actually due according to the canonical successful-full-mow timestamp, rather than `last_map_mowed`?
- Did the previous job complete and update tracking correctly?
- Is the lawn's apparent need a whole-lawn condition or only a single zone?
- Once available, are WH52 values representative, fresh, and calibrated?

**Likely correction**

- Incorrect job history: repair tracking, not growth parameters.
- A whole-lawn systematic cadence mismatch over several cycles: adjust the documented growth-to-interval policy using replayed observations.
- One zone consistently differs: retain the global environmental model; record evidence for the later static zone-policy revisit rather than adding a per-zone weather model.
- WH52 unavailable/uncalibrated: leave the soil limiter out of the active decision rather than inventing a substitute value.

### 5. Decision is unexpectedly blocked even though conditions look suitable

**Intended behaviour**

`binary_sensor.mower_inputs_healthy` is a visible decision-integrity prerequisite. Its off state must name the failed entity/reason and prevents a schedule-like command based on unknown inputs.

**Check before tuning**

- Read the failed-input list, source ages, and recovery state.
- Check for a manual hold, disabled automation policy, start window, mower status, or an unresolved pending job.
- After HA restart/reload, confirm all required inputs have returned fresh and the recovery audit completed.

**Likely correction**

Fix the named health/recovery/dispatch condition. Do not weaken freshness checks or make a silent bypass; if the operational policy itself needs changing, record it as a separately reviewed decision.

### 6. The system behaved unexpectedly after a Home Assistant reboot/reload

**Intended behaviour**

Recovery is explicit: models restore truthfully, require fresh inputs, reconcile a pending job against fresh mower evidence, and never replay a start command automatically.

**Check before tuning**

- Recovery audit state and reason;
- wetness restoration/ET baseline diagnostic;
- rain deduplication checkpoint;
- persisted pending-job identity, target zones, and observed mower state.

**Likely correction**

This is normally an implementation/recovery defect, not a tuning matter. Add a failing recovery fixture first; only adjust an explicit freshness or timeout policy once the persistence/reconciliation behaviour is proven correct.

## Parameter reference

| Parameter | Directional effect | Use only when |
|---|---|---|
| `WIND_SHELTER_FACTOR` | Lower → slower modelled ET dry-down; higher → faster. | Weather exposure/ET dry-down mismatch is confirmed over several valid observations. |
| `DRY_ENTER_THRESHOLD_MM` | Lower → harder/slower to become dry; higher → easier/faster. | Score is sound but dry-entry timing is systematically wrong. |
| `WET_ENTER_THRESHOLD_MM` | Lower → easier/faster to become wet; higher → harder/slower. Must remain greater than dry-entry threshold. | Score additions are sound but wet-state re-entry is systematically wrong. |
| `MINIMUM_DRY_DURATION_MINUTES` | Higher → longer stable-dry requirement; lower → shorter. | Hysteresis is already calibrated and evidence shows only the dwell period is wrong. |
| `TARGET_DEW_PER_NIGHT_MM` | Higher/lower → more/less modelled dew, when enabled. | Dew gates are validated and the error is magnitude, not event detection. |
| Growth response / interval policy | Higher demand response → shorter target intervals; lower → longer. | Several whole-lawn cycles and verified completion history support a systematic mismatch. |

All values remain intentionally unset or conservative until their necessary evidence exists. The guide does not authorise automatic dispatch or a live configuration change.

## Review cadence

- Review after material weather events, a completed all-zone job, a post-reboot recovery, or a clear recommendation mismatch.
- Prefer a small number of well-documented observations over continual micro-adjustment.
- Revisit a parameter only after enough new evidence exists to distinguish a repeatable model bias from normal weather/lawn variation.
