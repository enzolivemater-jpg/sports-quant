# Implementation Handoff Queue

Date: 2026-09-22

Status: ACTIVE

This file defines the handoff order. It does not override phase gates.

## Review gate

1. `.ai/handoffs/START_PROMPT_F0_INDEPENDENT_REVIEW.md`
   - actor: separate GPT/Codex review context
   - blocks F2

## Implementation queue

2. `.ai/handoffs/CLAUDE_F2_IMPLEMENTATION_HANDOFF.md`
   - issue #2
   - only after F0 review passes

3. `.ai/handoffs/CLAUDE_F3_IMPLEMENTATION_HANDOFF.md`
   - issue #6
   - only after F2 acceptance

4. `.ai/handoffs/CLAUDE_F4_IMPLEMENTATION_HANDOFF.md`
   - issue #7
   - only after F3 acceptance

5. `.ai/handoffs/CLAUDE_F5_IMPLEMENTATION_HANDOFF.md`
   - issue #8
   - only after F4 acceptance

## Parallel research queue

- `.ai/handoffs/GEMINI_FOOTBALL_VENDOR_AUDIT.md`
  - actor: Gemini Pro
  - related issues #3 and #5
  - may run before F0 review completion
  - must not modify business code

## Rule

Never hand Claude the next phase merely because the previous code compiles.

Each phase must satisfy:
- its acceptance criteria;
- CI/Security;
- required critical review;
- no unresolved P0/P1;
- Enzo decision where NEEDS_DECISION is raised.

## Next handoffs to prepare

After F5 design stabilizes:
- F6 Market Engine
- F7 Calibration/Uncertainty/P_safe
- F8 S-Tier
- F9 Backtest
- F10 Dependency/Parlay
- F11 Paper Betting/Monitoring
- F12 PWA
