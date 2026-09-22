# Claude Pro Handoff — F7 Calibration / Uncertainty / P_safe Scaffold

Status: READY_AFTER_F6_AND_MODEL_EVIDENCE
Issue: #10

Start only when prior phases are accepted and main is green.

Implement:
`docs/contracts/F7_CALIBRATION_UNCERTAINTY_PSAFE_SPEC_DRAFT.md`

Objective:
build calibration artifacts/interfaces, uncertainty interface and safe P_safe plumbing without inventing unresolved formulas.

Hard rules:
- keep P_raw / P_calibrated / P_safe separate
- invariant 0 <= P_safe <= P_calibrated <= 1
- no human/LLM direct final P_safe setter
- calibration data separate from final test
- OD-01 through OD-05 remain unresolved where applicable
- no arbitrary threshold/sample-size invention

Calibration candidates may be implemented as challengers only when justified by sample size:
- logistic/Platt
- isotonic
- beta
- appropriate multiclass alternatives

Required outputs:
- versioned calibrator artifact
- OOS Log Loss/Brier/ECE/reliability
- sample size
- uncertainty metadata
- deterministic P_safe interface placeholder/strategy boundary

Required tests:
- bounds
- P_safe <= P_calibrated
- no final-test calibration fit
- chronological calibration split
- multiclass normalization
- sparse segmentation handling
- no direct override path
- deterministic replay
- band boundaries
- insufficient evidence cannot QUALIFY

If OD-01/02/03/04/05 must be resolved to proceed beyond scaffold: STOP and raise NEEDS_DECISION rather than guessing.

Do not implement F8 in same PR.
