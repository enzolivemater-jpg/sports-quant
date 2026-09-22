# START PROMPT — Independent F0 Review Chat

Use this text as the first message in a **new, separate GPT/Codex review chat**.

---

You are the independent critical reviewer for SPORTS QUANT Foundation F0.

Repository: `enzolivemater-jpg/sports-quant`
Review target: current `main` HEAD.

Your task is REVIEW ONLY. Do not implement F2 or modify business logic during the review.

Read and review at minimum:

- `.project/FOUNDATION_DECISIONS_v0.1.yaml`
- `.project/OPEN_DECISIONS.yaml`
- `.project/SPORT_PREDICTABILITY_POLICY.yaml`
- `.project/PROJECT_PROFILE.yaml`
- `docs/adr/ADR-0001-foundation-v0.1.md`
- `docs/adr/ADR-0002-mandatory-sports-scope.md`
- `docs/adr/ADR-0003-additional-sports-allowlist.md`
- `docs/adr/ADR-0004-football-first-pilot.md`
- `.ai/AI_CHARTER.md`
- `.ai/AI_DECISIONS.md`
- `docs/runbooks/GOVERNANCE_DEVIATION_F1_BEFORE_F0_REVIEW.md`
- `scripts/validate_phase_gates.py`
- `.project/PHASE_GATES.toml`
- `.ai/handoffs/F0_INDEPENDENT_REVIEW.md`

Project authority and roles:
- Enzo = final authority.
- GPT/Codex = architecture, math, specification, anti-leakage and independent critical review.
- Claude Pro = primary implementation, refactoring, tests, integration and technical documentation.
- Gemini Pro = external research, vendor/licensing/document audit and methodological challenge.

Canonical current sport scope:
- mandatory: Basketball, Football, MMA
- UFC = mandatory initial MMA competition scope
- approved additional validation sports only: Handball, Volleyball, Tennis
- all other sports excluded unless Enzo explicitly changes scope
- Football = first end-to-end pilot sport

Important Foundation invariants:
- C2 Decision Support active
- C2+ deferred
- automated real-money wagering prohibited
- NO_BET is a native valid outcome
- P_raw, P_calibrated and P_safe are distinct
- 0 <= P_safe <= P_calibrated <= 1
- LLM/human may not directly set final P_safe
- known_at must be point-in-time defensible
- critical simulated information requires known_at <= decision_cutoff_at
- no speculative reconstruction of known_at
- source taxonomy and the four data-state axes remain orthogonal
- edge_calibrated and edge_safe are distinct
- edge_safe < 0 cannot be QUALIFIED
- Market Risk is structural, not probability
- weighted_average_mr is DEFERRED
- composite Dynamic Market Risk Score is DEFERRED
- Sport Predictability is distinct from P_safe, MR, edge, odds and profitability
- Sport Predictability requires versioned PIT-valid OOS evidence
- predictability_evidence_gate exists, but its numeric thresholds remain NOT_DEFINED_DO_NOT_IMPLEMENT
- Football Phase 1: FOOTBALL_1X2 MR2 and FOOTBALL_TOTAL_GOALS_MAIN MR2
- Football Phase 2: FOOTBALL_ASIAN_HANDICAP MR2, FOOTBALL_BTTS MR2, FOOTBALL_TEAM_TOTALS MR2
- Basketball and MMA/UFC market catalogs remain intentionally undefined
- OD-01 through OD-29 are the only numbered OPEN_DECISIONS unless Enzo explicitly authorizes a new one

Review questions:
1. Are all canonical decisions internally consistent?
2. Did any amendment silently resolve an OPEN_DECISION that should remain open?
3. Are current role assignments correct?
4. Are C2/C2+ and automated-wagering boundaries correct?
5. Are probability invariants and direct-P_safe prohibition consistent?
6. Are known_at and PIT semantics strict enough to prevent leakage?
7. Are source taxonomy and four data-state dimensions consistent and orthogonal?
8. Are edge_calibrated / edge_safe semantics correct?
9. Is edge_safe < 0 correctly incompatible with QUALIFIED?
10. Are Market Risk and Sport Predictability separated from probability/edge/odds?
11. Is the Football Phase 1/2 catalog exact?
12. Are Basketball and MMA/UFC catalogs still undefined rather than invented?
13. Is the current sport scope exact and consistent across YAML/ADRs/profile?
14. Does ADR-0004 only set Football as first pilot, without selecting a model champion?
15. Does Sport Predictability remain PIT/OOS/versioned and non-arbitrary?
16. Are weighted_average_mr and composite Dynamic Market Risk still deferred?
17. Are exactly OD-01 through OD-29 present?
18. Is the historical F1-before-review deviation honestly recorded and effectively contained by the machine gate so it cannot silently authorize F2?
19. Do any P0/P1 issues remain that must block F2?

Severity:
- P0 = correctness/safety/PIT/governance defect making implementation unsafe
- P1 = material inconsistency likely to propagate into architecture/model decisions
- P2 = non-blocking clarity/maintainability issue

Required output should be directly usable with `.project/reviews/F0_REVIEW_RECORD_TEMPLATE.md`.
Include the exact full Git HEAD you reviewed.

Required output:
- P0 findings
- P1 findings
- P2 findings
- exact file/section references
- required corrections
- explicit statement whether any OPEN_DECISION was silently changed
- final status: GO / GO_WITH_CONDITIONS / NO_GO / NEEDS_DECISION

Rules:
- Do not self-assume prior implementation claims are true.
- Do not implement F2.
- If P0/P1 exists, final status must not permit F2 until corrected and re-reviewed.
- If no P0/P1 remains, state clearly whether F2 may begin.

---

After the review, paste the complete review result back into the main SPORTS QUANT chat and/or attach it to GitHub issue #1.
