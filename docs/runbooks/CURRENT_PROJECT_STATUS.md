# SPORTS QUANT — Current Execution Status

Date: 2026-09-22

Status: ACTIVE

Pilot sport: FOOTBALL

## Governance gate

F0 independent review:
- issue #1: OPEN
- accepted review artifact: NOT YET RECORDED
- F2 machine authorization: CLOSED

Therefore:
- F2 production/domain implementation: BLOCKED
- F3+ implementation: BLOCKED
- research/specification/provider probes: ALLOWED

Machine enforcement:
- `.project/PHASE_GATES.toml`
- `scripts/validate_phase_gates.py`

## Repository foundation

F1:
- technically implemented
- CI/Security generally enforced on main
- PostgreSQL integration smoke exists
- secret scan and dependency audit exist

Repository admin state last verified:
- visibility: PUBLIC
- main protected: false

Hardening issue:
- #17

No provider secret should be added while the repository remains public.

## Football data research

### Free result baseline

OpenFootball EPL:
- 2000/01 through 2024/25
- 25 completed seasons
- 380 verified match records per season
- 9,500 verified matches total

Manifest:
`data/manifests/football_openfootball_epl_2000_2025_verified.json`

Use:
- baseline result/history research
- sequential-rating research
- Poisson/Dixon-Coles preparation
- entity/result cross-checking

Not supplied by this source:
- historical bookmaker odds
- historical injury publication chronology
- historical lineup publication chronology
- mutable-context known_at

### Stage A historical odds sample

Competition:
- EPL 2024/25

Scope:
- Matchweeks 1–4
- 40 fixtures
- 23 kickoff groups
- T-24h / T-1h / T-15m
- h2h + totals
- one region initially

Fixture identities have been cross-checked against OpenFootball:
- 0 / 40 mismatches after explicit non-fuzzy research aliases

Stage A runner:
`scripts/research/run_odds_stage_a.py`

Default:
DRY RUN

Paid execution:
NOT AUTHORIZED YET

### Free/trial provider probes

Machine plan:
`data/manifests/football_provider_probe_plan_v0.1.json`

Runner:
`scripts/research/run_provider_probes.py`

Current candidates:
- API-Football
- Sportmonks
- Sportradar

The Odds API is deliberately separated because historical requests may consume paid quota.

Credentials/spend tracker:
- issue #18

OD-24:
OPEN

## Football model research readiness

Verified result pool:
- 9,500 matches

Temporal evaluation design:
`docs/research/FOOTBALL_BASELINE_TEMPORAL_EVALUATION_PLAN_v0.1.md`

Final test:
- UNASSIGNED
- must remain unconsumed until governed F5 start

OD-11:
OPEN

No Champion model has been selected.

## Prepared implementation chain

- F2 Contracts — issue #2
- F3 PIT Kernel — #6
- F4 Football Data Layer — #7
- F5 Modeling Harness — #8
- F6 Market Engine — #9
- F7 Calibration / Uncertainty / P_safe — #10
- F8 S-Tier — #11
- F9 Backtesting — #12
- F10 Dependency / Parlay — #13
- F11 Paper Betting / Monitoring — #14
- F12 PWA — #15

Master execution issue:
- #16

Claude handoffs are prepared through F12.

## Immediate external blockers/actions

### A. Independent F0 review
Use:
`.ai/handoffs/START_PROMPT_F0_INDEPENDENT_REVIEW.md`

Required before F2.

### B. Repository hardening
Make repository private and protect main.

Tracked by:
- #17

### C. Provider credentials
Obtain free/trial credentials when ready for:
- API-Football
- Sportmonks
- Sportradar

Tracked by:
- #18

No credential should be committed or pasted into GitHub.

### D. Historical odds spend
The Odds API historical plan is NOT authorized merely by having the runner ready.

Stage A purchase/spend requires explicit approval after rechecking current price/quota.

## What can continue without waiting

Allowed research:
- provider documentation/licensing audit
- free-source parsing and quality checks
- Stage A reconciliation tooling
- acceptance-test design
- leakage-test design
- handoff preparation
- source/version manifests

Not allowed before F0 gate:
- actual F2 domain-contract implementation
- PIT kernel implementation
- production provider adapters
- model implementation
- production calibration/P_safe
- S-Tier engine
- optimizer
- PWA implementation

## Current project conclusion

Engineering preparation is substantially ahead of the implementation gate.

Primary critical-path blocker:
**independent F0 review**

Primary data execution blocker:
**provider credentials / later historical-odds spend**

Primary repository admin risk:
**PUBLIC + unprotected main**
