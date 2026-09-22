# Football Model Agreement and Drift Decision Pack v0.1

Date: 2026-09-22

Status: RESEARCH_DESIGN__NO_OD_RESOLVED

Open decisions covered:
- OD-08 model agreement definition / threshold
- OD-09 data / concept / calibration drift thresholds

## OD-08 — Model agreement

Purpose:
avoid vague rules such as "3 models agree" without proving that agreement predicts reliability.

Candidate agreement signals:
- dispersion of predicted probabilities across validated models;
- variance / standard deviation;
- max-min spread;
- entropy of model-vote distribution;
- pairwise rank agreement;
- agreement on market side/direction;
- weighted disagreement using historically validated model quality.

Do not use raw model count unless all models are sufficiently independent and individually validated.

### Experiment

For identical PIT-valid fixtures:
- collect all candidate model forecasts;
- compute agreement statistics;
- bucket by agreement strength;
- measure realized forecast error/calibration in each bucket;
- compare against single-model uncertainty;
- test across folds, seasons and markets.

Required evidence:
- agreement metric correlates with OOS reliability;
- threshold stable across folds;
- no one model dominates so strongly that "agreement" is decorative;
- correlated model families do not create false confidence.

Reject:
- threshold chosen to maximize backtest ROI;
- arbitrary "majority vote";
- treating model correlation as independent confirmation;
- using a weak challenger solely to manufacture agreement.

## OD-09 — Drift

Monitor three distinct families:

### Data drift
Examples:
- feature distributions;
- missingness;
- source/provider mix;
- odds coverage;
- competition composition.

Candidate measures:
- PSI where justified;
- Wasserstein distance;
- KS-style comparisons for continuous variables;
- categorical distribution divergence;
- missingness-rate changes.

### Concept / performance drift
Examples:
- Log Loss deterioration;
- Brier deterioration;
- model-vs-market residual change;
- segment-specific failure.

### Calibration drift
Examples:
- ECE increase;
- calibration slope/intercept shift;
- reliability-curve deviation;
- P_safe realization underperformance.

## Threshold protocol

Do not choose universal thresholds upfront.

For each metric:
1. estimate normal historical variation from walk-forward folds;
2. quantify false-alert rate;
3. define WARNING and CRITICAL candidates;
4. validate on known regime changes if available;
5. freeze before prospective monitoring;
6. review after sufficient paper period.

Hard rule:
PIT integrity incident is always CRITICAL regardless of statistical threshold.

## Drift response candidates

INFO:
- log only.

WARNING:
- increase monitoring;
- suppress automatic promotion;
- require investigation.

CRITICAL:
- block new qualification for affected scope;
- demote Champion;
- require recalibration/retraining review.

Exact response mapping remains subject to OD-09 resolution.

## Decision artifacts

OD-08 proposal must include:
- agreement metric
- threshold
- model set
- model correlation analysis
- OOS reliability relationship
- affected market scope

OD-09 proposal must include:
- drift metric
- threshold
- baseline/reference window
- monitoring window
- alert class
- false-alert estimate
- response action
- revalidation rule

## Current status

OD-08: OPEN
OD-09: OPEN
