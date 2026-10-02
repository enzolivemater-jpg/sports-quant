# SPORTS QUANT — Current Execution Status

Date: 2026-10-02

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
- status: COMPLETE / MERGED / GREEN
- PR #22, final reviewed head `43a15d88b5a5837c54057f26aa50c9b1f1b2e497`
- merge commit `3304c17d1204ec835a6ef21bb2845639b93cd33f`
- independent review: GO (P0=0, P1=0)
- post-merge checks on the merge commit: quality, postgres-integration, dependency-audit, secret-scan — all SUCCESS
- canonical PIT policy: `.project/POINT_IN_TIME_POLICY.yaml` = `APPROVED_F3_POLICY`
- issue #6: CLOSED

F4 Football Data Layer:
- status: READY_TO_IMPLEMENT once the F3 -> F4 transition PR merges
- recorded F4 authorization: `f4.authorized = true` in `.project/PHASE_GATES.toml` (not machine-enforced; see below)
- issue #7
- Phase 1 markets only: `FOOTBALL_1X2`, `FOOTBALL_TOTAL_GOALS_MAIN`
- OD-24 remains OPEN; no provider is approved by the transition

Therefore:
- F4 Football Data Layer implementation: ALLOWED after the transition merges (issue #7)
- F5+ implementation: BLOCKED until F4 acceptance
- research/specification/provider probes: ALLOWED

Machine enforcement:
- `.project/PHASE_GATES.toml`
- `scripts/validate_phase_gates.py` (enforces the F0 review and F2 authorization)

F3 and F4 authorization are recorded in `.project/PHASE_GATES.toml` but are not independently machine-enforced by `scripts/validate_phase_gates.py`.

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

These remain candidates only; none is approved.

StatsBomb Open Data:
- `VERIFIED_RESEARCH_SANDBOX` only
- NOT an approved production provider
- NOT an EPL 2024/25 provider
- NOT a standalone historical context PIT source

The Odds API is deliberately separated because historical requests may consume paid quota. It remains a candidate historical odds provider only.

Credentials/spend tracker:
- issue #18

OD-24:
OPEN — no provider preference is resolved by the F3 -> F4 transition.

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
- F3 PIT Kernel — #6 — COMPLETE
- F4 Football Data Layer — #7 — READY_TO_IMPLEMENT (current critical path)
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

### A. F4 Football Data Layer implementation
Use:
`.ai/handoffs/CLAUDE_F4_IMPLEMENTATION_HANDOFF.md`

Spec:
`docs/contracts/F4_FOOTBALL_DATA_LAYER_SPEC_DRAFT.md`

Issue:
- #7

Must consume F2 contracts and the F3 PIT kernel without bypassing either.

OD-24 remains OPEN: provider adapters stay experimental with explicit roles until resolved.

Requires independent critical review before F5.

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
- production (approved) provider adapters while OD-24 is OPEN
- model implementation
- production calibration/P_safe
- S-Tier engine
- optimizer
- PWA implementation

## Current project conclusion

F0, F2 and F3 gates are closed successfully; F4 is authorized once the transition merges.

Critical path:
**F4 Football Data Layer -> F5 Modeling Harness -> ...**

Primary data execution blocker:
**provider credentials / later historical-odds spend**

Primary repository admin risk:
**PUBLIC + unprotected main**
