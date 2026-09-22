# Football Pilot Dataset Manifest v0.1

Date: 2026-09-22

Status: RESEARCH_DESIGN__NO_INGESTION_CODE

Pilot sport: FOOTBALL

## Purpose

Define exactly what the first Football dataset must contain before ingestion code exists.

This is a dataset contract proposal for implementation planning. It does not resolve OD-24, OD-11, calibration thresholds, P_safe or production cutoffs.

## Two-sample strategy

### A. Provider bake-off / pipeline sample

Competition:
- English Premier League

Season:
- 2024/25

Purpose:
- compare providers on identical fixtures;
- reconstruct historical pre-match odds;
- validate entity mapping;
- validate point-in-time metadata;
- exercise Football Phase 1 market structures.

Important:
StatsBomb Open Data is not expected to supply this sample. Current open competition metadata exposes Premier League 2015/16 and 2003/04, not EPL 2024/25.

### B. Free event-data engineering sandbox

Competition:
- English Premier League

Season:
- 2015/16

Source candidate:
- StatsBomb Open Data

Purpose:
- parser development;
- event schema exploration;
- event-feature R&D;
- lineup/event joins;
- reproducible local experiments.

Restriction:
The sandbox is not automatically valid for historical decision-time context. Repository availability/update timestamps must not be substituted for historical `known_at`.

## Canonical fixture row

Required identity:
- canonical_event_id
- sport
- competition_id
- competition_name
- season_id
- season_name
- event_time
- home_team_id
- away_team_id

Required labels after completion:
- home_goals
- away_goals
- result_1x2
- total_goals
- event_status

Labels must never be visible to a feature computation before event completion.

## Pre-match market snapshot row

Initial Phase 1 markets only:
- FOOTBALL_1X2
- FOOTBALL_TOTAL_GOALS_MAIN

Required fields:
- canonical_event_id
- bookmaker_id
- market_family
- market_type
- market_instance
- outcome_key
- decimal_odds
- provider_snapshot_at
- received_at
- known_at
- known_at_basis
- source_id
- source_tier
- raw_payload_hash
- quality_state
- freshness_state
- verification_state
- conflict_state

Research cutoffs for provider comparison:
- T-24h
- T-6h
- T-1h
- T-30m
- T-15m
- nearest defensible pre-kickoff snapshot

These are bake-off observation points, not final production decision cutoffs.

## Match-state feature table

Every row is an as-of feature snapshot keyed by:
- canonical_event_id
- feature_cutoff_at
- feature_set_version

Initial PIT-safe feature families:

### Team strength
- sequential Elo/rating before fixture
- opponent-adjusted strength if computed strictly from prior matches
- home/away strength components

### Recent results
- prior-match points/form windows
- prior goals scored
- prior goals conceded
- prior goal difference

### Schedule
- days since previous match
- matches played in trailing windows
- congestion indicators derived only from known schedule/results

### Competition state
- reconstructed points/table position before fixture
- games played before fixture
- season phase
- promoted/new-season indicators if source state is known before cutoff

### Optional advanced historical stats
Only if PIT defensibility exists:
- xG for prior completed matches
- shots
- possession
- PPDA or similar

No current/future match statistic may leak into the pre-match feature row.

## Prospective context snapshot table

This table is built forward in real time rather than fabricated retrospectively.

Candidate categories:
- official lineup
- expected lineup
- injuries
- suspensions
- squad availability
- coach/manager changes
- weather
- trusted contextual claims

Required fields:
- canonical_event_id
- entity_id
- claim_type
- structured_value
- source_id
- source_tier
- provider_published_at if present
- received_at
- known_at
- known_at_basis
- valid_from
- valid_to
- expires_at
- quality_state
- freshness_state
- verification_state
- conflict_state
- raw_payload_hash
- ingestion_version

## Explicitly forbidden initial retrospective features

Unless a defensible point-in-time source proves prior availability:
- historical injury status reconstructed from current profile state
- historical "expected lineup" generated after the match
- final starting lineup used for a cutoff before it was officially known
- post-match xG or event statistics for the target fixture
- current league table backfilled into an old date
- current player/team ratings copied into historical rows
- closing odds used for an earlier decision cutoff
- any feature whose timestamp is missing and silently imputed

Missing values must remain missing/unknown according to contract. They must not be silently replaced by zero.

## Dataset lineage

Each materialized dataset must record:
- dataset_version
- extraction_run_id
- code_version
- provider/source list
- extraction_started_at
- extraction_completed_at
- source snapshot identifiers where available
- row counts
- missingness summary
- PIT validation result
- schema version
- feature_set_version

## Split design

No random match-level split.

Required chronology:
- training window
- validation window
- calibration window
- untouched final test window
- repeated walk-forward folds

Exact season boundaries and sample-size thresholds remain unresolved until data coverage is measured.

## Initial success criteria

The pilot dataset is ready for modeling only if:
1. fixture/entity mapping is deterministic;
2. no duplicate canonical fixtures remain;
3. event times are timezone-aware;
4. historical market observations have defensible timestamps;
5. feature rows can be reproduced from data known before each cutoff;
6. labels are isolated from feature computation;
7. missingness is explicit;
8. provider revisions are auditable;
9. raw-to-canonical lineage exists;
10. leakage tests pass.

## Non-goal

This manifest does not claim EPL is the most profitable league. It is the first engineering testbed.
