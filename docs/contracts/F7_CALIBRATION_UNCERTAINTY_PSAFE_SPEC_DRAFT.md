# F7 Calibration, Uncertainty and P_safe — Draft Ready Specification

Date: 2026-09-22

Status: DRAFT_READY__FORMULAS_AND_THRESHOLDS_DEFERRED

Pilot sport: FOOTBALL

Canonical basis:
- MODEL_POLICY.md
- NO_BET_AND_RISK_POLICY.md
- BACKTEST_AND_VALIDATION_STANDARD.md
- FOUNDATION_DECISIONS_v0.1

## Objective

Turn Football model outputs into validated calibrated probabilities, quantify uncertainty, and provide the governed interface from which a future P_safe can be produced.

The exact production P_safe formula is NOT defined here.

## Strict probability separation

Maintain distinct values:
- P_raw
- P_calibrated
- P_safe

Invariant:
`0 <= P_safe <= P_calibrated <= 1`

No human or LLM may directly set final P_safe.

## Data separation

Minimum chronological partitions:
- train
- validation
- calibration
- final_test

The calibrator must not fit on final_test.

Model hyperparameter choice must not use calibration/final-test leakage.

## Calibration candidates

OD-05 and related calibration decisions remain open.

Candidate methods may include, when sample size supports them:
- Platt/logistic scaling
- isotonic regression
- beta calibration
- multiclass calibration methods appropriate to 1X2

No method is preselected.

## Segmentation

Calibration may be:
- global;
- market-family-specific;
- competition-specific;
- probability-band-specific;
- other justified segments.

But segmentation is allowed only when sample size and stability support it.

Do not create small segments that look well calibrated from noise.

## Calibration metrics

At minimum:
- Log Loss
- Brier Score
- reliability/calibration curve
- ECE
- sample size

Additional:
- calibration slope/intercept
- probability-band counts
- confidence intervals
- subperiod stability

## Uncertainty

OD-02 remains OPEN.

The uncertainty layer must expose a typed output that can later feed P_safe conservatism.

Potential validated approaches may include:
- bootstrap intervals
- conformal-style approaches where appropriate
- Bayesian posterior uncertainty
- ensemble disagreement
- empirically validated residual/calibration uncertainty

No method is canonical until OOS validated.

## P_safe

OD-01 remains OPEN.

Requirements for any future formula:
- deterministic from versioned inputs;
- monotone/conservative where intended;
- never exceed P_calibrated;
- sensitive to validated uncertainty;
- reproducible;
- auditable;
- testable;
- no hidden LLM adjustment;
- no discretionary human probability bump.

## Missing/weak evidence

If calibration evidence is insufficient:
- do not fabricate P_safe confidence;
- evidence status must block qualification as appropriate;
- NO_BET is valid.

## Market comparison

Only after calibration and future P_safe exist:

`edge_calibrated = P_calibrated - P_market_no_vig`

`edge_safe = P_safe - P_market_no_vig`

Qualification uses edge_safe, not raw model optimism.

## Probability classifications

Presentation bands remain downstream labels derived from P_safe:
- P90 = 85–100%
- P80 = 75–84.99%
- P70 = 65–74.99%
- P60 = 60–64.99%
- P50 = 50–59.99%
- P40 = 40–49.99% Watchlist
- P25 = 25–39.99% Speculative
- below P25 = Reject

These labels never replace the underlying continuous probability.

## Required tests

1. probability bounds.
2. P_safe cannot exceed P_calibrated.
3. calibrator never fits final_test.
4. calibration split chronologically after model-training data.
5. multiclass probabilities sum to 1.
6. calibration artifact versioned.
7. sparse segmentation rejected or flagged.
8. no human/LLM direct P_safe setter exists.
9. deterministic replay with same model/calibrator/version.
10. probability-band boundary tests.
11. uncertainty metadata preserved.
12. insufficient calibration evidence cannot be QUALIFIED.
13. regression test for every future calibration leak.

## Promotion evidence

Calibration is not "VALID" merely because one reliability curve looks good.

OD-03 and OD-04 remain OPEN for:
- exact numerical VALID thresholds;
- minimum sample sizes.

Those thresholds must be justified empirically.

## Explicit non-goals

F7 does not:
- invent OD-01 P_safe formula;
- invent OD-02 uncertainty Champion;
- invent OD-03 calibration-valid thresholds;
- invent OD-04 sample thresholds;
- invent OD-05 segmentation Champion;
- qualify parlays;
- size real-money stakes.

## Acceptance

The scaffold is green when:
- calibration artifacts are fully separated/versioned;
- OOS calibration metrics are reproducible;
- uncertainty interface exists;
- P_safe interface prevents unsafe direct assignment;
- all unresolved numeric decisions remain visibly unresolved;
- final-test leakage is impossible by construction and tests.
