# Pre-F2 Readiness Audit

Date: 2026-09-22

Status: SATURATED_PREPARATION__IMPLEMENTATION_BLOCKED_BY_G0

Reviewed repository HEAD:
`04d6526514b53c91a4463fec3e083971ccdbfc7c`

## Executive result

SPORTS QUANT has enough architecture, research design, phase specifications and handoffs to begin F2 immediately once the independent F0 gate is legitimately opened.

Additional speculative documentation before new evidence is available has diminishing value and should stop.

## What is ready

### Repository foundation
- Python packaging
- locked dependencies
- CI
- Security workflow
- PostgreSQL local/test plumbing
- Alembic skeleton
- observability scaffold
- machine-checkable phase gate

Current HEAD before this audit:
- CI: SUCCESS
- Security: SUCCESS

### Governance
- Foundation canonical YAMLs
- OD-01 through OD-29 preserved
- sport-scope ADRs
- Football first-pilot ADR
- F0 independent review prompt
- F0 review record template
- F0 closure procedure
- F0 outcome routing
- machine gate preventing premature F2 implementation

### Implementation design
Prepared specifications:
- F2 Contracts
- F3 PIT Kernel
- F4 Football Data Layer
- F5 Football Modeling Harness
- F6 Football Market Engine
- F7 Calibration / uncertainty / P_safe
- F8 S-Tier
- F9 Backtesting
- F10 Dependency / Parlay
- F11 Paper Betting / Monitoring
- F12 PWA

### Implementation handoffs
Claude handoffs exist for F2 through F12.

### Football research
Prepared:
- PIT acceleration strategy
- provider bake-off
- provider evidence/licensing mapping
- API-Football / Sportmonks / Sportradar mappings
- historical odds Stage A plan and tooling
- StatsBomb sandbox probe
- OpenFootball research baseline
- Football feature governance
- baseline model mathematics
- temporal evaluation plan
- Champion/Challenger benchmark plan
- calibration / uncertainty / P_safe decision protocol
- no-vig / edge decision protocol
- model agreement / drift decision protocol
- dependency / parlay decision protocol
- Sports Intelligence decision protocol

### Research tooling
Prepared:
- provider capture harness
- provider probe runner/evidence renderer
- Stage A odds runner/reconciliation/coverage tools
- OpenFootball parser
- security/redaction tests

## What is NOT ready and why

### B1 — Independent F0 review
Status:
BLOCKING_F2

Evidence:
- issue #1 open
- no independent review comment/artifact recorded
- phase gate remains PENDING
- f2.authorized=false

Required action:
run the separate GPT/Codex F0 review using:
`.ai/handoffs/START_PROMPT_F0_INDEPENDENT_REVIEW.md`

This is the only governance blocker to starting F2.

### B2 — Repository privacy / branch protection
Status:
ADMIN_ACTION_REQUIRED

Current verified state:
- repository visibility: PUBLIC
- main protected: false

Tracked by:
- issue #17

This should be corrected before provider credentials, proprietary implementation or sensitive commercial/provider material expands.

It does not justify bypassing the F0 gate.

### B3 — Provider trial credentials
Status:
BLOCKS_AUTHENTICATED_PROVIDER_BAKEOFF, NOT_F2

Tracked by:
- issue #18

Needed later for:
- API-Football free probe
- Sportmonks trial
- Sportradar trial
- paid The Odds API historical Stage A

Provider credentials do not block F2 or F3.
They become materially blocking for F4 provider integration.

## Readiness by phase

| Phase | Design ready | Implementation authorized | External dependency |
|---|---|---|---|
| F2 Contracts | YES | NO | F0 independent review |
| F3 PIT | YES | NO | F2 acceptance |
| F4 Football Data | YES | NO | F3 + provider evidence/credentials |
| F5 Modeling | YES | NO | PIT-safe dataset |
| F6 Market | YES | NO | historical odds evidence |
| F7 Calibration/P_safe | YES | NO | OOS model/calibration evidence |
| F8 S-Tier | YES | NO | validated F7 evidence/rules |
| F9 Backtest | YES | NO | F8 stack |
| F10 Parlay | YES | NO | validated single-leg/dependency evidence |
| F11 Paper Betting | YES | NO | live pipeline |
| F12 PWA | YES | NO | stable backend contracts |

## Open decisions

No numbered OD should be resolved before its evidence exists.

Prepared evidence protocols now cover:
- OD-01..09
- OD-12..15
- OD-18..24 where applicable

Deferred/late decisions remain deferred:
- OD-16
- OD-17
- OD-25
- OD-26
- OD-27
- OD-28
- OD-29 according to its authorized phase

## Stop-work rule before F0 review

Do not create another architecture/specification document merely because the gate is still closed.

Before new external evidence arrives, useful work is limited to:
- fixing CI/security regressions;
- completing F0 independent review;
- repository hardening;
- authenticated provider probes if credentials become available;
- correcting verified documentation defects;
- recording new evidence.

Do NOT:
- implement F2 business contracts;
- implement F3 PIT;
- start provider production adapters;
- train Football production models;
- invent unresolved OD thresholds;
- polish the PWA.

## Immediate critical path

1. Independent F0 review.
2. Record review artifact.
3. Open machine F2 gate if no unresolved P0/P1.
4. Confirm CI/Security green.
5. Close issue #1.
6. Start Claude F2 using the existing handoff.
7. In parallel, complete repository hardening and provider trials.

## Result

Engineering preparation:
READY

F2 implementation authorization:
BLOCKED

Next meaningful action:
INDEPENDENT_F0_REVIEW

Verdict:
GO_WITH_CONDITIONS
