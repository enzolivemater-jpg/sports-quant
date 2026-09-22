# F2 Contracts — Ready-to-Implement Specification

Date: 2026-09-22

Status: DRAFT_READY__BLOCKED_PENDING_INDEPENDENT_F0_REVIEW

Pilot sport: FOOTBALL

## Objective

Implement the smallest stable domain-contract layer required by all later SPORTS QUANT phases.

F2 must contain contracts and validation only. It must not implement ingestion, models, calibration algorithms, P_safe formulas, odds algorithms, optimizer logic, or frontend behavior.

## Package targets

Create domain contracts under `src/sports_quant/contracts/`.

Minimum modules:

- `common.py`
- `time.py`
- `source.py`
- `data_state.py`
- `entity.py`
- `provenance.py`
- `sports_intelligence.py`
- `market.py`
- `market_risk.py`
- `probability.py`
- `edge.py`
- `dependency.py`
- `gates.py`
- `decision.py`
- `reproducibility.py`
- `predictability.py`

Names may be adjusted during implementation only if semantics remain identical and the change is documented.

## Required canonical enums

### Source tier
- OFFICIAL
- LICENSED_PRO
- TRUSTED_SPECIALIST
- TRUSTED_JOURNALIST
- AGGREGATOR
- SOCIAL_UNVERIFIED

Legacy normalization must be explicit and tested for:
- LICENSED DATA -> LICENSED_PRO
- LICENSED PROFESSIONAL -> LICENSED_PRO
- SOCIAL -> SOCIAL_UNVERIFIED
- SOCIAL/UNVERIFIED -> SOCIAL_UNVERIFIED

### Data-state dimensions

These are orthogonal and must never be collapsed into one status.

Quality:
- VALID
- PARTIAL
- UNAVAILABLE
- ERROR

Freshness:
- LIVE
- RECENT
- DELAYED
- STALE
- SUPERSEDED

Verification:
- NOT_REQUIRED
- UNVERIFIED
- VERIFIED
- CROSS_CONFIRMED

Conflict:
- NONE
- OPEN
- RESOLVED

### Business decision state
- QUALIFIED
- WAIT
- REVIEW
- NO_BET
- BLOCKED

Precedence:
BLOCKED > REVIEW > WAIT > NO_BET > QUALIFIED

### Known-at basis
- SYSTEM_RECEIPT
- VERIFIED_SOURCE_AVAILABILITY

No speculative third basis may be introduced in F2.

### Sports Intelligence claim type
- FACT
- EXPERT_ASSESSMENT
- OPINION
- RUMOR
- CONFLICT

Invariants:
- FACT does not imply VERIFIED;
- structured Sports Intelligence may affect only approved channels;
- no claim or LLM/human interpretation may directly assign final P_safe.

Approved effect channels:
- VALIDATED_MODEL_FEATURES
- STRUCTURED_CONTEXT
- UNCERTAINTY
- REVIEW_STATE
- RESTRICTIONS
- GATES
- NO_BET_REASONS

### Market Risk
Classes:
- MR1
- MR2
- MR3
- MR4
- MR5
- MR6

Modes:
- CONSERVATIVE
- BALANCED
- AGGRESSIVE
- SPECULATIVE

Invariants:
- MR_base is ordinal/structural, not probability;
- MR_base does not directly modify P_safe;
- weighted_average_mr remains DEFERRED;
- composite Dynamic Market Risk remains DEFERRED.

### Dependency class
- independent
- weak
- moderate
- strong
- redundant
- contradictory

F2 defines the qualitative contract only. Quantitative dependency estimation remains later (OD-19/OD-23).

### Sport Predictability
- SP1
- SP2
- SP3
- SP4
- SP5

Evidence status:
- INSUFFICIENT
- PROVISIONAL
- VALIDATED
- DEGRADED

F2 must not assign empirical SP classes to sports.

## Temporal contract

Minimum timestamp fields:
- event_time
- published_at
- received_at
- valid_from
- valid_to
- expires_at
- known_at
- known_at_basis
- decision_cutoff_at

`known_at` definition:
earliest verifiable instant at which the information could legitimately be used by SPORTS QUANT.

Hard PIT validation:
- critical simulated information requires `known_at <= decision_cutoff_at`;
- missing defensible `known_at` must not silently become usable;
- timezone-aware timestamps only;
- no naive datetime accepted at domain boundary.

F2 defines validation semantics only. F3 implements the PIT kernel.

## Entity contract

Minimum concepts:
- sport;
- competition;
- season;
- event/match;
- team;
- participant/player;
- provider external identifier;
- canonical internal identifier.

Entity resolution implementation is later; F2 only defines identifiers and provenance-safe references.

## Provenance contract

Every material record must be able to retain:
- source/provider;
- source tier;
- external ID where relevant;
- received_at;
- known_at;
- known_at_basis;
- source/version reference when available;
- quality/freshness/verification/conflict states.

No implicit provenance defaults for critical data.

## Market contract

Canonical dimensions:
- sport;
- market_family;
- market_type;
- market_instance;
- MR_base.

Football currently approved:
Phase 1:
- FOOTBALL_1X2 / MR2
- FOOTBALL_TOTAL_GOALS_MAIN / MR2

Phase 2:
- FOOTBALL_ASIAN_HANDICAP / MR2
- FOOTBALL_BTTS / MR2
- FOOTBALL_TEAM_TOTALS / MR2

Basketball and MMA/UFC market catalogs remain NOT_DEFINED_DO_NOT_IMPLEMENT.

Handball, Volleyball and Tennis are approved for later empirical validation but F2 must not invent their production market catalogs.

## Probability contract

Keep separate:
- P_raw
- P_calibrated
- P_safe

Invariant:
`0 <= P_safe <= P_calibrated <= 1`

F2 must not define the production P_safe formula.

LLM/human direct final-P_safe assignment is prohibited.

## Edge contract

Keep separate:
- edge_calibrated = P_calibrated - P_market_no_vig
- edge_safe = P_safe - P_market_no_vig

Validation invariant:
- if edge_safe < 0, state cannot be QUALIFIED.

A stricter positive minimum edge remains unresolved.

## Gate contract

F2 defines the contract surface needed by later qualification logic without implementing the S-Tier engine.

Minimum concepts:
- gate identifier;
- gate evidence/reference payload;
- evaluated_at / decision_cutoff_at where applicable;
- deterministic reason code/string identifier;
- resulting business decision state or non-final gate outcome representation that does not contradict the canonical business states.

F2 must not:
- implement S-Tier thresholds;
- invent model-agreement thresholds;
- invent drift thresholds;
- invent Sport Predictability numeric gate thresholds;
- allow a failed critical gate to be overridden by an aggregate score.

## Reproducibility contract

Minimum version/reference concepts:
- code version / commit reference;
- dataset or snapshot reference;
- configuration version;
- model/calibrator/version references when applicable later;
- deterministic run/assessment identifier where applicable.

F2 defines identifiers and serializable references only. Backtest/run-manifest implementation belongs to later phases.

## PredictabilityAssessment contract

Required fields:
- assessment_version;
- sport;
- market_family;
- competition_optional;
- predictability_prior;
- predictability_empirical;
- evidence_status;
- oos_brier;
- oos_log_loss;
- oos_ece;
- oos_skill;
- sample_sizes;
- evaluation_period;
- stability;
- data_quality;
- drift;
- baseline_scope;
- model_scope;
- dataset_version_or_snapshot;
- code_version;
- known_at.

Must be versioned, immutable and PIT-retrievable.

F2 must not define arbitrary numeric SP scores or empirical admission thresholds.

## Tests required before F2 is green

At minimum:

1. exact enum round-trip tests;
2. legacy source normalization tests;
3. rejection of unknown canonical enum values;
4. timezone-aware timestamp tests;
5. PIT invariant tests around `known_at` and `decision_cutoff_at`;
6. missing-known_at critical-data rejection test;
7. independence of the four data-state axes;
8. probability bound tests;
9. `P_safe <= P_calibrated` tests;
10. edge-calculation contract tests;
11. negative-edge cannot-QUALIFIED test;
12. business-state precedence tests;
13. Sports Intelligence claim-type/effect-channel contract tests;
14. Market Risk class/mode and non-probability contract tests;
15. dependency-class round-trip tests;
16. gate-contract serialization/reason-code tests without S-Tier logic;
17. reproducibility-reference serialization tests;
18. PredictabilityAssessment required-field tests;
19. immutable/versioned assessment behavior tests;
20. serialization/reproducibility tests;
21. regression tests for every corrected contract defect.

## Explicit non-goals

F2 does not:
- select Football model champion;
- fetch provider data;
- create features;
- implement Poisson/Dixon-Coles/Elo/ML;
- calibrate probabilities;
- implement production P_safe;
- calculate no-vig;
- run backtests;
- implement S-Tier;
- implement optimizer;
- build API endpoints or PWA.

## Acceptance

F2 can be marked technically green only when:
- all contract tests pass;
- lint/type/security checks pass;
- no F3+ implementation leaks in;
- canonical YAML and code contracts are semantically consistent;
- an independent critical review is requested for contract-sensitive changes.

Promotion beyond F2 still follows project governance.
