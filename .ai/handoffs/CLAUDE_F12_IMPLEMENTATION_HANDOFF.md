# Claude Pro Handoff — F12 PWA and Decision UI

Status: READY_ONLY_AFTER_BACKEND_CONTRACT_STABLE
Issue: #15

Implement:
`docs/contracts/F12_PWA_DECISION_UI_SPEC_DRAFT.md`

Objective:
responsive installable desktop/mobile PWA over one backend source of truth.

Frontend must NOT calculate:
- P_raw
- P_calibrated
- P_safe
- no-vig
- edge
- MR
- SP
- S-Tier
- dependency-adjusted parlay probability
- staking

Views:
- Today
- opportunity detail
- Parlay Lab when F10 ready
- history
- monitoring

Requirements:
- exact backend values/version metadata
- freshness visible
- WAIT/REVIEW/NO_BET/BLOCKED distinct
- immutable historical decision vs later settlement distinct
- no secrets in client
- stale/offline live decision cannot masquerade as current
- accessible UI

PWA polish must never block quant-engine correctness.
