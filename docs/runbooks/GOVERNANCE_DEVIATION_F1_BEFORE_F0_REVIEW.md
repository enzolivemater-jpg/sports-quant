# Governance Deviation Record — F1 Started Before Independent F0 Review

Date recorded: 2026-09-22

Status: REMEDIATED_FOR_FORWARD_PROGRESS__HISTORICAL_DEVIATION_REMAINS

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

## Forward remediation

The project now applies a stricter forward gate:

1. F2 remains unauthorized.
2. GitHub issue #1 remains open until independent F0 review is recorded.
3. `.project/PHASE_GATES.toml` is the machine-readable gate.
4. `scripts/validate_phase_gates.py` makes CI fail if F2 implementation appears while unauthorized.
5. F2 authorization requires:
   - accepted independent review artifact;
   - p0_open = 0;
   - p1_open = 0;
   - blocking_findings_cleared = true;
   - f2.authorized = true.
6. Claude F2 handoff independently checks the same gate before writing code.

## Reviewer instruction

The independent reviewer should assess whether the historical deviation creates any remaining P0/P1 correctness risk.

The reviewer must not treat this document as evidence that F0 passed.

## Resolution condition

The process deviation is considered remediated for forward execution only when:
- independent F0 review is completed;
- any P0/P1 findings are corrected and re-reviewed;
- the review artifact is committed;
- the F2 machine gate is opened;
- CI/Security are green.

The historical fact that F1 started early remains in the project record.
