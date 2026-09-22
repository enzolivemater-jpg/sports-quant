# Claude Pro Handoff — F11 Football Paper Betting and Monitoring

Status: READY_AFTER_F9_AND_LIVE_PIPELINE
Issue: #14

Implement:
`docs/contracts/F11_PAPER_BETTING_MONITORING_SPEC_DRAFT.md`

Objective:
prospective unseen Football validation.

At decision time:
- capture exact data/odds/context
- run approved pipeline
- freeze immutable decision
- settle only after event

Log ALL states:
QUALIFIED, WAIT, REVIEW, NO_BET, BLOCKED

Monitor:
- Log Loss
- Brier
- ECE
- sample size
- CLV
- paper ROI
- yield
- drawdown
- qualification/NO_BET/WAIT/REVIEW/BLOCKED rates
- data/concept/calibration/source drift

Hard rules:
- settlement cannot mutate pre-event snapshot
- no logging winners only
- simple deterministic paper stake
- no martingale/loss chasing
- paper results do not automatically authorize real-money use
- OD-09 drift thresholds remain open
- no invented minimum-N readiness threshold

Prospective context capture:
lineups, injuries, suspensions, squad changes, weather, trusted context, market movement with received_at/known_at.

Completion means Football is operational for PAPER BETTING, not automatically real-money use.
