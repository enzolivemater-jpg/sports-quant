# CURRENT TASK

Phase:
`F4_FOOTBALL_DATA_LAYER`

Status:
`READY_TO_IMPLEMENT`

Date:
2026-10-02

## F0 governance

F0 independent review is complete and the gate is closed successfully.

Final independently reviewed HEAD:
`e5220707b018dee501a2a9757c3e31d5bb41683a`

Final review result:
- P0 open: 0
- P1 open: 0
- blocking_findings_cleared: true
- final status: GO
- explicit authorization: F2 MAY BEGIN

Final authorization commit:
`eed1e41f0b045b8d11e38770b032f8e802a02a64`

Authorization-head validation:
- CI: SUCCESS
- Security: SUCCESS
- phase gate: SUCCESS
- PostgreSQL integration: SUCCESS

Machine state:
- foundation_review.status = PASS
- f2.authorized = true

Issue #1:
CLOSED

## F2 completion

F2 Domain Contracts is complete, merged and green.

Final F2 PR:
#19

Final independently reviewed HEAD:
`40a604d9e5ec3e3f2fe0528373f0313874667e8c`

Merge commit on main:
`d2cc02b5f5fbfbef2100eb07395e652a731bb31d`

Final review result:
- independent review: GO
- P0 open: 0
- P1 open: 0

Merge-commit validation:
- CI quality: SUCCESS
- PostgreSQL integration: SUCCESS
- Security dependency audit: SUCCESS
- Security secret scan: SUCCESS

Security prerequisite:
PR #20 (Gitleaks v3 PR scanning), merged at `b94eefdf2d6c2d54e4a2fe2c6c9910ba859bebd4`

Issue #2:
CLOSED (completed)

OD-01 through OD-29:
UNCHANGED

## F3 completion

F3 Point-in-Time Kernel is complete, merged and green.

Final F3 PR:
#22

Final independently reviewed HEAD:
`43a15d88b5a5837c54057f26aa50c9b1f1b2e497`

Merge commit on main:
`3304c17d1204ec835a6ef21bb2845639b93cd33f`

Final review result:
- independent review: GO
- P0 open: 0
- P1 open: 0

Merge-commit validation:
- CI quality: SUCCESS
- PostgreSQL integration: SUCCESS
- Security dependency audit: SUCCESS
- Security secret scan: SUCCESS

Canonical PIT policy:
`.project/POINT_IN_TIME_POLICY.yaml` status = `APPROVED_F3_POLICY`

Issue #6:
CLOSED (completed)

OD-01 through OD-29:
UNCHANGED

Recorded F4 authorization (`.project/PHASE_GATES.toml`):
- current_phase = F4_FOOTBALL_DATA_LAYER
- [f4] authorized = true

Note: F3 and F4 authorization are recorded in `.project/PHASE_GATES.toml` but are not independently machine-enforced by `scripts/validate_phase_gates.py`.

## Active implementation task

Issue:
#7 — F4 Football Data Layer

Primary handoff:
`.ai/handoffs/CLAUDE_F4_IMPLEMENTATION_HANDOFF.md`

Primary spec:
`docs/contracts/F4_FOOTBALL_DATA_LAYER_SPEC_DRAFT.md`

## F4 objective

Build the first provider-backed, provenance-complete, PIT-safe Football data layer on
top of the F2 contracts and the F3 PIT kernel (never bypassing or redefining either):

provider -> immutable raw capture -> provider normalization -> canonical Football records
-> F3 PIT materialization -> feature-ready dataset

Football remains the first end-to-end pilot.

## Phase 1 market scope

Phase 1 markets ONLY:
- `FOOTBALL_1X2`
- `FOOTBALL_TOTAL_GOALS_MAIN`

No Phase 2 Football market implementation.

## Provider boundaries

OD-24 remains OPEN.

No provider is approved by this transition.

- StatsBomb Open Data: `VERIFIED_RESEARCH_SANDBOX` only. It is NOT an approved
  production provider, NOT an EPL 2024/25 provider, and NOT a standalone historical
  context PIT source.
- The Odds API: candidate historical odds provider only.
- API-Football / Sportmonks / Sportradar: candidates only.

No provider preference is resolved here. Any adapter built before OD-24 is resolved
stays experimental with an explicit provider role and must not hardwire architecture
to that provider.

## Hard boundaries

Do not implement:
- Football feature engineering beyond validated materialization plumbing;
- model training / Champion selection;
- calibration algorithms;
- a production P_safe formula;
- no-vig;
- S-Tier engine;
- backtest metrics;
- parlay optimizer;
- API/frontend.

Do not resolve any OPEN_DECISION silently.

## Completion discipline

F4 must:
- preserve OD-01 through OD-29;
- materialize PIT views through F3 only (no provider-specific as-of shortcut);
- pass formatter/Ruff/mypy/pytest/Alembic/PostgreSQL/CI/Security;
- satisfy the F4 acceptance criteria, including deterministic rebuild from fixed raw snapshots;
- keep credentials out of the repository and logs;
- receive independent critical review;
- have no unresolved P0/P1 before F5.

Do not start F5 in the same change.

## Parallel non-blocking work

Issue #17:
repository privacy / main protection remains admin work.

Issue #18:
provider trials/credentials — now relevant for F4 provider work.
