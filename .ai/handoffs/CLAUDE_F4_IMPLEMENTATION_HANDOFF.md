# Claude Pro Handoff — F4 Football Data Layer

Date: 2026-09-22

Status: READY_TO_IMPLEMENT

Repository: `enzolivemater-jpg/sports-quant`
Implementation issue: #7

## Start condition

Do not begin unless:
- F0 review gate passed;
- F2 merged/accepted;
- F3 merged/accepted;
- current main CI/Security green;
- no unresolved P0/P1 in PIT contracts.

### Start condition status (recorded 2026-10-02)

SATISFIED by:
- F0 review gate passed (`foundation_review.status = PASS`, issue #1 closed);
- F2 merged/accepted (PR #19, merge commit `d2cc02b5f5fbfbef2100eb07395e652a731bb31d`, review GO, P0=0, P1=0);
- F3 merged/accepted (PR #22, final reviewed head `43a15d88b5a5837c54057f26aa50c9b1f1b2e497`, merge commit `3304c17d1204ec835a6ef21bb2845639b93cd33f`, independent review GO, issue #6 closed);
- current main green (quality, postgres-integration, dependency-audit, secret-scan: SUCCESS on `3304c17d1204ec835a6ef21bb2845639b93cd33f`);
- no unresolved F3 P0/P1 (P0=0, P1=0);
- PIT policy approved (`.project/POINT_IN_TIME_POLICY.yaml` status `APPROVED_F3_POLICY`).

Machine record: `[f4] authorized = true` in `.project/PHASE_GATES.toml` (recorded, not independently machine-enforced by `scripts/validate_phase_gates.py`).

This transition approves no provider. OD-24 remains OPEN. Existing provider status is unchanged:
- StatsBomb Open Data: `VERIFIED_RESEARCH_SANDBOX` only — not an approved production provider, not an EPL 2024/25 provider, not a standalone historical context PIT source;
- The Odds API: candidate historical odds provider only;
- API-Football / Sportmonks / Sportradar: candidates only.

## Primary spec

Implement:
`docs/contracts/F4_FOOTBALL_DATA_LAYER_SPEC_DRAFT.md`

Read first:
- `docs/research/FOOTBALL_PROVIDER_BAKEOFF_PLAN_v0.1.md`
- `docs/research/FOOTBALL_PROVIDER_EVIDENCE_MATRIX_v0.1.md`
- `docs/research/FOOTBALL_PILOT_DATASET_MANIFEST_v0.1.md`
- `docs/research/FOOTBALL_FEATURE_GOVERNANCE_v0.1.md`
- `docs/research/FOOTBALL_PIT_ACCELERATION_STRATEGY.md`
- `docs/research/STATSBOMB_OPEN_EPL_2015_16_PROBE.md`

## Objective

Build the first provider-backed, provenance-complete, PIT-safe Football data layer.

Flow:
provider -> immutable raw capture -> provider normalization -> canonical records -> F3 PIT materialization -> feature-ready dataset

## Required first milestone

Implement only enough to prove:
- one fixture/results source;
- one historical Phase 1 odds source OR an explicit evidence-backed block;
- deterministic EPL sample rebuild;
- entity mapping;
- raw-to-canonical lineage;
- F3 replay on mutable/history-aware records;
- missing/conflict/revision handling.

## Provider discipline

OD-24 remains authoritative.

Do not silently approve a vendor because its adapter is easiest to code.

If Gemini/provider bake-off has not resolved a role:
- keep adapter experimental;
- make provider role explicit;
- do not hardwire architecture to it.

## Football scope

Phase 1 only:
- FOOTBALL_1X2
- FOOTBALL_TOTAL_GOALS_MAIN

Do not implement player props, exact score, goalscorer, micro-markets.

## Required zones

- raw immutable snapshot layer
- normalized provider layer
- canonical domain layer
- PIT materialization through F3 only

No provider-specific as-of shortcut.

## Entity resolution

Must preserve:
- provider external IDs
- canonical IDs
- mapping source/method
- aliases
- review/confidence state where applicable

Never fuzzy-merge solely by name.

## Missingness

Never silently replace missing with zero.

Differentiate:
- unavailable
- unsupported
- not-yet-published
- parse error
- true zero

## Corrections

Provider correction creates new version/supersession lineage.
Never destructive-overwrite a historical decision-critical version when avoidable.

## Required tests

At minimum:
- raw -> normalized parse
- normalized -> canonical mapping
- external-ID preservation
- raw lineage preservation
- duplicate fixture handling
- conflict handling
- missing != zero
- odds bookmaker/time granularity
- correction/version behavior
- F3 excludes later revisions
- deterministic rebuild from fixed raw snapshots
- source taxonomy mapping
- unsupported field state
- malformed payload visible failure
- no secrets in repo/logs

## Secrets

API credentials only through env/secret store.
Do not commit or print secrets.

## Non-goals

Do not:
- choose model Champion
- implement calibration/P_safe
- implement S-Tier
- implement parlay
- build frontend

## Completion

TECHNICALLY_GREEN only if:
- accepted minimum provider path works
- deterministic pilot dataset rebuild works
- lineage complete
- PIT tests green
- CI/Security green
- no F5+ model logic leaks in
- critical review requested

Do not start F5 in same PR.
