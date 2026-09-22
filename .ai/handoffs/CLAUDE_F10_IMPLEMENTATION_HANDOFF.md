# Claude Pro Handoff — F10 Dependency and Parlay Optimizer

Status: READY_AFTER_SINGLE_LEG_STACK_AND_F9
Issue: #13

Implement:
`docs/contracts/F10_DEPENDENCY_PARLAY_OPTIMIZER_SPEC_DRAFT.md`

Objective:
build parlays only from already-qualified legs.

Hard rules:
- failed S-Tier leg never enters optimizer
- main combined P_safe >= 50%
- no naive product unless independence is justified
- strong/redundant/contradictory dependence handled explicitly
- no odds-only objective
- no forced leg count
- NO_BET is valid
- weighted_average_mr remains DEFERRED
- composite Dynamic Market Risk remains DEFERRED

Keep OD-18 through OD-23 open until validated.

Required output:
legs, individual/combined P_safe, joint method, odds, P/L/R, MR summary, dependency profile, marginal contribution, mono/multi marker, reason codes.

Start transparent enumeration/pruning before adding OR-Tools unless complexity actually requires it.

Tests:
candidate-pool gate, P50 main-mode boundary, dependency handling, contradictory rejection, full recalculation on added leg, MR summary, mono/multi comparison, deterministic NO_BET behavior.

Do not invent dependency thresholds or solver decisions.
