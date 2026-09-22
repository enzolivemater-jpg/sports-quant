# Claude Pro Handoff — F9 Backtesting and Reproducibility

Status: READY_AFTER_F8_ACCEPTANCE
Issue: #12

Implement:
`docs/contracts/F9_BACKTEST_REPRODUCIBILITY_SPEC_DRAFT.md`

Objective:
deterministic PIT replay of historical Football decisions.

Mandatory:
- Train -> Validation -> Calibration -> frozen Final Test
- walk-forward / chronological evaluation
- no future information
- immutable decision snapshots
- reproducibility manifest
- forecast metrics separated from economic metrics

Metrics:
- Log Loss
- Brier
- ECE/calibration
- sample size
- confidence intervals where defined
- CLV where available
- paper ROI
- yield
- drawdown

Classification reports:
P bands, L bands, R bands, MR, competition, market family, odds band, versions.

Hard rules:
- closing odds evaluation only, never pre-cutoff input
- final test not used for tuning
- no retrospective stake tuning
- no martingale/loss chasing
- invalid PIT run = invalid evidence
- backtest alone does not authorize real-money use

Tests:
deterministic replay, future-record rejection, closing leakage, final-test isolation, label isolation, segment boundaries, ROI/yield/drawdown correctness, manifest completeness, frozen-test mutation detection.

Do not start F10/F11 in same PR.
