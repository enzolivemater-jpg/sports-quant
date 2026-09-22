# Football Model Benchmark Plan v0.1

Date: 2026-09-22

Status: RESEARCH_DESIGN__OD-11_REMAINS_OPEN

Pilot sport: FOOTBALL

## Objective

Prepare a fair Champion/Challenger benchmark before implementation so SPORTS QUANT does not select a model family by intuition, popularity or in-sample accuracy.

No champion is selected by this document.

## Core principle

Separate:
1. independent sporting signal;
2. market information;
3. calibration;
4. conservative decision probability.

A model that reproduces bookmaker probabilities is not automatically evidence of exploitable edge.

## Baselines

### B0 — Naive frequency / class baseline
Purpose:
- detect whether sophisticated models add real predictive skill.

### B1 — De-vigged market baseline
Purpose:
- establish the strongest practical forecasting reference;
- evaluate whether model signal adds information beyond prices.

Use point-in-time odds only.

Do not train B1 as a sports model.

## Candidate model families

### M1 — Elo / sequential rating model
Purpose:
- robust low-complexity team-strength baseline;
- easy sequential PIT update;
- interpretable drift.

Candidate outputs:
- direct 1X2 probabilities through an appropriate mapping;
- strength features for other models.

### M2 — Bradley-Terry family
Purpose:
- direct relative-strength comparison;
- challenger to Elo for outcome modeling.

Draw handling must be explicit rather than silently collapsed.

### M3 — Poisson goal model
Purpose:
- model home/away scoring intensities;
- naturally derive 1X2 and total-goals distributions.

### M4 — Dixon-Coles
Purpose:
- Poisson-family challenger with low-score dependence correction;
- especially relevant for football scorelines.

### M5 — Multinomial logistic regression / GAM
Purpose:
- calibrated, interpretable discriminative benchmark;
- test whether engineered features add signal beyond ratings.

### M6 — Gradient boosting
Candidate implementations later may include LightGBM, CatBoost or XGBoost.

Purpose:
- nonlinear challenger;
- handle interactions among rolling team-strength/context features.

Do not assume boosting is superior.

### M7 — Ensemble
Allowed only after individual models are OOS validated.

Potential ensemble inputs:
- score-model probabilities;
- rating-model probabilities;
- discriminative-model probabilities.

Weights must be learned/validated out of sample. No manual weights.

## Market-blind versus market-aware tracks

### Track A — Market-blind sports model
Odds are excluded from model features.

Purpose:
- measure independent sports-data predictive skill;
- avoid circular comparison when edge is later measured against the market.

### Track B — Market-aware challenger
Point-in-time market probabilities may be included as features only in a separate challenger.

Purpose:
- test whether non-market features add incremental information conditional on market state.

Important:
- Track B must be compared against the same de-vigged market baseline;
- apparent edge must not arise merely from feeding the target market price into the model and comparing the transformed output back to itself;
- market-aware models require explicit ablation tests.

## Initial feature families for retrospective PIT-safe baseline

Only use features derivable from data legitimately available before cutoff.

Examples:
- sequential team ratings;
- rolling goals for/against;
- rolling expected-goal features only if historical source timestamps are defensible;
- home/away splits;
- rest days;
- schedule congestion;
- opponent-strength-adjusted form;
- league-position state reconstructed from prior results;
- promotion/relegation/new-season indicators;
- season phase.

Context such as historical injuries/lineups is excluded until known_at can be defended.

## Target markets

Canonical Football Phase 1:
- FOOTBALL_1X2;
- FOOTBALL_TOTAL_GOALS_MAIN.

The score-model families should produce coherent probabilities for both when possible.

## Temporal validation

Never random-shuffle match records.

Minimum design:
- chronological train window;
- separate validation window;
- separate calibration window;
- untouched final test window;
- repeated walk-forward evaluation.

Any feature transformer must fit only on information available within the training boundary.

## Champion metrics

Primary:
- Log Loss;
- Brier Score;
- calibration / ECE.

Additional:
- Ranked Probability Score for 1X2 where appropriate;
- calibration slope/intercept;
- reliability plots;
- confidence intervals;
- performance by probability band;
- performance by season/competition segment;
- stability under drift.

Market/decision metrics are downstream:
- edge_safe after P_safe exists;
- CLV;
- paper ROI/yield;
- drawdown.

Accuracy alone cannot select the champion.

## Required ablations

At minimum compare:
- ratings only;
- rolling form only;
- ratings + rolling form;
- score model without market;
- discriminative model without market;
- market baseline;
- market-aware challenger;
- model ensemble if justified.

Any context feature later added must show incremental OOS value and not merely improve in-sample fit.

## Statistical comparison

Use:
- confidence intervals;
- paired comparisons on identical test fixtures;
- bootstrap or another validated dependence-aware method;
- sample-size reporting.

Do not declare a winner from tiny score differences without uncertainty analysis.

## Pilot engineering sample

For provider bake-off and pipeline plumbing, use the English Premier League as the first engineering sample unless a provider coverage test fails.

This is NOT a claim that EPL offers the best betting edge.

Reason:
- broad provider documentation/coverage;
- broad bookmaker coverage;
- stable competition format;
- useful entity and market testbed.

Suggested first completed-season sample:
- 2024/25 EPL.

If one provider cannot supply the required historical sample, record that as a coverage limitation rather than silently switching samples for that provider.

## Research rationale

Recent comparative literature supports:
- strong bookmaker forecasts as a necessary baseline;
- small performance differences among many model classes;
- temporal validation rather than random splits;
- continued relevance of Poisson/Dixon-Coles and Bradley-Terry/Elo families;
- proper scoring rules and calibration over raw accuracy.

## OD-11 status

OPEN.

The Football champion model family will be selected only after point-in-time, out-of-sample comparison.
