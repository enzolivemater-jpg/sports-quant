# CURRENT TASK

Phase:
`PRE_F2_GATE`

Status:
`PREPARATION_SATURATED__F2_BLOCKED_PENDING_INDEPENDENT_F0_REVIEW`

Date:
2026-09-22

## Current repository state

Authoritative source:
GitHub `enzolivemater-jpg/sports-quant`

Pre-audit reviewed HEAD:
`04d6526514b53c91a4463fec3e083971ccdbfc7c`

At that HEAD:
- CI: SUCCESS
- Security: SUCCESS

## Foundation / F1

F1 repository foundation is technically green.

F0 independent review is NOT yet recorded.

Machine state:
- foundation_review.status = PENDING
- f2.authorized = false

Issue #1 remains the blocking governance gate.

## Football

Football is the first end-to-end pilot.

Prepared but not production-authorized:
- provider research
- PIT/data specifications
- feature governance
- model benchmark/math
- temporal evaluation
- market/no-vig research
- calibration/uncertainty/P_safe research
- S-Tier design
- backtest design
- dependency/parlay design
- paper betting design
- PWA design

## Implementation queue

Claude handoffs exist for F2 through F12.

Do not start F2 until the F0 gate is legitimately opened.

## External/admin work

Issue #17:
repository is still public and main is unprotected.

Issue #18:
provider credentials/trials are still required for authenticated Football bake-off.

These do not authorize bypassing F0.

## Current priority

1. independent F0 review;
2. record accepted review;
3. machine-authorize F2;
4. CI/Security green;
5. Claude F2;
6. repository hardening/provider probes in parallel.

## Stop-work rule

Further speculative architecture documentation is now lower value.

Until new evidence arrives, do only:
- review/gate work;
- CI/security fixes;
- repo hardening;
- provider probes;
- verified defect corrections.

Reference:
`docs/runbooks/PRE_F2_READINESS_AUDIT.md`
