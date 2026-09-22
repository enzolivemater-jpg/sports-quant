# F6 Football Market Engine — Draft Ready Specification

Date: 2026-09-22

Status: DRAFT_READY__BLOCKED_BY_PREVIOUS_PHASES

Pilot sport: FOOTBALL

Canonical basis:
- MARKET_AND_PARLAY_POLICY.md
- MARKET_RISK_TAXONOMY.md
- FOUNDATION_DECISIONS_v0.1

## Objective

Convert point-in-time bookmaker odds into transparent market probabilities, remove bookmaker margin, preserve market provenance, and expose market benchmarks for Football Phase 1.

## Initial market scope

Football Phase 1 only:
- FOOTBALL_1X2 / MR2
- FOOTBALL_TOTAL_GOALS_MAIN / MR2

No player props, exact scores, goalscorers or micro-markets in the first milestone.

## Inputs

Every market observation must include:
- canonical_event_id
- bookmaker
- market_family
- market_type
- market_instance
- outcome
- decimal_odds
- provider_snapshot_at
- known_at
- decision_cutoff_at
- source/provenance
- data-state dimensions

## Implied probability

For decimal odds:

`p_implied_raw = 1 / decimal_odds`

Validate:
- odds > 1.0 for standard decimal-bookmaker observations unless a provider schema explicitly documents another representation;
- no silent conversion from malformed values;
- provider formats normalized before domain calculation.

## Overround

For a mutually exclusive exhaustive outcome set:

`overround = sum(p_implied_raw_i) - 1`

The engine must preserve:
- bookmaker-level overround;
- timestamp;
- market instance.

Do not average odds before measuring each book's margin.

## No-vig

OD-07 remains OPEN.

F6 must implement an extensible no-vig interface and at least one transparent baseline method for research, but no method becomes canonical Champion without validation.

Candidate methods may include:
- proportional normalization;
- later validated alternatives.

For proportional baseline:

`p_market_no_vig_i = p_implied_raw_i / sum(p_implied_raw_j)`

This baseline is not automatically the final production no-vig method.

## Consensus

Market consensus may combine multiple bookmakers only after:
- each book is individually normalized;
- stale observations are excluded or flagged;
- market instances are aligned;
- outcome labels are canonicalized.

Consensus algorithm remains subject to validation.

Required metadata:
- contributing bookmakers
- observation times
- book count
- dispersion
- consensus method/version

## Opening / current / closing

Preserve distinct concepts:
- opening observation
- decision-cutoff observation
- closing observation

Closing odds are evaluation data for CLV and must never leak into an earlier decision.

## Edge outputs

Canonical definitions:

`edge_calibrated = P_calibrated - P_market_no_vig`

`edge_safe = P_safe - P_market_no_vig`

Invariant:
- edge_safe < 0 => cannot be QUALIFIED.

F6 can expose calculations once probability inputs exist but does not define P_safe.

## Market risk

Football Phase 1:
- 1X2 = MR2
- main total goals = MR2

MR_base is structural only.

It must not:
- modify P_safe directly;
- act as probability;
- bypass calibration;
- create arbitrary numeric probability penalties.

Composite dynamic Market Risk Score and weighted_average_mr remain DEFERRED.

## Snapshot selection

All market inputs must pass F3 PIT.

For a decision cutoff:
- select only market observations known at/before cutoff;
- later odds must not be visible;
- nearest-before selection semantics must be explicit;
- staleness must be reported.

## Bookmaker identity

Normalize bookmaker IDs/names while preserving original provider identifiers.

Do not merge brands/entities without deterministic mapping evidence.

## Required diagnostics

Per market snapshot:
- raw implied probabilities
- overround
- no-vig probabilities
- bookmaker count
- market dispersion if consensus used
- age/staleness
- source lineage
- market risk class
- exact cutoff

## Required tests

1. decimal odds -> implied probability.
2. valid overround on 1X2.
3. proportional no-vig sums to 1 within tolerance.
4. malformed odds rejected.
5. missing outcome set cannot silently produce valid no-vig.
6. later snapshot excluded at earlier cutoff.
7. closing price never available to pre-close decision.
8. bookmaker normalization deterministic.
9. stale source state propagated.
10. edge_calibrated formula exact.
11. edge_safe formula exact.
12. negative edge_safe cannot qualify.
13. MR2 does not alter probability values.
14. consensus never mixes different market instances.
15. reproducible output from fixed inputs.

## Explicit non-goals

F6 does not:
- choose final no-vig Champion under OD-07;
- define P_safe;
- select bets;
- calculate parlays;
- infer bookmaker efficiency as truth;
- use closing odds as model inputs for earlier decisions.

## Acceptance

F6 first milestone is green when:
- Phase 1 odds can be reconstructed at fixed cutoffs;
- no-vig baseline works and is versioned;
- overround diagnostics are stored;
- market provenance is complete;
- edge calculations are exact when supplied calibrated/safe probabilities;
- PIT tests exclude future odds;
- closing-price leakage tests pass.
