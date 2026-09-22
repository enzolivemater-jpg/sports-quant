# Claude Pro Handoff — F2 Contracts

Date: 2026-09-22

Status: READY_TO_START_ONLY_AFTER_F0_REVIEW_GATE_PASSES

Repository: `enzolivemater-jpg/sports-quant`
Implementation issue: #2
Pilot sport: FOOTBALL

## Start condition

Do not begin implementation unless:
1. GitHub issue #1 contains an independent F0 review;
2. no unresolved P0/P1 blocks F2;
3. any required corrections from the review are merged;
4. current `main` CI and Security are green.

If the review returns NEEDS_DECISION, STOP and escalate to Enzo.

## Primary implementation spec

Read and implement exactly:
- `docs/contracts/F2_READY_TO_IMPLEMENT_SPEC.md`

Also read before coding:
- `.project/FOUNDATION_DECISIONS_v0.1.yaml`
- `.project/OPEN_DECISIONS.yaml`
- `.project/SPORT_PREDICTABILITY_POLICY.yaml`
- `.project/PROJECT_PROFILE.yaml`
- `docs/adr/ADR-0001-foundation-v0.1.md`
- `docs/adr/ADR-0002-mandatory-sports-scope.md`
- `docs/adr/ADR-0003-additional-sports-allowlist.md`
- `docs/adr/ADR-0004-football-first-pilot.md`
- `docs/runbooks/FAST_EXECUTION_PLAN.md`
- `.ai/AI_CHARTER.md`
- `.ai/AI_DECISIONS.md`

## Implementation objective

Implement the smallest stable domain-contract layer required by later phases.

F2 is contracts + validation only.

Do NOT implement:
- provider ingestion
- PIT kernel logic beyond contract-level validation
- feature engineering
- Football models
- calibration algorithms
- production P_safe formula
- no-vig engine
- S-Tier engine
- backtests
- dependency/parlay logic
- API endpoints
- frontend

## Required modules

Create under `src/sports_quant/contracts/`:
- `common.py`
- `time.py`
- `source.py`
- `data_state.py`
- `entity.py`
- `provenance.py`
- `market.py`
- `probability.py`
- `edge.py`
- `decision.py`
- `predictability.py`

Module names may change only if semantics remain identical and the change is documented.

## Canonical invariants to encode

### Source taxonomy
- OFFICIAL
- LICENSED_PRO
- TRUSTED_SPECIALIST
- TRUSTED_JOURNALIST
- AGGREGATOR
- SOCIAL_UNVERIFIED

Legacy normalization:
- LICENSED DATA -> LICENSED_PRO
- LICENSED PROFESSIONAL -> LICENSED_PRO
- SOCIAL -> SOCIAL_UNVERIFIED
- SOCIAL/UNVERIFIED -> SOCIAL_UNVERIFIED

### Data-state axes
Keep four independent dimensions:
- quality
- freshness
- verification
- conflict

Never collapse them into one enum/status.

### Time
At domain boundaries:
- timezone-aware datetimes only
- reject naive datetimes
- known_at remains explicit
- critical information without defensible known_at is not silently PIT-eligible
- F2 defines validation semantics; F3 will implement as-of selection/replay

### Probability
Keep separate:
- P_raw
- P_calibrated
- P_safe

Invariant:
`0 <= P_safe <= P_calibrated <= 1`

No human/LLM direct setter for final P_safe.

Do not invent the production P_safe formula.

### Edge
- edge_calibrated = P_calibrated - P_market_no_vig
- edge_safe = P_safe - P_market_no_vig

If edge_safe < 0, QUALIFIED must be impossible at the contract/state-validation level.

Do not invent a stricter positive edge threshold.

### Decision states
- QUALIFIED
- WAIT
- REVIEW
- NO_BET
- BLOCKED

Precedence:
BLOCKED > REVIEW > WAIT > NO_BET > QUALIFIED

### Market scope
Football Phase 1:
- FOOTBALL_1X2 / MR2
- FOOTBALL_TOTAL_GOALS_MAIN / MR2

Football Phase 2:
- FOOTBALL_ASIAN_HANDICAP / MR2
- FOOTBALL_BTTS / MR2
- FOOTBALL_TEAM_TOTALS / MR2

Do not invent Basketball or MMA/UFC market catalogs.

### Sport Predictability
Implement the contract shape, not empirical scores.

Assessment must support:
- assessment_version
- sport
- market_family
- optional competition
- predictability_prior
- predictability_empirical
- evidence_status
- oos_brier
- oos_log_loss
- oos_ece
- oos_skill
- sample_sizes
- evaluation_period
- stability
- data_quality
- drift
- baseline_scope
- model_scope
- dataset_version_or_snapshot
- code_version
- known_at

Must be versionable/serializable and compatible with later immutable PIT retrieval.

Do not invent:
- numeric SP scoring
- empirical admission thresholds
- parlay SP aggregation

## Required tests before asking for review

At minimum:
1. exact enum round-trip
2. legacy source normalization
3. unknown canonical enum rejection
4. timezone-aware timestamp validation
5. known_at/cutoff contract validation
6. missing known_at critical-data rejection
7. four data-state axes remain independent
8. probability bounds
9. P_safe <= P_calibrated
10. edge formulas
11. negative edge cannot QUALIFIED
12. decision precedence
13. PredictabilityAssessment required fields
14. assessment serialization/version behavior
15. deterministic serialization/reproducibility
16. regression tests for any defect fixed during implementation

## Engineering quality

Run and keep green:
- formatter
- Ruff
- mypy
- pytest
- Alembic heads
- PostgreSQL smoke if repository workflow requires it
- secret scan
- dependency audit

Do not weaken CI to make the implementation pass.

## Commit / PR behavior

Prefer one focused F2 branch/PR.

PR description must include:
- scope implemented
- tests added
- explicit non-goals
- any divergence from spec
- any unresolved issue
- confirmation that OD-01..OD-29 were not silently resolved
- confirmation no F3+ logic was implemented

If a canonical contradiction is discovered:
- do not guess
- do not silently reinterpret
- mark NEEDS_DECISION
- identify exact conflicting sources
- stop the affected implementation path

## Completion condition

F2 may be proposed as TECHNICALLY_GREEN only if:
- spec is implemented
- required tests pass
- CI/Security pass
- no F3+ leakage
- canonical YAML and code semantics match
- independent review is requested for critical contract changes

Claude must not be the sole critical reviewer of its own F2 implementation.

## Next phase

Do not implement F3 in the same change.

After F2 is merged and independently reviewed/accepted, hand off to:
`docs/contracts/F3_POINT_IN_TIME_KERNEL_SPEC_DRAFT.md`
