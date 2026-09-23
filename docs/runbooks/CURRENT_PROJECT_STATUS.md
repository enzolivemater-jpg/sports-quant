# SPORTS QUANT — Current Execution Status

Date: 2026-09-23

Status: ACTIVE

Pilot sport: FOOTBALL

## Governance gate

F0 independent review:
- issue #1: CLOSED
- accepted review artifact: `.project/reviews/F0_REVIEW_RECORD_2026-09-22_e5220707.md`
- F2 machine authorization: OPEN (`f2.authorized = true`)

F2 Domain Contracts:
- status: COMPLETE / MERGED / GREEN
- PR #19, final reviewed head `40a604d9e5ec3e3f2fe0528373f0313874667e8c`
- merge commit `d2cc02b5f5fbfbef2100eb07395e652a731bb31d`
- independent review: GO (P0=0, P1=0)
- CI + Security green on the merge commit
- issue #2: CLOSED

F3 Point-in-Time Kernel:
- status: READY_TO_IMPLEMENT
- machine authorization: OPEN (`f3.authorized = true`)
- issue #6

Therefore:
- F3 PIT kernel implementation: ALLOWED (issue #6)
- F4+ implementation: BLOCKED until F3 acceptance
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
- secret scan now also executes on pull requests (Gitleaks v3, PR #20)

Repository admin state last verified (2026-09-23):
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

- F2 Contracts — issue #2 — COMPLETE
- F3 PIT Kernel — #6 — READY_TO_IMPLEMENT (current critical path)
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

### A. F3 PIT Kernel implementation
Use:
`.ai/handoffs/CLAUDE_F3_IMPLEMENTATION_HANDOFF.md`

Spec:
`docs/contracts/F3_POINT_IN_TIME_KERNEL_SPEC_DRAFT.md`

Requires independent critical review before F4.

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

Not allowed before their phase gates:
- production provider adapters
- model implementation
- production calibration/P_safe
- S-Tier engine
- optimizer
- PWA implementation

## Current project conclusion

F0 and F2 gates are closed successfully; F3 is authorized.

Critical path:
**F3 PIT Kernel -> F4 Football Data Layer -> F5 Modeling Harness -> ...**

Primary data execution blocker:
**provider credentials / later historical-odds spend**

Primary repository admin risk:
**PUBLIC + unprotected main**
