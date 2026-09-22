# Football Market Validation Decision Pack v0.1

Date: 2026-09-22

Status: RESEARCH_DESIGN__NO_OD_RESOLVED

Open decisions covered:
- OD-06 optional positive edge_safe threshold
- OD-07 no-vig Champion by sport/market/source

Football initial market families:
- FOOTBALL_1X2
- FOOTBALL_TOTAL_GOALS_MAIN

## OD-07 — No-vig methods to benchmark

Minimum research baseline:
- proportional normalization

Candidate challengers, where mathematically appropriate:
- power method
- additive method
- Shin-style method
- odds-ratio/logit style normalization
- source/bookmaker-specific method only if evidence supports it

Do not assume one method is best across:
- 1X2
- totals
- bookmakers
- market conditions

## No-vig experiment

For each bookmaker/market snapshot:
1. preserve raw decimal prices;
2. compute raw implied probabilities;
3. compute overround;
4. apply each candidate method;
5. validate probability constraints;
6. compare forecasting quality against realized outcomes;
7. compare stability across bookmaker/time/overround bands.

Metrics:
- Log Loss
- Brier
- calibration/ECE
- probability normalization error
- numerical stability
- sensitivity to overround
- missing-outcome failure rate

For totals:
- ensure exact line instance matches both sides;
- no mixing Over 2.5 with Under 3.0;
- incomplete pair => invalid snapshot for two-way no-vig.

For 1X2:
- home/draw/away set must be complete.

## Champion selection discipline

OD-07 may be resolved only after:
- same PIT snapshots are used for all methods;
- identical outcome sample;
- confidence intervals;
- no final-test tuning;
- no method selected from downstream betting ROI alone;
- source-specific differences documented.

A simpler method wins when performance is statistically indistinguishable and robustness is better.

## OD-06 — Positive edge_safe threshold

Current hard invariant:
- edge_safe < 0 => not QUALIFIED

Whether a stricter threshold > 0 is useful remains open.

Candidate research policies:
A. >0 only
B. fixed positive threshold
C. threshold conditional on uncertainty/data quality
D. threshold conditional on market family
E. abstention region derived empirically from edge estimation error

Do not use:
- threshold chosen to maximize historical ROI;
- one universal value without error analysis;
- odds-dependent threshold invented post hoc.

## Edge threshold evaluation

For each candidate threshold:
- qualification count/rate
- P_safe calibration among qualified selections
- realized no-vig advantage diagnostics
- CLV in later prospective evidence
- edge estimation error
- stability by season/fold
- sensitivity to odds/bookmaker
- false-positive rate
- opportunity loss / abstention cost

Paper ROI may be reported downstream but cannot be the sole threshold objective.

## Edge uncertainty

Threshold analysis should account for uncertainty in:
- P_calibrated
- P_safe
- market no-vig estimate
- stale/dispersion market observations

If estimated edge is smaller than its own uncertainty, qualification should not be assumed safe merely because the point estimate is positive.

Exact rule remains open until validated.

## Decision sequence

1. Historical PIT odds Stage A proves data semantics.
2. F6 implements versioned no-vig candidates.
3. OOS compare candidates by market family/source.
4. Freeze OD-07 proposal.
5. F7 provides P_safe + uncertainty.
6. Backtest edge estimation error.
7. Paper betting supplies CLV/prospective evidence.
8. Propose OD-06 only after enough evidence.
9. Independent review.
10. Enzo approval where required.

## Required artifacts

- bookmaker/source
- market family
- odds cutoff
- overround distribution
- candidate no-vig probabilities
- outcomes
- OOS scoring metrics
- confidence intervals
- edge candidate threshold
- qualification rate
- edge error analysis
- CLV when available
- code/data versions

## Current status

OD-06: OPEN
OD-07: OPEN
