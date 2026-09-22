# Claude Pro Handoff — F8 S-Tier Qualification Gate

Status: READY_AFTER_F7_ACCEPTANCE
Issue: #11

Implement:
`docs/contracts/F8_STIER_QUALIFICATION_GATE_SPEC_DRAFT.md`

Objective:
fail-closed qualification for Football.

Canonical states:
QUALIFIED, WAIT, REVIEW, NO_BET, BLOCKED

Precedence:
BLOCKED > REVIEW > WAIT > NO_BET > QUALIFIED

Mandatory gates:
- PIT integrity
- data quality
- model evidence
- calibration
- uncertainty
- P_safe
- edge
- context
- Market Risk
- Sport Predictability evidence
- model agreement if enabled
- backtest evidence
- drift

Hard rules:
- critical gates are conjunctive
- no aggregate score may compensate for a failed critical gate
- negative edge_safe cannot QUALIFY
- human review cannot manually alter P_safe
- MR does not alter probability
- SP does not directly alter P_safe/edge
- unresolved WAIT at cutoff -> NO_BET
- unresolved critical REVIEW at cutoff -> NO_BET
- technical PIT/licensing/integrity failure -> BLOCKED
- numeric thresholds still unresolved must remain unresolved

Main parlay mode:
combined P_safe >= 50%, but parlay implementation itself belongs to F10.

Tests:
all gate/state transitions, immutability, reason codes, no compensating score, direct-override prevention, P_safe/main-mode boundary.

Do not implement F9/F10 in same PR.
