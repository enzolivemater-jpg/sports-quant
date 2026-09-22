# F11 Paper Betting and Monitoring — Draft Ready Specification

Date: 2026-09-22

Status: DRAFT_READY__REAL_MONEY_NOT_AUTHORIZED

Pilot sport: FOOTBALL

Canonical basis:
- NO_BET_AND_RISK_POLICY.md
- BACKTEST_AND_VALIDATION_STANDARD.md
- MODEL_POLICY.md
- FOUNDATION_DECISIONS_v0.1

## Objective

Evaluate SPORTS QUANT prospectively on genuinely unseen Football events before any real-money operational use is considered.

Paper betting is not optional validation theater. It is the bridge between historical backtest and real-world decision support.

## Core rule

At decision time:
1. capture the exact available data/odds/context;
2. run the approved pipeline;
3. freeze the decision snapshot;
4. do not alter it after the event;
5. settle outcome later;
6. evaluate forecast, calibration, CLV and paper economics.

## Decision modes

Record every evaluated opportunity, including:
- QUALIFIED
- WAIT
- REVIEW
- NO_BET
- BLOCKED

Do not log only winning/qualified selections.

This prevents survivorship bias.

## Paper selection record

Required:
- paper_decision_id
- event
- competition
- market
- bookmaker/market consensus reference
- decision_cutoff_at
- exact odds available
- P_raw
- P_calibrated
- P_safe
- probability band
- edge_calibrated
- edge_safe
- MR_base
- SP evidence reference
- model/calibrator/P_safe versions
- gate-by-gate results
- context evidence
- dependency data for parlays
- decision state
- reason codes
- immutable snapshot hash

## Paper stake policy

V1 priority is validation, not bankroll optimization.

Initial paper stake should be a simple deterministic unit policy.

Do not use:
- martingale
- loss chasing
- stake increase after a loss
- retrospective stake changes
- hidden discretionary sizing

Any later staking policy is a separate governed module and does not change prediction probability.

## Settlement

After event completion record:
- result
- market settlement
- paper P/L
- void/push handling
- closing odds where available
- CLV
- settlement source/provenance

Settlement data must remain isolated from the frozen pre-event decision record.

## Monitoring metrics

At minimum rolling and cumulative:
- Log Loss
- Brier Score
- ECE/calibration
- sample size
- CLV
- ROI paper
- yield
- drawdown
- qualification rate
- NO_BET rate
- WAIT/REVIEW/BLOCKED rates

Segment by:
- competition
- market family
- odds band
- P_safe band
- MR
- model version
- calibrator version
- decision cutoff
- source/provider composition

For parlays later:
- L1–L6
- mono/multi
- dependency class
- R class

## Drift monitoring

Track:
- data drift
- concept drift
- calibration drift
- model/market disagreement
- source coverage drift
- missingness drift
- provider revision behavior

OD-09 remains open for numeric drift thresholds.

Do not invent thresholds solely to keep a model active.

## Model lifecycle

If monitoring indicates critical degradation:
- stop qualification where required;
- demote Champion to Challenger or BLOCK outputs according to approved policy;
- investigate;
- retrain/recalibrate through governed pipeline;
- never silently hot-fix probabilities.

## Calibration monitoring

Track observed frequencies by P_safe/P_calibrated bands.

Example principle:
events predicted around 70% should not systematically realize far below that level over sufficient sample.

Exact validity thresholds and minimum sample sizes remain OD-03/OD-04.

## CLV

Track decision-time price against closing price when available.

Positive CLV is useful evidence of market timing/value but is not by itself proof of calibrated probability or profitability.

## NO_BET quality

Monitor NO_BET explicitly.

Questions:
- are too many weak opportunities being qualified?
- are nearly all opportunities blocked because rules are too strict?
- do rejected candidates later reveal systematic missed signal?
- is NO_BET stable by competition/market/time?

Do not optimize for bet frequency.

## Alert levels

Exact numeric thresholds remain deferred.

Conceptual alert classes may be:
- INFO
- WARNING
- CRITICAL

Examples:
- provider outage
- missing critical context
- calibration deterioration
- unexpected no-vig/overround behavior
- severe model/market disagreement
- PIT integrity incident

A PIT integrity incident is always treated as critical.

## Prospective context dataset

Paper betting is also the moment SPORTS QUANT begins accumulating high-quality context history.

Persist immutable snapshots for:
- lineups
- injuries
- suspensions
- squad changes
- weather
- trusted contextual claims
- market movement

This dataset later enables honest evaluation of whether context features improve predictions.

## Real-money readiness review

Paper betting does not automatically authorize real-money use after N bets.

No minimum N is invented here.

A future readiness review must consider:
- calibration
- uncertainty
- predictive stability
- CLV
- paper ROI/yield
- drawdown
- sample size
- drift
- data reliability
- operational incidents
- model/market stability
- independent review

Result may still be:
- NO_GO
- GO_WITH_CONDITIONS
- GO

## Execution safety

V1:
- no automated real-money betting;
- no automatic staking;
- no martingale/chasing;
- manual execution only if a future governance review authorizes real-money decision support.

## Required tests

1. every decision snapshot immutable after cutoff.
2. settlement cannot mutate pre-event prediction fields.
3. losing and NO_BET decisions remain logged.
4. exact decision-time odds preserved.
5. CLV uses later closing data only for evaluation.
6. paper stake deterministic.
7. no loss-chasing logic.
8. model/version drift visible in reports.
9. provider outage reflected in decision state.
10. calibration metrics segment correctly.
11. drawdown/yield/ROI deterministic.
12. PIT incident raises critical monitoring condition.
13. prospective context snapshots preserve received_at/known_at.
14. regression tests for monitoring defects.

## Acceptance

F11 is operational when:
- live Football events can be evaluated prospectively;
- decisions are frozen before matches;
- settlements are attached afterward without mutation;
- monitoring dashboards/reports expose required metrics;
- context snapshots accumulate;
- drift/incident handling is testable;
- no real-money automation exists.

## Definition of Football "operational"

For SPORTS QUANT, Football becomes operational for paper betting when F2–F11 required Football scope is green and live prospective decisions are being recorded.

Real-money use is a later governance decision based on prospective evidence, not merely completion of software.
