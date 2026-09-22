# Downstream Quant Open-Decision Readiness

Status: PREPARED_NOT_RESOLVED

This runbook tracks which downstream decisions can be researched before production implementation.

## Ensemble / monitoring

- OD-08 model agreement: research design ready.
- OD-09 drift thresholds: research design ready.

Production resolution requires OOS/paper evidence.

## Optimizer

- OD-18 MR mode limits: research design ready.
- OD-19 dependency quantification: research design ready.
- OD-20 marginal leg value: research design ready.
- OD-21 multi-sport improvement: research design ready.
- OD-22 solver: defer until search complexity is measured.
- OD-23 joint/Monte-Carlo method: research design ready.

## Guardrail

"Research design ready" does not mean "decision resolved".

Implementation may create interfaces/scaffolds consistent with phase specs, but production behavior must not silently select an unresolved rule.
