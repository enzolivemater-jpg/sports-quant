# F0 Review Outcome Routing

Date: 2026-09-22

Status: ACTIVE

Purpose: convert the independent F0 review result into the next repository action without ambiguity.

## Outcome A — GO

Conditions:
- P0 open = 0
- P1 open = 0
- reviewer explicitly states F2 may begin

Actions:
1. Store the exact review in `.project/reviews/F0_INDEPENDENT_REVIEW_<date>.md`.
2. Update `.project/PHASE_GATES.toml`:
   - foundation_review.status = "PASS"
   - independent_reviewer = reviewer/context identifier
   - review_artifact = exact path
   - p0_open = 0
   - p1_open = 0
   - blocking_findings_cleared = true
   - f2.authorized = true
   - f2.authorization_basis = explicit review reference
3. Run CI + Security.
4. If green, close issue #1.
5. Start Claude with `.ai/handoffs/CLAUDE_F2_IMPLEMENTATION_HANDOFF.md`.
6. Do not start F3.

## Outcome B — GO_WITH_CONDITIONS

### Only P2 / non-blocking conditions
If reviewer explicitly allows F2:
- record review exactly;
- mark foundation_review.status = "PASS_WITH_P2";
- keep P0/P1 at zero;
- record P2 corrections as issues/tasks;
- open F2 only if the conditions do not alter critical contracts.

### Any condition that is actually P0/P1
Do not reinterpret it as P2.
Route to Outcome C.

## Outcome C — P0 or P1 findings

Actions:
1. Store the original review exactly.
2. Leave F2 unauthorized.
3. Create one correction task per materially distinct finding or one scoped correction issue if tightly coupled.
4. Correct canonical files only as required.
5. Do not silently resolve an OPEN_DECISION.
6. Run CI/Security.
7. Run a new independent review against the corrected HEAD.
8. Store the second review as a new artifact.
9. Only the latest accepted review with zero unresolved P0/P1 may open F2.

The original negative review must remain in history.

## Outcome D — NEEDS_DECISION

Actions:
1. F2 remains blocked.
2. Extract only the exact decisions requiring Enzo authority.
3. Present:
   - question
   - available options
   - consequences
   - affected files/ODs
4. Enzo decides.
5. Record the decision through the appropriate ADR/canonical file.
6. Re-run independent review.

Do not let implementer or reviewer silently choose for Enzo.

## Outcome E — NO_GO

Actions:
- F2 remains blocked.
- record the review;
- identify root cause(s);
- correct only after explicit scope/governance understanding;
- re-review from a corrected HEAD.

## Machine-gate rule

Never edit `.project/PHASE_GATES.toml` to make CI pass unless the repository review artifact genuinely supports the state being declared.

The gate follows evidence; evidence does not get rewritten to satisfy the gate.

## Claude start rule

Claude receives F2 only after:
- accepted review artifact exists;
- machine gate authorizes F2;
- issue #1 is resolved;
- CI and Security are green;
- no unresolved P0/P1 exists.

If any item is missing:
STOP.
