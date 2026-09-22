# SPORTS QUANT — Fast Execution Plan

Date: 2026-09-22

Status: ACTIVE_EXECUTION_PLAN

Pilot: FOOTBALL

## Objective

Minimize calendar time without compressing statistical validation.

Engineering tasks may be parallelized.
PIT integrity, OOS validation, calibration evidence and prospective paper evidence may not be shortcut.

## Current gate

### G0 — Independent F0 review

Blocking issue:
- #1 Governance gate: independent review of F0 before F2

Required outcome before F2 implementation:
- no unresolved P0/P1 defect;
- any material disagreement resolved by Enzo;
- review artifact recorded.

Until G0 passes:
- documentation/research may continue;
- F2+ production/business implementation must not begin.

## Critical path after G0

### F2 — Contracts
Issue #2

Deliver:
- canonical enums/contracts
- timestamps/known_at
- provenance
- market/probability/edge/decision/predictability contracts

Gate:
- contract tests green
- no F3 leakage

### F3 — PIT Kernel
Issue #6

Deliver:
- deterministic as-of replay
- revision semantics
- snapshot manifests
- anti-leakage tests

### F4 — Football Data Layer
Issue #7

Parallel research:
- issue #3 provider bake-off
- issue #5 pilot dataset

Deliver:
- raw/normalized/canonical zones
- provider adapters
- entity resolution
- historical Phase 1 odds
- EPL reproducible pilot dataset

### F5 — Football Modeling
Issue #8

Parallel after stable dataset:
- Elo/rating
- Bradley-Terry
- Poisson
- Dixon-Coles
- logistic/GAM
- boosting challenger
- market benchmark

Deliver:
- temporal OOS forecasts
- reproducible experiment artifacts
- no Champion without required review

### F6 — Market Engine
Issue #9

Can overlap late F5 once PIT odds dataset is stable.

Deliver:
- implied probabilities
- overround
- no-vig baseline/interface
- market consensus plumbing
- edge calculations

### F7 — Calibration / uncertainty / P_safe
Issue #10

Deliver:
- calibration harness
- uncertainty interface
- governed P_safe interface

Blocked on empirical decisions:
- OD-01 through OD-05 as applicable

### F8 — S-Tier Gate
Issue #11

Deliver:
- fail-closed qualification
- deterministic reason codes
- explicit NO_BET / WAIT / REVIEW / BLOCKED

### F9 — Backtest
Issue #12

Deliver:
- full PIT decision replay
- frozen final test
- Log Loss/Brier/ECE
- CLV/paper ROI/yield/drawdown
- segment reporting

### F10 — Dependency / Parlay
Issue #13

Can start only after qualified single-leg stack exists.

Deliver:
- dependency-aware joint probability
- mono/multi comparison
- combined P_safe >=50% main mode
- P/L/R/MR reporting
- NO_BET optimizer output

### F11 — Prospective Football paper betting
Issue #14

This is the first operational live validation milestone.

Deliver:
- pre-event frozen decisions
- post-event settlement
- live calibration/CLV/paper economics
- drift monitoring
- prospective context dataset

### F12 — PWA
Deferred until stable backend contract.

Deliver:
- Today
- opportunities
- explanations
- Parlay Lab
- history
- monitoring
- desktop/mobile PWA

## Parallel lanes

### Lane A — Core engineering
F2 -> F3 -> F4 -> F5 -> F6/F7 -> F8 -> F9 -> F11

### Lane B — Data/vendor
Issue #3 continuously until OD-24 can be resolved.

### Lane C — Quant research
Issue #4 model benchmark design/evidence.
Later calibration/dependency research.

### Lane D — CI/security
Every commit:
- format
- lint
- type check
- tests
- migrations
- PostgreSQL integration where relevant
- secret scan
- dependency audit

### Lane E — Governance/review
Independent reviews at critical promotion points.

## Speed rules

1. Reuse common infrastructure; never reuse sport-specific model assumptions.
2. Build only current-phase code.
3. Prepare next-phase specification before current phase ends.
4. Use provider trials/free tiers before recurring spend.
5. Never wait for perfect historical context; use retrospective PIT-safe core plus prospective context capture.
6. Automate tests before multiplying providers/models.
7. Fail fast on providers that cannot support defensible PIT.
8. Freeze interfaces before parallel implementations.
9. Benchmark simple models before complex ones.
10. Do not optimize UI before decision engine validity.

## Football operational milestones

### M1 — Quant pipeline runnable
F2–F8 Football minimum scope green.

System can produce governed Football decisions but is not yet prospectively validated.

### M2 — Historical evidence
F9 green.

System has reproducible PIT backtests and frozen final-test evidence.

### M3 — Paper operational
F11 live.

SPORTS QUANT evaluates upcoming Football matches, freezes decisions, settles afterward and monitors calibration/CLV/paper performance.

### M4 — Real-money readiness review
Not automatic.

Requires sufficient prospective evidence under future approved thresholds and independent review.

No guaranteed winning-bet milestone exists.

## Resource allocation

- GPT/Codex: architecture, math, contracts, anti-leakage, independent critical review in a separate context.
- Claude Pro: primary implementation/refactoring/tests/integration/docs.
- Gemini Pro: vendor/licensing/literature research and methodological challenge.
- GitHub: source of truth, issues, CI, review trail.
- Enzo: final authority.

## Current instruction

Do not begin F2 implementation until G0 is resolved.

Until then, continue:
- provider research
- license research
- schema probes
- draft specs
- acceptance tests design
- review preparation
