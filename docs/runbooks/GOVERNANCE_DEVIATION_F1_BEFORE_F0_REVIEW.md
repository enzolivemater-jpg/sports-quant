# Governance Deviation Record — F1 Started Before Independent F0 Review

Date recorded: 2026-09-22

Status: REMEDIATION_IN_PROGRESS__P1_01_HARDENED_PENDING_REREVIEW

## Historical deviation

Foundation governance required independent F0 review before F1, but the F1 repository skeleton was implemented first. This remains a recorded historical process deviation.

No F2 domain contracts, model, production P_safe, market engine, optimizer or automated wagering logic were implemented before the gate.

## Review history

Initial review:
- reviewed HEAD: `f7be5354f0cb50cd82617571485c2d2fab6d7fa4`
- P0: 0
- P1: 1
- status: NO_GO

First targeted re-review:
- reviewed HEAD: `3cd2bba8bd29d7795d998d12f7f84b756bb6ee4f`
- P0: 0
- P1: 1
- P1-01 remains OPEN
- status: NO_GO

Both negative review artifacts are preserved under `.project/reviews/`.

## Current P1-01 remediation

While `f2.authorized=false`, the machine gate now enforces all of the following:

1. The exact F1 source path set is hard-coded in `scripts/validate_phase_gates.py`.
2. `.project/F1_SOURCE_ALLOWLIST.toml` must exactly mirror that canonical set; it cannot add or remove paths.
3. The scaffold exception is hard-coded to exactly `README.md`.
4. Each of the seven approved F1 Python files is frozen by its exact Git blob SHA.
5. Any content change to one of those files fails the closed F2 gate.
6. The scanner covers all files under `src/`, not only `src/sports_quant/`.
7. Every file under `src/` while F2 is closed must be either:
   - one exact frozen F1 source blob; or
   - a `README.md` scaffold.
8. `pyproject.toml` explicitly restricts setuptools discovery to `sports_quant*`, and the validator verifies that exact packaging scope.
9. A second package under `src/` fails independently of packaging configuration.
10. Tests cover:
   - allowlist extension;
   - scaffold filename change;
   - content mutation of an already allowlisted F1 file;
   - contracts;
   - Football modeling;
   - calibration;
   - market;
   - probability outside contracts;
   - second package under src;
   - packaging-scope broadening.

## Scope of guarantee

This is intentionally strict because F2 is closed.

Legitimate changes to frozen F1 source files before F2 authorization require updating the baseline and another independent review; they cannot silently pass.

Research scripts outside `src/` are not production package implementation and remain governed separately.

Repository administrator controls remain separately tracked in issue #17.

## Resolution condition

P1-01 remains governance-open until an independent reviewer verifies the hardened gate and reports:
- P0 open = 0;
- P1 open = 0;
- blocking_findings_cleared = true;
- explicit F2 authorization statement.

Until then:
F2 MUST REMAIN BLOCKED.
