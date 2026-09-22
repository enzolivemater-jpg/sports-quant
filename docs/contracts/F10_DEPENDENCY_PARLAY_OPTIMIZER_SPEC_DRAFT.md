# F10 Dependency and Parlay Optimizer — Draft Ready Specification

Date: 2026-09-22

Status: DRAFT_READY__DEPENDENCY_METHODS_DEFERRED

Pilot sport: FOOTBALL initially; architecture reusable across approved sports.

Canonical basis:
- MARKET_AND_PARLAY_POLICY.md
- MARKET_RISK_TAXONOMY.md
- NO_BET_AND_RISK_POLICY.md
- FOUNDATION_DECISIONS_v0.1

## Objective

Construct parlays only from already-qualified legs and optimize the probability/risk/return profile without assuming independence when it is not defensible.

NO_BET remains a valid optimizer output.

## Preconditions

A leg may enter the candidate pool only if:
- selection-level S-Tier gate passes;
- P_safe exists from approved pipeline;
- edge_safe satisfies current policy;
- market is available/legal;
- data/calibration/PIT/context requirements pass.

Optimizer cannot rescue a failed selection.

## Dependency classes

Canonical qualitative classes:
- independent
- weak
- moderate
- strong
- redundant
- contradictory

Exact quantitative estimation method remains OD-19.

## Independence rule

Never compute combined probability as:

`prod(P_safe_i)`

unless independence is justified for that exact set of legs.

For dependent legs use later validated:
- conditional models;
- empirical joint distributions;
- copula/joint models where justified;
- Monte Carlo;
- other approved dependency method.

OD-23 remains open for exact joint/Monte-Carlo method.

## Main parlay probability rule

Main mode requires:
- combined P_safe >= 50%.

Do not manipulate uncertainty or leg count to force this threshold.

If no candidate combination meets requirements:
- NO_BET.

## Leg-count classes

- L1: 2–5
- L2: 6–7
- L3: 8–10
- L4: 11–15
- L5: 16–20
- L6: 21+

Leg count is not an objective.

Every added leg must improve the combined profile sufficiently under future validated marginal-value criteria.

OD-20 remains open for exact marginal-value rule.

## Return classes

Combined decimal odds:
- R1: <2
- R2: 2–3
- R3: 3–5
- R4: 5–10
- R5: 10–20
- R6: 20+

Higher R is not inherently better.

The optimizer must not maximize odds alone.

## Probability class

Combined output classified from combined P_safe:
- P90
- P80
- P70
- P60
- P50
- P40 Watchlist
- P25 Speculative
- Reject

Main mode cannot qualify below P50.

## Market Risk constraints

Use structural MR only as currently canonical.

Parlay summary:
- max_mr
- count_by_mr
- count_mr4_plus
- market_risk_mode
- dependency_profile

Do NOT implement:
- weighted_average_mr
- composite Dynamic Market Risk Score

Both remain deferred.

## Market Risk modes

### CONSERVATIVE
Default research constraint:
- prioritize MR1–MR2;
- higher MR only if later explicitly authorized.

### BALANCED
- may include MR3;
- limited higher-risk exposure subject to validated rules.

### AGGRESSIVE
- may consider up to MR4 under stricter controls.

### SPECULATIVE
- explicit separate mode;
- must not weaken calibration/PIT/edge/data gates.

Exact additional mode limits remain OD-18.

## Mono-sport vs multi-sport

Generate and compare:
- best valid mono-sport parlay
- best valid multi-sport parlay

Prefer mono-sport when quality/performance is comparable.

Allow multi-sport only when it materially improves the probability/risk/return profile.

OD-21 remains open for exact "significant improvement" threshold.

## Objective function

No single scalar objective is canonically approved yet.

Candidate search must preserve a Pareto-style view over:
- combined P_safe
- uncertainty
- edge profile
- return
- dependency
- MR profile
- data/calibration quality

Do not collapse all dimensions into an arbitrary weighted score.

## Solver

OD-22 remains open.

OR-Tools may be considered later but is not required until search complexity justifies it.

Start with transparent enumeration/pruning when candidate set is small enough.

## Marginal leg analysis

For each candidate addition report:
- change in combined P_safe
- change in return class/odds
- dependency impact
- MR impact
- uncertainty impact
- whether qualification is preserved

A leg that worsens the profile without sufficient validated benefit is rejected.

## Re-ranking

Top candidates may undergo:
- Monte Carlo
- joint-model evaluation
- scenario analysis

only after the dependency method is validated.

## Contradictory / redundant legs

Contradictory:
- reject unless the market structure explicitly makes them jointly coherent.

Redundant:
- do not count duplicated expression of the same underlying event as diversification;
- model joint dependence explicitly.

## Required output

For each proposed parlay:
- leg identities
- individual P_safe
- combined P_safe
- method used for joint probability
- combined odds
- P/L/R classification
- MR summary
- dependency class/profile
- marginal contribution per leg
- data/calibration evidence references
- reason codes
- mono/multi-sport marker

## Required tests

1. failed S-Tier leg never enters candidate pool.
2. main-mode combined P_safe <50% rejected.
3. independent product used only when independence flag is justified.
4. strong/redundant dependency cannot silently use naive multiplication.
5. contradictory pair rejected.
6. adding leg recalculates full joint profile.
7. odds-maximization alone cannot select output.
8. no forced target leg count.
9. L/R/P boundaries exact.
10. MR summary exact without weighted_average_mr.
11. mono and multi candidates both evaluated when available.
12. NO_BET returned when no valid combination exists.
13. deterministic search from same candidate set/config.
14. regression tests for dependency bugs.

## Backtest requirements

Parlay backtests must report separately:
- L1 through L6
- mono-sport vs multi-sport
- dependency classes
- P class
- R class
- MR profile

Do not pool all parlays into one ROI number.

## Explicit open decisions

Remain open:
- OD-18 additional MR mode limits
- OD-19 dependency quantification method
- OD-20 marginal leg value criterion
- OD-21 significant multi-sport improvement threshold
- OD-22 solver
- OD-23 joint model / Monte Carlo method

## Acceptance

F10 is green only when:
- dependency assumptions are explicit;
- naive independence is impossible for non-approved pairs;
- main P_safe >=50% enforced;
- optimizer can return NO_BET;
- no arbitrary scalar score overrides critical dimensions;
- all open quantitative decisions remain visibly unresolved until validated.
