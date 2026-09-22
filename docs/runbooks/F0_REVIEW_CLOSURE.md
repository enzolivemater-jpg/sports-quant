# F0 Independent Review — Recording and Closure Procedure

Date: 2026-09-22

Status: ACTIVE

## Purpose

Turn the independent F0 review from a chat result into an auditable repository gate.

A chat saying "GO" is not enough by itself. The review result must be recorded and the machine gate updated consistently.

## Step 1 — Run independent review

Use:
`.ai/handoffs/START_PROMPT_F0_INDEPENDENT_REVIEW.md`

The reviewer must be a separate GPT/Codex review context from the implementation/design context.

## Step 2 — Store the exact review result

Create:

`.project/reviews/F0_INDEPENDENT_REVIEW_<YYYY-MM-DD>.md`

The artifact must contain:
- reviewer/context identification sufficient to establish separation;
- repository HEAD reviewed;
- files reviewed;
- P0 findings;
- P1 findings;
- P2 findings;
- required corrections;
- statement on silent OPEN_DECISION changes;
- final status;
- review date.

Do not rewrite a negative review into a positive summary.

## Step 3 — Resolve P0/P1

If any P0/P1 exists:
- leave F2 unauthorized;
- correct the defect;
- rerun independent review against the corrected HEAD;
- record the new review artifact.

P2 may be non-blocking only when the independent reviewer explicitly permits progression and the issue does not conceal a correctness/PIT problem.

## Step 4 — Open machine gate

Only when the accepted review has no unresolved P0/P1:

Update `.project/PHASE_GATES.toml`:

- foundation_review.status = "PASS" or "PASS_WITH_P2"
- foundation_review.independent_reviewer = non-empty identifier
- foundation_review.review_artifact = exact repository path
- foundation_review.p0_open = 0
- foundation_review.p1_open = 0
- foundation_review.blocking_findings_cleared = true
- f2.authorized = true
- f2.authorization_basis = reference to accepted review

Do not modify canonical OPEN_DECISIONS merely to satisfy the gate.

## Step 5 — CI

CI must pass:
- `scripts/validate_phase_gates.py`
- F1 foundation validator
- Ruff
- mypy
- tests
- PostgreSQL smoke
- Security workflow

If the gate says F2 is authorized but the review artifact is missing or blocking findings remain, CI must fail.

## Step 6 — Close issue #1

Close #1 only after:
- accepted review artifact is committed;
- machine gate is open;
- CI/Security are green.

Then Claude may receive:
`.ai/handoffs/CLAUDE_F2_IMPLEMENTATION_HANDOFF.md`

## Fail-safe behavior

If review status is PENDING, BLOCKED or NEEDS_DECISION:
- f2.authorized must remain false;
- any non-scaffold file placed in `src/sports_quant/contracts/` causes CI failure.

## Scope

This procedure authorizes F2 only.

It does not automatically authorize F3 or any later phase.
