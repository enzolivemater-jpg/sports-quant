# Football Provider Probe Execution Matrix v0.1

Date: 2026-09-22

Status: READY_FOR_CREDENTIALLED_RESEARCH_PROBES

OD-24: OPEN

This document defines the execution order for provider trials. It does not approve any vendor.

## Global rules

Every authenticated probe must:
- use `scripts/research/capture_provider_json.py`;
- store raw payloads only under ignored local `data/research-probes/`;
- record SPORTS QUANT `received_at`;
- preserve payload SHA-256;
- keep request metadata redacted;
- never assign canonical `known_at`;
- never write API keys to Git, issues, docs, screenshots or logs;
- preserve failures and missing responses instead of cherry-picking successes.

A provider role fails when the evidence required for that role cannot be established. Failure for one role does not automatically reject the provider for every other role.

## Probe order

### P1 — API-Football free probe

Cost objective:
- zero recurring spend;
- stay within current free-tier quota while testing schema/PIT behavior.

Research role:
- fixtures/entity spine;
- prospective injuries/suspensions;
- prospective lineups;
- low-cost context capture.

Do not test it as the primary long-horizon historical odds archive.

Evidence sequence:
1. league/season coverage metadata for EPL;
2. fixture list and stable fixture/team IDs;
3. injury endpoint shape for selected fixtures/teams;
4. lineup endpoint shape;
5. paging behavior;
6. timezone behavior;
7. odds retention behavior/documented unavailability for older windows;
8. prospective repeated captures around one or more future fixtures when feasible.

Pass evidence for prospective-context candidacy:
- stable IDs;
- explicit unsupported/missing behavior;
- raw responses capture cleanly;
- lineups/injuries can be observed prospectively;
- no secret leakage;
- response cadence/quota workable for a small pilot.

Hard stop for historical mutable context role:
- current-state records without historical first-publication evidence.

### P2 — Sportmonks free/trial probe

Research role:
- broad fixtures/context/statistics;
- expected vs confirmed lineups;
- sidelined records;
- prospective odds/context challenger.

Evidence sequence:
1. fixture/participant IDs;
2. EPL availability on trial;
3. `starting_at` and fixture state semantics;
4. `last_processed_at` behavior;
5. confirmed lineup fields;
6. expected-lineup distinction;
7. sidelined start/end/completed fields;
8. provider update/revision behavior;
9. odds entry timestamps/history limits;
10. prospective repeated captures around selected future fixture(s).

Pass evidence for broad-context candidacy:
- stable entity spine;
- expected/confirmed lineup distinction survives raw capture;
- mutable context can be versioned prospectively;
- trial coverage adequate to test EPL;
- no critical undocumented timestamp assumption is needed.

Hard stop for historical context role:
- start/end/current state used as publication time.

### P3 — Sportradar trial probe

Research role:
- premium/licensed comprehensive Football feed challenger.

Evidence sequence:
1. competition/season coverage;
2. namespaced ID stability;
3. schedule confirmation fields;
4. `generated_at` behavior;
5. season/sport-event lineup structures;
6. missing-player structures;
7. current/historical correction behavior;
8. prospective confirmed-lineup transitions;
9. trial limitations;
10. contract/retention/model-use questions logged separately.

Pass evidence for technical candidacy:
- stable identity model;
- adequate EPL coverage;
- mutable fields can be captured prospectively;
- response metadata can be cleanly separated from historical `known_at`.

Contractual gate:
technical PASS does not resolve licensing/retention/model-use uncertainty.

### P4 — The Odds API historical Stage A

Run only when ready to spend a small historical quota.

Research role:
- historical Football market reconstruction.

Fixed sample:
- EPL 2024/25
- Matchweeks 1–4
- 40 fixtures
- 23 distinct kickoff groups
- T-24h / T-1h / T-15m
- markets: h2h + totals
- one region initially

Current planned maximum Stage A request count:
- 69 historical snapshot requests before retries/schema probes.

Current planned quota envelope:
- use the documented cost model from `FOOTBALL_ODDS_BAKEOFF_STAGE_A_SAMPLE_v0.1.md`;
- re-check pricing/quota documentation immediately before purchase/execution.

Collect:
- requested timestamp;
- returned snapshot timestamp;
- previous/next navigation timestamps;
- event IDs;
- commence times;
- bookmakers;
- bookmaker/market update times;
- prices;
- totals lines;
- missingness;
- payload hash;
- SPORTS QUANT received_at.

Pass evidence:
- reliable EPL event reconciliation;
- useful 1X2 and main-total coverage at target cutoffs;
- timestamp behavior consistent with documentation;
- raw historical payload capture reproducible;
- quota economics acceptable;
- no critical PIT ambiguity.

Fail fast when:
- event reconciliation is unreliable;
- Phase 1 market coverage is materially insufficient;
- returned timing semantics contradict documented assumptions;
- licensing/storage requirements are incompatible.

## Evidence result vocabulary

For every tested dimension use only:
- VERIFIED_PASS
- VERIFIED_FAIL
- PARTIAL
- DOCUMENTED_NOT_PROBED
- UNKNOWN
- NOT_APPLICABLE

Do not use a numeric vendor score.

## Role-based decision table

Possible provider roles:
- HISTORICAL_ODDS
- FIXTURE_RESULTS
- EVENT_RESEARCH
- PROSPECTIVE_CONTEXT
- PROSPECTIVE_MARKET
- PREMIUM_PRODUCTION_DATA

A provider can pass some roles and fail others.

## OD-24 resolution requirement

OD-24 may be resolved only after:
- evidence records exist for the relevant role;
- PIT limitations are explicit;
- licensing/storage terms are acceptable or explicitly conditioned;
- cost is understood;
- reproducibility is demonstrated;
- residual risk is recorded.

No single-provider architecture is required.
