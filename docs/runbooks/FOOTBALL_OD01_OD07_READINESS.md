# Football Quant Decision Readiness — OD-01 to OD-07

Status: PREPARED_NOT_RESOLVED

This checklist prevents unresolved quantitative decisions from being guessed during implementation.

| OD | Decision | Earliest evidence needed | May implementation scaffold proceed? | May production rule be fixed now? |
|---|---|---|---|---|
| OD-01 | exact P_safe formula | calibrated OOS + uncertainty evidence | Yes | No |
| OD-02 | uncertainty Champion | OOS forecast error + uncertainty experiments | Yes | No |
| OD-03 | Calibration=VALID thresholds | calibration folds + final-test evidence | Yes | No |
| OD-04 | minimum sample sizes | observed variance/dependence + precision analysis | Yes | No |
| OD-05 | calibrator segmentation | candidate segment OOS comparison | Yes | No |
| OD-06 | stricter edge_safe threshold | P_safe + market error + prospective/CLV evidence | Yes | No |
| OD-07 | no-vig Champion | same-snapshot OOS method benchmark | Yes | No |

## Stop rule

If Claude/GPT/Gemini reaches a point where production behavior depends on one of these unresolved decisions:
- do not invent a default and silently promote it;
- implement an explicit research baseline only when the phase spec allows it;
- label the baseline as non-Champion;
- raise NEEDS_DECISION when the phase cannot continue safely without resolution.

## Research baselines currently permitted by existing specs

- no-vig: proportional normalization as transparent research baseline;
- calibration: multiple candidate methods may be tested;
- P_safe: interface/scaffold only, no production formula;
- edge: edge_safe < 0 prohibits QUALIFIED; stricter threshold unresolved.

## Approval discipline

A final OD resolution must preserve:
- supporting experiment references;
- code/data version;
- affected sport/market scope;
- rejected alternatives;
- uncertainty;
- review status;
- Enzo authority where governance requires it.
