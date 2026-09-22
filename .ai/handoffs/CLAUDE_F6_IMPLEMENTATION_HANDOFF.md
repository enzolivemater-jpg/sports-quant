# Claude Pro Handoff — F6 Football Market Engine

Status: READY_AFTER_F5_ACCEPTANCE
Issue: #9

Start only when F0–F5 gates are green and main CI/Security are green.

Implement exactly:
`docs/contracts/F6_FOOTBALL_MARKET_ENGINE_SPEC_DRAFT.md`

Scope:
- Football Phase 1 only
- FOOTBALL_1X2
- FOOTBALL_TOTAL_GOALS_MAIN
- implied probabilities
- overround
- extensible no-vig interface
- transparent proportional no-vig research baseline
- PIT snapshot selection
- bookmaker identity normalization
- market provenance
- edge_calibrated / edge_safe calculations

Hard rules:
- OD-07 remains OPEN
- no final no-vig Champion is chosen here
- closing odds cannot leak into earlier decisions
- each book normalized before consensus
- market instances cannot be mixed
- MR2 is structural and does not change probability
- edge_safe < 0 cannot QUALIFY

Tests must cover:
- odds -> implied probability
- overround
- no-vig sums to 1
- malformed/missing outcome set rejection
- PIT future-odds exclusion
- closing-price leakage
- bookmaker normalization
- staleness propagation
- edge formulas
- MR non-interference
- deterministic output

Do not implement F7 in same PR.
