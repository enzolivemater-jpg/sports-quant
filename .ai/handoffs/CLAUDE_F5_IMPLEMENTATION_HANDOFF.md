# Claude Pro Handoff — F5 Football Modeling Harness

Date: 2026-09-22

Status: READY_AFTER_F4_ACCEPTANCE

Repository: `enzolivemater-jpg/sports-quant`
Implementation issue: #8

## Start condition

Do not begin unless:
- F0 gate passed;
- F2/F3/F4 merged and accepted;
- Football pilot dataset is reproducible;
- PIT audit green;
- current main CI/Security green.

## Primary spec

Implement:
`docs/contracts/F5_FOOTBALL_MODELING_HARNESS_SPEC_DRAFT.md`

Read:
- `docs/research/FOOTBALL_MODEL_BENCHMARK_PLAN_v0.1.md`
- `docs/research/FOOTBALL_FEATURE_GOVERNANCE_v0.1.md`
- canonical model/backtest policies.

## Objective

Build reproducible Football Champion/Challenger comparison infrastructure.

No model is preselected as Champion.

## Required candidates / baselines

- naive baseline
- de-vigged market benchmark
- sequential Elo/rating
- Bradley-Terry family
- Poisson
- Dixon-Coles
- multinomial logistic / interpretable discriminative model
- one gradient boosting challenger when dependencies justify it
- ensemble only after individual OOS validation

If library choice for boosting is not yet governed, STOP before hardwiring an unnecessary dependency.

## Two tracks

### Market-blind
No odds as sports-model features.

### Market-aware challenger
Point-in-time de-vigged market state may enter only in a separate explicitly labelled challenger with ablation against market baseline.

Never claim edge because a model ingested the market then reproduced it.

## Validation

Train -> Validation -> Calibration -> Final frozen test.

Main evaluation is chronological/walk-forward.

No random shuffle primary evaluation.

All learned transforms fit inside training boundary only.

## Required metrics

- Log Loss
- Brier
- ECE / reliability
- sample size
- calibration slope/intercept where implemented
- 1X2 RPS where useful
- confidence intervals
- subperiod stability

Accuracy may be reported but cannot select Champion.

## Reproducibility

Every experiment retains:
- experiment ID
- dataset/PIT snapshot
- feature version
- code SHA
- model family/version
- hyperparameters
- preprocessing
- seeds
- split intervals
- dependency lock
- metrics
- artifact hashes

## OD-11

OD-11 stays OPEN until governed OOS comparison and final-test review.

Claude must not mark any model Champion solely from validation metrics.

## Required tests

- deterministic seed behavior where applicable
- temporal fold order
- no train rows after eval rows
- preprocessing fit scope
- label isolation
- sequential Elo update order
- market-blind contains no market features
- market-aware cutoff safety
- valid/normalized probabilities
- Poisson/Dixon-Coles sanity
- complete model lineage
- final test cannot enter tuning
- market-family metrics separate
- missing != zero
- leakage regression tests

## Non-goals

Do not:
- define production P_safe
- qualify bets
- implement S-Tier
- implement optimizer
- claim profitability from backtest
- start F6/F7 in same PR

## Completion

TECHNICALLY_GREEN only if:
- harness reproducible
- required models/baselines for approved milestone run
- walk-forward works
- metrics generated
- leakage tests green
- CI/Security green
- no Champion promoted without review
