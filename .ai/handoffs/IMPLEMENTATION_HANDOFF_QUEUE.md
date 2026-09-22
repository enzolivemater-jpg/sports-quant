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

6. `.ai/handoffs/CLAUDE_F6_IMPLEMENTATION_HANDOFF.md`
   - issue #9
   - after F5 acceptance and stable PIT odds

7. `.ai/handoffs/CLAUDE_F7_IMPLEMENTATION_HANDOFF.md`
   - issue #10
   - after F6/model evidence; unresolved OD-01..05 may block full completion

8. `.ai/handoffs/CLAUDE_F8_IMPLEMENTATION_HANDOFF.md`
   - issue #11
   - after F7 acceptance

9. `.ai/handoffs/CLAUDE_F9_IMPLEMENTATION_HANDOFF.md`
   - issue #12
   - after F8 acceptance

10. `.ai/handoffs/CLAUDE_F10_IMPLEMENTATION_HANDOFF.md`
    - issue #13
    - after valid single-leg/backtest stack

11. `.ai/handoffs/CLAUDE_F11_IMPLEMENTATION_HANDOFF.md`
    - issue #14
    - prospective Football paper betting

12. `.ai/handoffs/CLAUDE_F12_IMPLEMENTATION_HANDOFF.md`
    - issue #15
    - only after backend decision contracts stabilize

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
