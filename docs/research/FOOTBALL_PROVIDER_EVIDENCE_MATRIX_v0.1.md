# Football Provider Evidence Matrix v0.1

Date: 2026-09-22

Status: DOCUMENTATION_EVIDENCE_ONLY__OD-24_OPEN

This matrix records what current official/public documentation supports. It does not approve a provider.

## The Odds API

### Documented
- historical odds snapshots for covered sports/bookmakers;
- featured-market historical data from 2020-06-06;
- 10-minute snapshots historically;
- 5-minute snapshots from September 2022;
- additional-market history from May 2023;
- historical endpoint returns the closest snapshot equal to or earlier than requested timestamp;
- historical access requires a paid plan.

### SPORTS QUANT fit
Strongest documented candidate currently identified for:
- historical market reconstruction;
- no-vig backtests;
- market movement snapshots;
- later CLV-oriented analysis where suitable observations exist.

### Unknown / must test
- exact EPL 2024/25 bookmaker coverage for required regions;
- exact Football 1X2 + total-goals availability at every selected cutoff;
- bookmaker continuity across season;
- revision/correction semantics;
- legal storage/derived-use constraints;
- marginal cost at target extraction volume.

### Current role state
CANDIDATE_HISTORICAL_ODDS

---

## API-Football

### Documented
- free plan: 100 requests/day;
- all endpoint families available on free plan, with season-depth limitations;
- fixtures, results, events, lineups, injuries/sidelined, statistics, predictions, pre-match and live odds;
- paid tiers increase request volume and historical range;
- current official guidance states pre-match odds endpoint can retrieve only odds data from the last 7 days.

### SPORTS QUANT fit
Good low-cost candidate for:
- prospective/live context capture;
- fixtures and current competition coverage tests;
- lineups/injuries/statistics exploration;
- rapid API integration experiments.

### Critical limitation
Not suitable as the sole long-horizon historical odds source under the documented seven-day odds-retention behavior.

### Unknown / must test
- exact EPL 2024/25 historical depth for non-odds endpoints on chosen plan;
- provider timestamps per endpoint;
- revision semantics;
- historical injury/lineup as-of behavior;
- raw-storage and derivative-use terms.

### Current role state
CANDIDATE_PROSPECTIVE_CONTEXT
NOT_PRIMARY_HISTORICAL_ODDS

---

## Sportmonks

### Documented
- more than 2,200 football leagues/cups marketed;
- fixtures, historical results, live data, events, squads, player data, lineups, stats, odds and xG-related options;
- free access for limited leagues/testing;
- paid plans with 14-day trial;
- Starter advertised from EUR 29/month;
- historical-data add-on currently advertised from EUR 29 one-time;
- odds/predictions and premium odds are separate/additional offerings depending on plan.

### SPORTS QUANT fit
Potential one-vendor convenience for:
- fixtures;
- context;
- stats;
- lineups;
- xG;
- prospective odds.

### Unknown / must test
- exact EPL historical field coverage;
- exact historical odds granularity and retention;
- source publication/update timestamp semantics;
- whether old revisions remain queryable;
- injury/sidelined publication chronology;
- licensing for raw snapshot retention and model-derived outputs.

### Current role state
CANDIDATE_BROAD_FOOTBALL_PROVIDER

---

## Sportradar Soccer

### Documented
- Soccer API includes historical statistics;
- historical availability varies by competition/field;
- competition-season endpoints and historical feeds exist;
- Season Missing Players exposes fields including start_date, reason, status and estimated_return_date;
- Premier League has documented competition identifier examples;
- trial defaults currently documented as 30 days, 1,000 requests per rolling 30 days and 1 QPS.

### SPORTS QUANT fit
Strong licensed-data candidate for:
- structured competition/season data;
- lineups;
- missing players;
- broader production-grade football data.

### Important PIT caution
A field such as missing-player `start_date` must not automatically be treated as the moment SPORTS QUANT first could have known the information. Provider semantics must be validated.

### Unknown / must test
- EPL 2024/25 field-by-field accessibility under trial/product;
- revision history;
- publication/update timestamps;
- old-version retrievability;
- commercial licensing/storage terms;
- any separate odds product required for the market leg.

### Current role state
CANDIDATE_LICENSED_COMPREHENSIVE_DATA

---

## StatsBomb Open Data

### Verified by direct repository probe
- current public competition manifest includes EPL 2015/16 and 2003/04, not EPL 2024/25;
- EPL 2015/16 match file contains 380 matches and 20 team IDs;
- event and lineup payloads are rich and directly inspectable;
- one sample match contained 3,732 events;
- currently published match records expose dataset `last_updated` timestamps years after the original matches.

### SPORTS QUANT fit
Excellent free source for:
- parser development;
- event schema R&D;
- event-feature prototyping;
- lineup/event joins.

### Critical PIT limitation
Current repository `last_updated` is dataset-update metadata, not proof of historical information availability before the fixture.

### Current role state
VERIFIED_RESEARCH_SANDBOX
NOT_EPL_2024_25_SOURCE
NOT_STANDALONE_HISTORICAL_CONTEXT_PIT_SOURCE

---

## Current evidence-based architecture hypothesis

Not a provider decision:

- historical market leg -> test The Odds API first;
- free event-feature R&D -> StatsBomb Open Data;
- prospective context -> test API-Football / Sportmonks / Sportradar;
- broader production sports-data role -> compare Sportmonks vs Sportradar on the same EPL sample.

## Fastest test order

1. StatsBomb Open sandbox — already partially verified.
2. API-Football free — zero-cost schema/context probe.
3. Sportradar trial — licensed-data PIT/coverage probe.
4. Sportmonks free/trial — broad-data comparison.
5. The Odds API paid historical test — purchase only when ready to collect the fixed EPL market sample.

## OD-24 rule

Do not resolve OD-24 until the provider bake-off has produced:
- coverage evidence;
- PIT evidence;
- license/storage evidence;
- cost evidence;
- reproducibility evidence;
- explicit residual risks.
