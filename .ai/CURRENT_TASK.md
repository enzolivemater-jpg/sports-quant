# CURRENT TASK

Phase:
`F2_DOMAIN_CONTRACTS`

Status:
`READY_TO_IMPLEMENT__F0_GATE_PASSED`

Date:
2026-09-22

## Governance gate

Independent F0 review is complete and accepted.

Reviewed HEAD:
`d4d6c0ce4d26f42183312b6386b7d0e00ab46f88`

Review result:
- P0 open: 0
- P1 open: 0
- blocking_findings_cleared: true
- final status: GO
- explicit authorization: F2 MAY BEGIN

Machine state:
- foundation_review.status = PASS
- f2.authorized = true

Accepted machine-readable review record:
`.project/reviews/F0_REVIEW_RECORD_2026-09-22_d4d6c0ce.md`

Verbatim final reviewer report:
`.project/reviews/F0_FINAL_REREVIEW_RAW_2026-09-22_d4d6c0ce.md`

## Current implementation task

Implement F2 domain contracts only.

Primary handoff:
`.ai/handoffs/CLAUDE_F2_IMPLEMENTATION_HANDOFF.md`

Primary spec:
`docs/contracts/F2_READY_TO_IMPLEMENT_SPEC.md`

Do not start F3 in the same change.

## Required completion discipline

F2 must:
- stay within the contract layer;
- preserve all OPEN_DECISIONS;
- pass formatter/Ruff/mypy/pytest/Alembic/PostgreSQL/CI/Security;
- receive critical review;
- have no unresolved P0/P1 before F3.

## Parallel work

Issue #17:
repository hardening remains an admin action.

Issue #18:
provider trial credentials remain relevant for later Football provider bake-off/F4.

These no longer block starting F2.
