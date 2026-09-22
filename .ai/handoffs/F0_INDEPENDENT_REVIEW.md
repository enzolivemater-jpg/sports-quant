# F0 Independent Review Handoff

Purpose: independent critical review of SPORTS QUANT Foundation governance before F2 implementation.

Reviewer must not assume previous implementation claims are correct.

## Repository

Repository: enzolivemater-jpg/sports-quant
Review target: current main HEAD at review time.

## Required files

Review at minimum:

- .project/FOUNDATION_DECISIONS_v0.1.yaml
- .project/OPEN_DECISIONS.yaml
- .project/SPORT_PREDICTABILITY_POLICY.yaml
- .project/PROJECT_PROFILE.yaml
- docs/adr/ADR-0001-foundation-v0.1.md
- docs/adr/ADR-0002-mandatory-sports-scope.md
- docs/adr/ADR-0003-additional-sports-allowlist.md
- docs/adr/ADR-0004-football-first-pilot.md
- .ai/AI_CHARTER.md
- .ai/AI_DECISIONS.md
- docs/runbooks/GOVERNANCE_DEVIATION_F1_BEFORE_F0_REVIEW.md
- scripts/validate_phase_gates.py
- .project/PHASE_GATES.toml

## Mandatory review questions

1. Are canonical decisions internally consistent?
2. Did any amendment silently resolve an OPEN_DECISION that should remain open?
3. Are the roles correct?
   - Enzo: final authority
   - GPT/Codex: architecture/math/spec/anti-leakage/independent review
   - Claude Pro: primary implementation/integration/tests/refactoring/docs
   - Gemini Pro: external research/vendor/licence/methodological audit
4. Is C2 Decision Support active, with C2+ deferred and automated wagering prohibited?
5. Are P_raw, P_calibrated and P_safe correctly separated?
6. Is direct human/LLM assignment of final P_safe prohibited?
7. Are known_at semantics strict enough to prevent point-in-time leakage?
8. Are source taxonomy and the four data-state axes consistent and orthogonal?
9. Are edge_calibrated and edge_safe correctly distinguished?
10. Is edge_safe < 0 correctly incompatible with QUALIFIED?
11. Are Market Risk and Sport Predictability kept separate from probability, odds and edge?
12. Is the Football Phase 1/2 market catalog represented exactly as approved?
13. Are Basketball and MMA/UFC market catalogs intentionally undefined rather than invented?
14. Is the active sport scope consistent?
    - mandatory: Basketball, Football, MMA/UFC
    - additional validation-only: Handball, Volleyball, Tennis
    - every other sport excluded unless Enzo changes scope
15. Does ADR-0004 correctly make Football the first pilot without selecting a model champion?
16. Does Sport Predictability require PIT-valid OOS evidence and avoid arbitrary numeric scoring?
17. Are weighted_average_mr and composite Dynamic Market Risk still deferred?
18. Are exactly OD-01 through OD-29 present, with no invented numbered decision?
19. Is the historical F1-before-review deviation explicitly documented, honestly preserved, and effectively contained by the current F2 machine gate?
20. Do any P0/P1 inconsistencies remain that should block F2?

## Severity

- P0: correctness/safety/PIT/governance defect making implementation unsafe.
- P1: material inconsistency likely to propagate into architecture or model decisions.
- P2: non-blocking clarity/maintainability issue.

## Required output

Return:

- P0 findings
- P1 findings
- P2 findings
- exact files/sections affected
- required corrections
- whether any OPEN_DECISION was silently changed
- final status: GO / GO_WITH_CONDITIONS / NO_GO / NEEDS_DECISION

Do not implement F2 during this review.

If P0/P1 findings exist, F2 remains blocked until corrected and re-reviewed.
