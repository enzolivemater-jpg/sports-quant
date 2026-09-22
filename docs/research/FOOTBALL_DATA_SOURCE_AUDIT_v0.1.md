# Football Data Source Audit v0.1

Date: 2026-09-22

Status: RESEARCH_DRAFT__NO_PROVIDER_APPROVED

Authority note: OD-24 remains unresolved. This document evaluates candidate sources only and does not approve a vendor.

## Pilot objective

Support the first Football end-to-end vertical with enough information to validate:

data -> point-in-time integrity -> features -> model -> calibration -> P_safe -> market/no-vig -> gates -> backtest

The critical requirement is not merely "historical data exists". SPORTS QUANT must be able to prove what was knowable at each simulated decision cutoff.

## Candidate sources

### StatsBomb Open Data

Observed capabilities from current public documentation/repository:
- selected football competitions and seasons;
- matches;
- lineups;
- event data;
- StatsBomb 360 for selected matches;
- JSON format suitable for research/prototyping.

Strength:
- excellent structured event-data source for model prototyping and feature research.

Known limitation for SPORTS QUANT:
- open coverage is selective rather than a complete live production feed;
- it does not by itself solve historical market odds;
- publication/update timestamps must not be assumed to equal SPORTS QUANT's canonical `known_at`.

Potential pilot role:
- research/event-feature dataset;
- not approved as the sole Football source.

### The Odds API

Observed capabilities from current official documentation:
- historical bookmaker-odds snapshots;
- historical featured-market data from 2020-06-06;
- snapshots at 10-minute intervals historically, 5-minute intervals from September 2022;
- historical event odds at a requested timestamp;
- additional historical markets from May 2023;
- historical functionality is paid-plan functionality.

Strength:
- unusually useful for point-in-time market reconstruction because the API explicitly exposes historical snapshots at timestamps.

Known limitation for SPORTS QUANT:
- odds alone do not provide the complete sporting/contextual feature set;
- exact bookmaker/sport/market coverage and licensing must be verified for the Football competitions selected;
- snapshot frequency creates a finite temporal resolution that must be reflected in `known_at_basis` and backtest design.

Potential pilot role:
- candidate historical market/no-vig/CLV source.

### Sportradar Soccer API

Observed capabilities from current official documentation:
- historical soccer data available through the Soccer API;
- availability varies by competition and coverage tier;
- documentation states a current-season-plus-two-previous-seasons rule of thumb, with some competitions extending back to 2007;
- season lineups, missing players, statistics and other historical feeds are documented.

Strength:
- broad licensed-data candidate with competition-dependent historical depth.

Known limitation for SPORTS QUANT:
- historical depth and field availability are not uniform;
- exact competition coverage must be audited before architecture depends on it;
- point-in-time semantics for revisions/publication must be explicitly tested rather than inferred.

Potential pilot role:
- licensed comprehensive sports-data candidate.

### Sportmonks Football API

Observed capabilities from current official documentation:
- broad football competition coverage;
- schedules and historical results;
- match statistics and in-play events;
- lineups, formations, squads and player profiles;
- pre-match/in-play odds;
- xG and other match features;
- injuries/suspensions through sidelined records with start/end dates and completion state.

Strength:
- one-source convenience for a fast pilot because many Football entities are exposed through one API family.

Known limitation for SPORTS QUANT:
- an injury start date is not automatically the same thing as the earliest time SPORTS QUANT could have known the information;
- odds-history granularity and historical revision semantics must be validated for the intended backtest;
- league-by-league historical depth and license conditions require verification.

Potential pilot role:
- candidate rapid integration source for fixtures/context/stats.

## Point-in-time qualification tests required before provider approval

Every candidate provider must pass explicit tests for:

1. source timestamp semantics;
2. update/revision timestamps;
3. ability to retrieve or reconstruct historical values as they existed before event time;
4. no silent backfill of data that became known only later;
5. stable entity identifiers;
6. competition/season coverage;
7. missing-data behavior;
8. deduplication and correction behavior;
9. legal/licensing permissions for storage, modeling and derived outputs;
10. reproducible snapshot extraction.

## Fast pilot evaluation plan

Run a small provider bake-off on a fixed Football sample before OD-24 is resolved.

Required sample:
- at least one top domestic league;
- a date range containing completed fixtures;
- pre-match odds snapshots;
- lineups;
- at least one contextual availability signal if exposed;
- final results for outcome labels.

For each candidate measure:
- coverage completeness;
- PIT defensibility;
- timestamp quality;
- entity-resolution difficulty;
- API stability;
- historical depth;
- latency/freshness where relevant;
- integration effort;
- license constraints;
- marginal value versus another source.

## Current fastest research path

For engineering speed only, not provider approval:
- StatsBomb Open Data can bootstrap event-feature research immediately;
- The Odds API is a strong candidate for market snapshot reconstruction;
- Sportmonks and Sportradar should be tested as broader production-data candidates.

A mixed-source architecture is acceptable only if provenance, entity resolution and PIT semantics remain explicit.

## Decision state

OD-24: OPEN.

No provider or provider combination is approved by this document.


### API-Football

Observed capabilities from current official documentation:
- fixtures, results, events, lineups, player/match statistics;
- injuries and suspensions;
- predictions;
- pre-match and live odds;
- competition/season coverage flags;
- lineups typically appear shortly before kickoff;
- injury feed is periodically updated;
- pre-match odds endpoint retains only the last seven days of odds history.

Strength:
- broad, inexpensive integration candidate for prospective/live Football capture;
- useful coverage flags allow the ingestion layer to detect unsupported data categories instead of silently treating missing data as zero.

Critical limitation for SPORTS QUANT:
- the seven-day pre-match odds retention window makes it unsuitable as the sole source for long-horizon historical market reconstruction;
- live/injury/lineup data still require SPORTS QUANT-owned raw snapshots to establish defensible `received_at` and `known_at`.

Potential pilot role:
- prospective live/context ingestion candidate;
- not a substitute for a dedicated historical-odds source.
