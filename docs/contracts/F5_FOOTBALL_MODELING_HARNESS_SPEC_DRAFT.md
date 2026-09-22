# F5 Football Modeling Harness — Draft Ready Specification

Date: 2026-09-22

Status: DRAFT_READY__BLOCKED_BY_F0_REVIEW_F2_F3_F4

Pilot sport: FOOTBALL

Canonical basis:
- MODEL_POLICY.md
- BACKTEST_AND_VALIDATION_STANDARD.md
- ARCHITECTURE.md
- docs/research/FOOTBALL_MODEL_BENCHMARK_PLAN_v0.1.md

## Objective

Implement a reproducible Football-specific model benchmark harness that produces comparable raw probabilistic forecasts without selecting a champion in advance.

F5 is Football-specific. It must not become a generic universal multi-sport champion model.

## Mandatory evaluation sequence

Train -> Validation -> Calibration -> Final frozen test

Temporal / walk-forward validation is mandatory.

Random shuffle split is prohibited for the main evaluation.

## F5 boundary

F5 owns:
- model interfaces;
- Football candidate implementations;
- temporal training/evaluation harness;
- raw probability outputs;
- model artifacts/metadata;
- OOS metric computation needed for model comparison.

F5 does not own:
- historical provider ingestion;
- PIT eligibility;
- production calibration policy;
- production P_safe formula;
- S-Tier qualification;
- parlay optimization;
- real-money execution.

F3/F4 supply PIT-safe model inputs.

## Required model baselines/candidates

### B0 — naive baseline

Simple interpretable baseline required to prove more complex models add signal.

### B1 — de-vigged market benchmark

A separate forecasting benchmark based on point-in-time market probabilities.

It is not the Football sports model and must not be confused with model edge.

### M1 — sequential Elo/rating

Requirements:
- strictly chronological updates;
- pre-match rating frozen before target outcome;
- transparent initialization/season transition treatment.

### M2 — Bradley-Terry family

Requirements:
- relative team strength;
- explicit draw treatment for 1X2;
- no silent binary collapse.

### M3 — Poisson goal model

Requirements:
- home/away goal-intensity modeling;
- coherent score distribution;
- derivable 1X2 probabilities;
- derivable total-goals probabilities where mathematically valid.

### M4 — Dixon-Coles challenger

Requirements:
- low-score dependence adjustment;
- same PIT and temporal validation discipline.

### M5 — multinomial logistic / interpretable discriminative model

Purpose:
- simple discriminative benchmark using approved Football features.

### M6 — gradient boosting challenger

Candidate implementation family may later include:
- CatBoost
- LightGBM
- XGBoost

The exact library is not preselected by this spec.

### M7 — ensemble

Only after individual candidates are OOS validated.

No manual ensemble weights.

Weights must be learned and validated without test leakage.

## Market-blind and market-aware tracks

### Track A — market-blind

Bookmaker probabilities are excluded from sports-model features.

Purpose:
- measure independent sporting signal;
- preserve clean comparison to market.

### Track B — market-aware challenger

Point-in-time de-vigged market state may be included only as a separate challenger.

Requirements:
- explicit ablation against B1 market baseline;
- no circular claim of edge;
- same chronological evaluation;
- market features available at the exact simulated cutoff.

## Market-specific evidence

Football Phase 1 families:
- FOOTBALL_1X2
- FOOTBALL_TOTAL_GOALS_MAIN

A model/calibration result for one family must not automatically authorize another.

Where a score model naturally produces both markets, each market still requires its own OOS calibration/performance evidence.

## Dataset partitions

The harness must support explicit immutable partitions:
- train
- validation
- calibration
- final_test

And repeated walk-forward folds.

Final test:
- untouched during model/hyperparameter choice;
- frozen before final comparison;
- results recorded once per approved evaluation version unless governance explicitly authorizes a new final-test generation.

## Preprocessing

Any learned transformation must be fit inside the training boundary only:
- scaling
- encoding
- imputation
- feature selection
- dimensionality reduction
- learned embeddings
- hyperparameter search

No transform may see validation/calibration/final-test future information during fitting.

## Missing values

No silent zero fill.

Imputation:
- must be semantically justified;
- learned only on training data;
- missingness indicator considered where appropriate;
- compared OOS;
- recorded in model pipeline.

## Minimum predictive metrics

Per BACKTEST_AND_VALIDATION_STANDARD and MODEL_POLICY:

- Log Loss
- Brier Score
- calibration / reliability
- ECE
- sample size

Additional recommended Football comparison:
- Ranked Probability Score for 1X2
- calibration slope/intercept
- performance by probability band
- performance by season/time segment
- performance by competition if/when multiple competitions enter
- confidence intervals

Accuracy may be reported but cannot select Champion alone.

## Market/decision metrics kept downstream

Track but do not use as a substitute for predictive validation:
- CLV
- paper ROI
- yield
- drawdown

These become meaningful in later market/paper-betting phases.

## Uncertainty in model comparison

Small OOS score differences must not automatically create a champion.

The harness must support paired comparison on identical fixtures and confidence intervals.

Bootstrap or another validated dependence-aware method may be used later; exact method remains subject to validation.

## Reproducibility record

Every experiment must retain:
- experiment_id
- sport
- market_family
- dataset snapshot/version
- PIT materialization reference
- feature_set_version
- code commit/SHA
- model family
- model version
- hyperparameters
- preprocessing specification
- random seed where applicable
- train interval
- validation interval
- calibration interval
- final test interval
- environment/dependency lock reference
- metrics
- artifact hashes

## Champion/Challenger lifecycle

Initial state:
- all complex candidates are challengers.

Promotion to Champion requires:
- temporal OOS validation;
- satisfactory calibration evidence;
- stability by subperiod;
- comparison with simple baseline;
- comparison with market baseline where relevant;
- no detected temporal leakage;
- documented metrics;
- model card;
- frozen final test;
- independent review.

OD-11 remains OPEN until these requirements are met.

## Drift hooks

F5 artifacts must expose enough metadata for later monitoring of:
- data drift
- concept drift
- calibration drift
- model/market disagreement

F5 does not implement production drift thresholds.

## Required tests

1. deterministic training with fixed seed where estimator permits.
2. chronological fold ordering.
3. no train rows after evaluation rows.
4. preprocessing fit only on allowed training rows.
5. labels never present in features.
6. incremental Elo update order.
7. market-blind track contains no market feature.
8. market-aware track cannot use odds after its cutoff.
9. probability outputs valid and normalized for 1X2.
10. Poisson/Dixon-Coles score-distribution sanity checks.
11. model artifact contains lineage fields.
12. final-test partition cannot be silently reused for tuning.
13. market-family metrics kept separate.
14. missing values are not silently converted to zero.
15. regression test for every future leakage/modeling defect.

## Engineering sample

Initial plumbing sample:
- EPL 2024/25 when provider data is available.

Open-data parser/event-feature sandbox:
- EPL 2015/16 StatsBomb Open.

The engineering sample is not evidence of superior betting profitability.

## Acceptance

F5 technical green requires:
- all required baseline/candidate interfaces implemented for the approved milestone;
- walk-forward harness green;
- reproducibility artifacts complete;
- required metrics generated;
- no leakage failures;
- no champion declared solely from validation data;
- independent model review requested before Champion promotion.

## Explicit non-goals

F5 does not:
- define P_safe;
- qualify bets;
- implement bankroll sizing;
- implement S-Tier;
- implement parlays;
- claim profitability from backtest alone.
