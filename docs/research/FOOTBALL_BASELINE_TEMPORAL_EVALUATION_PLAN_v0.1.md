# Football Baseline Temporal Evaluation Plan v0.1

Date: 2026-09-22

Status: RESEARCH_DESIGN__FINAL_TEST_NOT_ASSIGNED

Pilot sport: FOOTBALL

Verified free results baseline:
- EPL 2000/01 through 2024/25
- 25 completed seasons
- 9,500 matches

Source evidence:
`data/manifests/football_openfootball_epl_2000_2025_verified.json`

## Purpose

Prepare a leakage-resistant temporal evaluation structure before model implementation without prematurely consuming a final test period.

This document does not start F5 and does not resolve OD-04 minimum sample-size thresholds.

## Non-negotiable ordering

Train -> Validation -> Calibration -> Final Test

The main evaluation is chronological.

Random match-level shuffle is prohibited for the principal benchmark.

## Why the final test is not assigned now

A final test is useful only if it remains untouched during:
- model-family selection;
- feature selection;
- hyperparameter tuning;
- calibration-method selection;
- ensemble design.

Therefore this research document deliberately does not designate a specific final-test season.

At F5 start:
1. confirm the usable historical dataset after PIT/data-quality filtering;
2. choose and record the final-test block before running candidate-model metrics on it;
3. hash/freeze the partition definition;
4. prevent tuning code from accessing it.

## Research-development pool

The 25-season source corpus is a **source availability pool**, not an automatic modeling dataset.

Before a season enters a modeling fold it must pass:
- parser validation;
- entity-resolution readiness;
- chronological ordering;
- missing-time policy;
- rule/competition-format consistency review;
- feature availability for the selected feature set.

A season can be excluded with an explicit reason; do not silently shrink the denominator.

## Walk-forward structure

Use season-blocked folds.

Generic fold shape:

- TRAIN: all approved seasons up to season S
- VALIDATION: next approved season(s)
- CALIBRATION: later non-overlapping approved season(s)
- EVALUATION: next approved season(s), for research folds only

The exact number of seasons in each block is configuration, not hardcoded policy.

The final governed test remains separate from research-fold evaluation.

## Expanding versus rolling training window

Benchmark both only if justified:

### Expanding window
Train on all approved history before the fold.

Pros:
- maximum sample size;
- stable simple-model estimation.

Risk:
- very old regimes may dilute current signal.

### Rolling window
Train on the most recent N approved seasons.

Pros:
- adapts to drift/regime changes.

Risk:
- lower sample size;
- N can be overfit if tuned carelessly.

No rolling-window length is selected by this document.

## Season boundaries

Treat season transitions explicitly.

Candidates for later model-specific policy:
- Elo carry-over with shrinkage;
- promoted-team initialization;
- attack/defence parameter partial pooling;
- season intercept;
- competition-wide scoring-rate drift.

Do not reset or carry ratings by intuition. Compare policies OOS.

## Feature chronology

For target fixture i:
1. construct feature state from fixtures completed before the decision cutoff;
2. freeze the feature row;
3. generate prediction;
4. observe target result only afterward;
5. update sequential state.

No target result or later fixture may affect the target feature row.

## Calibration

Calibration data must be distinct from:
- training;
- hyperparameter validation;
- final test.

Calibration candidates are compared only when sample size permits.

No calibration method is selected here.

## Market benchmark alignment

When historical odds become available:
- the market observation must match the exact simulated cutoff;
- closing odds remain evaluation-only unless the simulated decision cutoff is actually closing;
- market-blind and market-aware tracks remain separate.

The 40-fixture Stage A odds sample is provider/PIT engineering evidence, not sufficient model-selection evidence.

## Metrics

Per market family, later F5/F7/F9 must report:
- Log Loss;
- Brier Score;
- calibration/reliability;
- ECE;
- sample size;
- confidence intervals when defined;
- time/subperiod stability.

For 1X2:
- Ranked Probability Score may be included.

Accuracy is secondary and cannot select Champion alone.

## Drift / era analysis

Because the source spans 25 seasons, later research must test performance by era/subperiod rather than assuming stationarity.

Questions:
- does older history improve or hurt OOS Log Loss?
- do scoring-rate changes shift Poisson calibration?
- does Elo optimal carry-over vary over time?
- are model errors stable pre/post structural competition changes?
- does market baseline efficiency change across available odds eras?

Do not answer these from in-sample fit.

## Model-family fairness

Elo, Bradley-Terry, Poisson, Dixon-Coles, logistic/discriminative and boosting candidates must be evaluated on the same eligible fixtures for a given comparison.

If a model requires richer features unavailable in older seasons:
- report the reduced common sample;
- also keep simple-model comparison on the broader results-only sample;
- do not compare scores from different fixture sets as if directly equivalent.

## Reproducibility requirements

A future split manifest must record:
- dataset/source snapshot;
- included seasons;
- excluded seasons/reasons;
- train interval;
- validation interval;
- calibration interval;
- research evaluation interval;
- final-test interval once frozen;
- feature set version;
- code SHA;
- random seeds where relevant;
- fold IDs;
- row counts.

## OD-04

Minimum acceptable sample size remains OPEN.

The existence of 9,500 source matches does not itself define:
- calibration minimum N;
- model promotion minimum N;
- per-band minimum N;
- Sport Predictability evidence minimum N.

Those require empirical justification.

## Current conclusion

The free OpenFootball baseline appears large enough to support serious chronological baseline-model research without buying broad result history first.

The next paid-data priority remains historical market state and high-value PIT context rather than basic result labels.

Final test:
**UNASSIGNED — DO NOT INVENT OR CONSUME DURING PRE-F5 RESEARCH**
