# Governance Deviation Record — F1 Started Before Independent F0 Review

Date recorded: 2026-09-22

Status: REMEDIATION_IN_PROGRESS__P1_01_CORRECTED_PENDING_REREVIEW

## What happened

Foundation governance states:

`f1_may_start_before_independent_review_of_f0: false`

However, the F1 repository skeleton was implemented and technically validated before the required independent F0 review was completed.

This is a historical process deviation.

## What this record does NOT do

This record does not:
- retroactively claim the F0 review occurred;
- waive the independent-review requirement;
- authorize F2;
- change the canonical Foundation decision;
- erase the deviation;
- turn same-chat/self-review into independent review.

## Impact assessment

The premature work was limited to F1 repository-foundation scope:
- repository structure;
- Python packaging/lock;
- CI/Security;
- PostgreSQL local/test plumbing;
- migration skeleton;
- minimal observability;
- governance/research documentation.

No F2 domain-contract implementation was started.

No model, production P_safe, market engine, optimizer or automated wagering logic was implemented.

## Independent F0 review result

The independent review of HEAD `f7be5354f0cb50cd82617571485c2d2fab6d7fa4` reported:
- P0 open: 0
- P1 open: 1
- blocking finding: P1-01
- final status: NO_GO

P1-01 identified that the previous machine gate inspected only `src/sports_quant/contracts/`, so it did not exhaustively contain premature F2/F3+ source logic elsewhere.

The original review is preserved under `.project/reviews/`.

## Forward remediation

The project now applies a stricter forward gate:

1. F2 remains unauthorized.
2. GitHub issue #1 remains open until the corrected gate is independently re-reviewed.
3. `.project/PHASE_GATES.toml` is the machine-readable gate.
4. `.project/F1_SOURCE_ALLOWLIST.toml` enumerates the exact non-README source files allowed while F2 is closed.
5. `scripts/validate_phase_gates.py` scans all tracked/runtime files under `src/sports_quant/` and fails when any non-README source file is outside that explicit F1 allowlist.
6. Regression tests prove that premature code in:
   - `contracts/`
   - `modeling/football/`
   - `calibration/`
   - `market/`
   is blocked while legitimate F1 source/scaffold files pass.
7. F2 authorization still requires:
   - accepted independent review artifact;
   - p0_open = 0;
   - p1_open = 0;
   - blocking_findings_cleared = true;
   - f2.authorized = true.
8. Claude F2 handoff independently checks the same gate before writing code.

## Scope of the guarantee

The machine containment guarantee is now intentionally precise:

While `f2.authorized=false`, no new production/package source file may appear under `src/sports_quant/` unless it is explicitly present in the F1 source allowlist or is a README scaffold reservation.

Research tooling outside the production package remains governed separately and does not become F2 implementation merely by existing.

Repository-admin protection of `main` remains a separate issue (#17).

## Reviewer instruction

The targeted re-review should verify:
- the explicit allowlist is complete and no broader than F1;
- unauthorized code in contracts/football/calibration/market is blocked;
- valid F1 source and README scaffold pass;
- protected gate files cannot drift after an accepted review without requiring re-review;
- P2-01 and P2-02 were corrected without changing canonical scope.

The reviewer must not treat this document as evidence that F0 passed.

## Resolution condition

The process deviation is considered remediated for forward execution only when:
- P1-01 correction is independently re-reviewed;
- any remaining P0/P1 findings are cleared;
- the accepted review artifact is committed;
- the F2 machine gate is opened;
- CI/Security are green.

The historical fact that F1 started early remains in the project record.
