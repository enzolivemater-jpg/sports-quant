# CURRENT TASK

Phase:
`F2_DOMAIN_CONTRACTS`

Status:
`AUTHORIZED_PENDING_GREEN_AUTHORIZATION_HEAD`

Date:
2026-09-22

## F0 governance

Independent F0 review cycle is complete.

Final reviewed HEAD:
`e5220707b018dee501a2a9757c3e31d5bb41683a`

Final review result:
- P0 open: 0
- P1 open: 0
- blocking_findings_cleared: true
- final status: GO
- explicit authorization: F2 MAY BEGIN

Canonical review record:
`.project/reviews/F0_REVIEW_RECORD_2026-09-22_e5220707.md`

Verbatim micro-review:
`.project/reviews/F0_CI_HISTORY_MICRO_REREVIEW_RAW_2026-09-22_e5220707.md`

## Machine state

- foundation_review.status = PASS
- f2.authorized = true

Before implementation begins, the authorization commit itself must pass:
- CI
- Security
- phase-gate validation

If it fails, F2 implementation must not start until corrected.

## F2 implementation

Primary handoff:
`.ai/handoffs/CLAUDE_F2_IMPLEMENTATION_HANDOFF.md`

Primary spec:
`docs/contracts/F2_READY_TO_IMPLEMENT_SPEC.md`

Scope:
domain-contract layer only.

Do not start F3 in the same change.

## Completion discipline

F2 must:
- preserve all OPEN_DECISIONS;
- implement only approved contracts;
- pass formatter/Ruff/mypy/pytest/Alembic/PostgreSQL/CI/Security;
- receive independent critical review;
- have no unresolved P0/P1 before F3.

## Parallel work

Issue #17:
repository privacy / main protection remains admin work.

Issue #18:
provider trials/credentials remain relevant for later F4 work.
