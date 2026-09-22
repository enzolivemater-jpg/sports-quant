# CURRENT TASK

Phase:
`F2_DOMAIN_CONTRACTS`

Status:
`READY_TO_IMPLEMENT`

Date:
2026-09-22

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

## Active implementation task

Issue:
#2 — F2 Domain Contracts

Primary handoff:
`.ai/handoffs/CLAUDE_F2_IMPLEMENTATION_HANDOFF.md`

Primary spec:
`docs/contracts/F2_READY_TO_IMPLEMENT_SPEC.md`

## F2 scope

Implement the smallest stable domain-contract layer only.

Expected modules under `src/sports_quant/contracts/`:
- common.py
- time.py
- source.py
- data_state.py
- entity.py
- provenance.py
- market.py
- probability.py
- edge.py
- decision.py
- predictability.py

Follow the handoff/spec if they include additional contract modules already approved.

## Hard boundaries

Do not implement:
- provider ingestion;
- F3 PIT kernel beyond contract validation;
- Football feature engineering;
- model training;
- calibration algorithms;
- a production P_safe formula;
- no-vig Champion;
- S-Tier engine;
- backtests;
- parlay optimizer;
- API/frontend.

Do not resolve any OPEN_DECISION silently.

## Completion discipline

F2 must:
- preserve OD-01 through OD-29;
- pass formatter/Ruff/mypy/pytest/Alembic/PostgreSQL/CI/Security;
- satisfy the F2 acceptance criteria;
- receive independent critical review;
- have no unresolved P0/P1 before F3.

Do not start F3 in the same change.

## Parallel non-blocking work

Issue #17:
repository privacy / main protection remains admin work.

Issue #18:
provider trials/credentials remain relevant for later F4 work.
