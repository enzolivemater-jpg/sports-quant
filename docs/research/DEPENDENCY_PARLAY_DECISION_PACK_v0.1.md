# Dependency / Parlay Decision Pack v0.1

Date: 2026-09-22

Status: RESEARCH_DESIGN__NO_OD_RESOLVED

Open decisions covered:
- OD-18 Market Risk mode limits
- OD-19 quantitative dependency method
- OD-20 marginal leg value criterion
- OD-21 significant multi-sport improvement threshold
- OD-22 solver choice
- OD-23 joint model / Monte Carlo method

## OD-19 — Dependency quantification

Candidate methods:
- empirical conditional frequencies;
- correlation of latent/event outcomes where meaningful;
- conditional probability models;
- copula/joint-distribution approaches;
- shared latent-variable models;
- Monte Carlo from validated event models.

Use case decides method.

Do not apply one universal correlation coefficient to all market pairs.

Required classes remain:
- independent
- weak
- moderate
- strong
- redundant
- contradictory

Quantitative thresholds remain open.

## OD-23 — Joint probability / Monte Carlo

Candidate approaches:
- exact joint enumeration where tractable;
- conditional factorization;
- Monte Carlo from joint score/state model;
- empirical resampling;
- copula-based simulation where justified.

Validation:
- marginal probabilities reproduced;
- dependence structure reproduced;
- joint-event calibration;
- Monte Carlo convergence;
- deterministic seed/reproducibility;
- sensitivity analysis.

Reject:
- multiplying marginals under unverified independence;
- simulator whose marginals do not match approved P_safe inputs;
- arbitrary correlation adjustments.

## OD-20 — Marginal leg value

A new leg should be evaluated by change in:
- combined P_safe;
- return;
- dependency burden;
- uncertainty;
- MR profile;
- data/calibration quality.

Candidate decision rule:
Pareto improvement / dominated-leg elimination rather than single weighted score.

A leg that increases odds while materially reducing safe probability without validated compensation is rejected.

No exact numeric rule is selected here.

## OD-21 — Multi-sport improvement

Compare best valid mono-sport and best valid multi-sport candidates on the same dimensions:
- combined P_safe;
- return;
- uncertainty;
- dependency;
- MR;
- data quality.

Multi-sport may be preferred only when improvement is meaningful under future validated threshold.

Do not assume diversification automatically reduces risk.

## OD-18 — MR mode limits

Current structural modes:
- conservative
- balanced
- aggressive
- speculative

Exact additional limits may consider:
- max MR per leg;
- count of MR3+;
- count of MR4+;
- interaction with dependency class.

Do not implement weighted_average_mr or composite Dynamic Market Risk Score.

## OD-22 — Solver

Start with transparent enumeration/pruning when candidate set is small.

Adopt OR-Tools or another solver only when:
- candidate-space size creates material runtime issue;
- constraints are stable enough to encode;
- results can be independently verified on small cases.

Solver convenience alone is not reason to add dependency.

## Experimental order

1. validate single-leg stack;
2. collect qualified leg datasets;
3. label/event-link common underlying outcomes;
4. test pairwise dependency estimation;
5. validate joint-probability method;
6. implement transparent small-set enumeration;
7. evaluate marginal leg rules;
8. compare mono/multi;
9. only then consider optimization solver.

## Required tests for any final method

- marginals preserved;
- independence case reproduces product within tolerance;
- dependent synthetic cases recover known direction;
- contradictory legs rejected;
- redundant legs not treated as diversification;
- deterministic simulation seed;
- convergence diagnostics;
- exact small-case comparison;
- no invalid leg enters optimizer.

## Current status

OD-18: OPEN
OD-19: OPEN
OD-20: OPEN
OD-21: OPEN
OD-22: OPEN
OD-23: OPEN
