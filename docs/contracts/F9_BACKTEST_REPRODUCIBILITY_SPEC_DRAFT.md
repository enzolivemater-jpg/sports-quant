# F9 Backtesting and Reproducibility — Draft Ready Specification

Date: 2026-09-22

Status: DRAFT_READY__BLOCKED_BY_PREVIOUS_PHASES

Pilot sport: FOOTBALL

Canonical basis:
- BACKTEST_AND_VALIDATION_STANDARD.md
- MODEL_POLICY.md
- DATA_POLICY.md
- FOUNDATION_DECISIONS_v0.1

## Objective

Provide a leakage-resistant, deterministic backtesting framework that replays historical Football decisions exactly as SPORTS QUANT could have made them at each simulated decision cutoff.

Backtesting validates forecasting and decision logic. It does not prove future profitability.

## Mandatory temporal structure

Train -> Validation -> Calibration -> Final Test

Main evaluation:
- walk-forward / time-series split mandatory;
- no random shuffle as the primary evaluation;
- every simulated event uses only information PIT-eligible at its decision cutoff.

## Replay unit

A backtest decision snapshot must bind:
- event
- market family
- market instance
- decision_cutoff_at
- PIT dataset snapshot
- feature_set_version
- model version
- calibrator version
- uncertainty/P_safe version when available
- market/no-vig version
- S-Tier gate version
- code commit/SHA
- dependency/environment lock

The result must be reproducible from these references.

## No future information

For event E at cutoff T:
- no record with known_at > T;
- no later provider revision unless the earlier version is independently available;
- no closing odds for an earlier cutoff;
- no final lineup before historical publication;
- no target-match post-event statistic;
- no transform fitted with later rows.

A single critical leakage defect invalidates the affected backtest evidence.

## Backtest layers

### Layer A — Forecast validation
Evaluate raw/calibrated model forecasts independently of betting decisions.

Required:
- Log Loss
- Brier Score
- calibration/reliability
- ECE
- sample size
- confidence intervals where defined
- segment stability

### Layer B — Market comparison
At the exact historical cutoff evaluate:
- P_market_no_vig
- edge_calibrated
- edge_safe when P_safe exists
- opening/current/closing market references where available

Closing price is evaluation-only for earlier decisions.

### Layer C — Decision replay
Replay:
- QUALIFIED
- WAIT
- REVIEW
- NO_BET
- BLOCKED

using the S-Tier rules/version that were valid for the simulated experiment.

No retroactive manual overrides.

### Layer D — Paper economics
For qualified simulated selections track:
- odds used at simulated decision time
- theoretical paper stake unit
- result
- profit/loss
- ROI paper
- yield
- drawdown
- CLV where closing observations exist

Backtest economic metrics do not override predictive/calibration requirements.

## Required segment reporting

At minimum report by:
- sport
- competition
- market family
- market instance where useful
- odds band
- P_safe band
- MR_base
- model version
- calibrator version
- season/time period
- decision cutoff policy

For parlays later also:
- L1: 2–5 legs
- L2: 6–7
- L3: 8–10
- L4: 11–15
- L5: 16–20
- L6: 21+
- mono-sport
- multi-sport
- dependency class

## Classification reporting

Probability bands:
- P90: 85–100%
- P80: 75–84.99%
- P70: 65–74.99%
- P60: 60–64.99%
- P50: 50–59.99%
- P40: 40–49.99%
- P25: 25–39.99%
- below P25: Reject

Return bands:
- R1: <2
- R2: 2–3
- R3: 3–5
- R4: 5–10
- R5: 10–20
- R6: 20+

Parlay leg-count bands:
- L1: 2–5
- L2: 6–7
- L3: 8–10
- L4: 11–15
- L5: 16–20
- L6: 21+

These are descriptive reporting dimensions, not targets.

## CLV

Where closing odds are available:
- compare decision-time price with closing market price;
- preserve bookmaker/consensus methodology;
- distinguish raw odds movement from no-vig probability movement.

CLV is diagnostic evidence, not proof of model correctness by itself.

## ROI / yield / drawdown

Paper calculations must be deterministic and based on the exact simulated decision-time odds.

V1 must not use:
- martingale
- chase losses
- retrospective stake tuning
- stake increase after losses

If a fixed-unit paper stake is used initially, it must be explicit and versioned.

## Multiple testing / research discipline

Do not promote a strategy because one parameter combination happens to produce attractive historical ROI.

Record:
- all candidate configurations evaluated;
- tuning space;
- validation criterion;
- final test freeze.

The final test must remain untouched during iterative research.

## Reproducibility manifest

Every backtest run must persist:
- backtest_run_id
- created_at
- code SHA
- dependency lock hash/reference
- dataset snapshot
- raw source snapshot references
- PIT kernel version
- feature set version
- model version
- calibrator version
- P_safe version if applicable
- market engine version
- gate version
- parameter/config version
- train/validation/calibration/test intervals
- random seeds
- output artifact hashes
- row counts and exclusions
- leakage audit result

## Frozen final test

Champion promotion requires:
- predefined final-test period;
- no tuning against final-test metrics;
- one governed evaluation per approved experiment generation;
- independent review.

If the final test is reopened for development, it loses frozen-test status and a new untouched test period must be defined.

## Failure semantics

Backtest run is INVALID when:
- PIT integrity fails;
- lineage is incomplete for critical data;
- final test was used in tuning;
- output cannot be reproduced;
- target leakage is detected;
- decision-time odds cannot be reconstructed but are silently approximated.

Backtest run may be PARTIAL/RESEARCH_ONLY when:
- some non-critical evaluation metrics are unavailable;
- CLV unavailable;
- optional context absent.

## Required tests

1. same manifest + same inputs -> identical decisions/metrics.
2. future record injection changes nothing because it is rejected.
3. closing odds unavailable at pre-close cutoff.
4. final-test rows cannot enter tuning.
5. labels inaccessible during feature generation.
6. excluded records have explicit reason.
7. P/L/R/MR segment boundaries exact.
8. drawdown calculation deterministic.
9. ROI/yield calculations deterministic.
10. no missing odds silently approximated.
11. walk-forward fold ordering valid.
12. backtest manifest complete.
13. fixed frozen test hash detects mutation.
14. regression test for every future leakage bug.

## Promotion rule

A Football model/decision stack cannot be promoted from backtest alone.

Backtest evidence is necessary but must be followed by prospective paper betting.

## Explicit non-goals

F9 does not:
- guarantee profitability;
- authorize real-money use;
- choose staking strategy;
- build parlays before dependency modeling;
- replace live paper validation.

## Acceptance

F9 is green only when:
- deterministic replay works;
- anti-leakage tests pass;
- segment reporting is complete;
- final-test governance is enforced;
- predictive and economic metrics are separated;
- independent review finds no P0/P1 flaw.
