# Football Calibration / Uncertainty / P_safe Decision Pack v0.1

Date: 2026-09-22

Status: RESEARCH_DESIGN__NO_OD_RESOLVED

Open decisions covered:
- OD-01 exact P_safe formula
- OD-02 primary uncertainty method
- OD-03 numeric Calibration=VALID criteria
- OD-04 minimum sample sizes
- OD-05 calibrator segmentation

## Purpose

Prevent F7 from becoming a subjective design exercise.

No candidate is selected here.
No threshold is approved here.
No method may be promoted from in-sample fit.

## OD-05 — Calibrator segmentation experiment

Candidate scopes to compare:

A. global Football calibrator
- one calibrator per market family across all pilot data.

B. competition-specific
- separate by competition only when evidence supports enough data.

C. model-family-specific
- separate calibration by model output family/version.

D. probability-band / regime segmentation
- only if statistically justified;
- high overfitting risk.

E. hybrid hierarchical / pooled approach
- consider only if sample scarcity makes hard segmentation unstable.

Primary comparison:
- OOS Log Loss
- OOS Brier
- ECE
- calibration slope/intercept
- reliability stability
- confidence intervals
- fold-to-fold variance

Hard rejection:
- segmentation materially reduces sample size without robust OOS calibration gain;
- performance gain appears only in one fold;
- final-test tuning;
- empty/sparse bins create unstable calibration.

## OD-02 — Uncertainty method experiment

Candidate evidence sources:

1. bootstrap predictive/calibration uncertainty
2. model ensemble disagreement
3. Bayesian/posterior uncertainty where model family supports it
4. conformal-style intervals/scores where mathematically appropriate
5. empirical calibration residual uncertainty
6. combinations of the above only if each component has independent value

Required properties:
- out-of-sample estimable;
- deterministic/versioned given fixed inputs/seeds;
- monotonic interpretation;
- does not reward model disagreement;
- can be mapped into a conservative probability adjustment later;
- stable across time segments.

Evaluate:
- interval/safety coverage;
- sharpness;
- calibration conditional on uncertainty bucket;
- stability by season/fold;
- correlation with realized forecast error;
- failure during drift.

Reject:
- uncertainty score with no relationship to OOS error;
- method whose apparent coverage is tuned on final test;
- arbitrary disagreement penalty;
- method impossible to reproduce.

## OD-01 — P_safe candidate families

P_safe is a conservative transformation of P_calibrated informed by validated uncertainty.

Candidate families to test after OD-02 evidence exists:

A. lower-confidence-bound style
- P_safe derived from a lower confidence/credible bound.

B. calibrated shrinkage
- shrink P_calibrated toward a neutral/base rate according to validated uncertainty.

C. empirical risk envelope
- estimate conservative lower realization rate for similar forecast/uncertainty states.

D. hybrid bound
- combine calibration uncertainty and model uncertainty under explicit conservative rule.

Required invariants:
- 0 <= P_safe <= P_calibrated <= 1
- deterministic
- monotone with evidence quality where intended
- no human/LLM probability adjustment
- market odds are not used to inflate P_safe
- stronger uncertainty never increases P_safe unless a formally justified model says so
- no hidden threshold chosen to maximize paper ROI

Candidate evaluation:
- empirical realization frequency by P_safe band
- one-sided coverage / conservatism
- Brier / Log Loss diagnostics
- qualification stability
- sensitivity to sample size
- sensitivity to drift
- calibration retention
- edge false-positive rate downstream

Reject:
- formula optimized directly on betting ROI;
- constant arbitrary haircut such as "-5%" without evidence;
- direct MR/SP arithmetic penalty;
- LLM/context manual adjustment;
- formula that frequently yields P_safe > P_calibrated.

## OD-03 — Calibration=VALID decision protocol

Do not set numeric limits until the Football calibration dataset exists.

Candidate dimensions that final rule may use:
- ECE
- Brier relative to baseline
- Log Loss relative to baseline
- calibration slope/intercept
- confidence interval width
- minimum observations
- probability-bin support
- temporal stability
- drift status

A future VALID rule should be conjunctive or structured, not a single vanity metric.

Failure examples:
- excellent ECE from tiny sample;
- global calibration acceptable but severe P70/P80 band failure;
- good current score but unstable fold history;
- model underperforms naive/market benchmark materially.

## OD-04 — Minimum sample-size protocol

Do not choose one universal N.

Estimate required evidence separately by:
- sport
- market family
- calibration segmentation
- probability band
- model version scope

Methods to consider:
- confidence interval width targets
- bootstrap stability
- binomial/proportion precision for calibration bands
- effective sample size under temporal dependence
- simulation/power analysis

Rules:
- nominal sample count is not enough if observations are strongly clustered;
- sparse high-probability bands may require more calendar time;
- no minimum N may be chosen merely because it is convenient.

## Experimental sequence

1. F5 emits OOS P_raw across temporal folds.
2. Split calibration data remains untouched by model fitting.
3. Fit candidate calibrators.
4. Compare OD-05 segmentation candidates.
5. Measure calibration uncertainty and candidate OD-02 methods.
6. Define candidate P_safe transformations.
7. Evaluate without market-profit optimization.
8. Freeze candidate rules before final test.
9. Run frozen final test.
10. Independent review.
11. Only then propose OD-01..05 resolutions to Enzo.

## Required artifacts

For each experiment:
- dataset/PIT snapshot
- code SHA
- model version
- calibrator candidate/version
- uncertainty candidate/version
- segmentation
- sample counts
- folds/time ranges
- metrics
- confidence intervals
- calibration plots/tables
- failure notes
- final-test isolation statement

## Decision output format

For each OD, final proposal must include:
- chosen method/rule
- rejected alternatives
- OOS evidence
- uncertainty
- sample limitations
- affected markets
- failure behavior
- revalidation trigger
- reviewer verdict
- Enzo approval if required

## Current status

OD-01: OPEN
OD-02: OPEN
OD-03: OPEN
OD-04: OPEN
OD-05: OPEN
