# CURRENT TASK

Phase:
`F3_POINT_IN_TIME_KERNEL`

Status:
`READY_TO_IMPLEMENT`

Date:
2026-09-23

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

Machine state:
- current_phase = F3_POINT_IN_TIME_KERNEL
- f3.authorized = true

## Active implementation task

Issue:
#6 — F3 Point-in-Time Kernel

Primary handoff:
`.ai/handoffs/CLAUDE_F3_IMPLEMENTATION_HANDOFF.md`

Primary spec:
`docs/contracts/F3_POINT_IN_TIME_KERNEL_SPEC_DRAFT.md`

## F3 scope

Implement reusable, sport-agnostic, deterministic point-in-time logic on top of the
F2 contracts (never redefining them locally):
- PIT eligibility with explicit rejection reasons;
- as-of version selection;
- validity-window enforcement;
- deterministic historical revision selection;
- snapshot/replay manifest;
- timezone-safe handling;
- raw snapshot lineage hooks.

Football is the first consumer.

## Hard boundaries

Do not implement:
- provider fetching/ingestion;
- Football feature engineering;
- model training;
- calibration algorithms;
- a production P_safe formula;
- no-vig;
- S-Tier engine;
- backtest metrics;
- parlay optimizer;
- API/frontend.

Do not resolve any OPEN_DECISION silently.

## Completion discipline

F3 must:
- preserve OD-01 through OD-29;
- pass formatter/Ruff/mypy/pytest/Alembic/PostgreSQL/CI/Security;
- satisfy the F3 acceptance criteria, including deterministic replay;
- introduce no speculative timestamps;
- receive independent critical review;
- have no unresolved P0/P1 before F4.

Do not start F4 in the same change.

## Parallel non-blocking work

Issue #17:
repository privacy / main protection remains admin work.

Issue #18:
provider trials/credentials remain relevant for later F4 work.
