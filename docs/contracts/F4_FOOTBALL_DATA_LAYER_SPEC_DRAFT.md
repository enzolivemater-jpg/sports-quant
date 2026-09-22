# F4 Football Data Layer — Draft Ready Specification

Date: 2026-09-22

Status: DRAFT_READY__BLOCKED_BY_F0_REVIEW_F2_F3

Pilot sport: FOOTBALL

## Objective

Build the first provider-backed, provenance-complete, PIT-safe Football data layer.

F4 consumes F2 contracts and the F3 PIT kernel. It must not bypass either.

## Architecture principle

Use adapters per provider and a canonical internal schema.

Provider payloads must never leak vendor-specific assumptions into model code.

Flow:

provider -> immutable raw capture -> provider adapter -> canonical records -> PIT filter/materialization -> feature-ready datasets

## Initial provider roles

No role is approved until OD-24 is resolved.

Current candidates:
- The Odds API: historical market snapshots;
- StatsBomb Open Data: free event-data research sandbox;
- Sportradar: licensed comprehensive sports-data candidate;
- Sportmonks: broad fixture/context/statistics candidate;
- API-Football: low-cost prospective/live context candidate.

## Required layers

### Raw zone

Store legally permitted raw provider responses or equivalent immutable source snapshots.

Metadata:
- provider
- endpoint/resource
- request parameters
- retrieved_at / received_at
- provider timestamp(s)
- payload hash
- ingestion version
- HTTP/status metadata when relevant

Never edit a raw snapshot in place.

### Normalized provider zone

Parse provider-specific payloads into typed provider records.

Keep:
- original external IDs;
- provider timestamps;
- raw snapshot reference;
- parsing version.

### Canonical domain zone

Resolve into canonical:
- competition
- season
- team
- player
- event
- market
- odds observation
- context claim
- result/stat record

Preserve many-to-one provider ID mapping where necessary.

### PIT materialization

Use F3 only.

No adapter may implement its own weaker "as of" shortcut.

## Football pilot scope

### Competition

Engineering provider-bakeoff sample:
- EPL 2024/25

Free event-data sandbox:
- EPL 2015/16 via StatsBomb Open Data

Neither choice is a profitability claim.

### Phase 1 markets

- FOOTBALL_1X2
- FOOTBALL_TOTAL_GOALS_MAIN

No Phase 2 market implementation during the first data-layer milestone unless explicitly authorized.

## Entity resolution

Minimum deterministic mapping:
- provider competition ID -> canonical competition ID
- provider season ID -> canonical season ID
- provider team ID -> canonical team ID
- provider event ID -> canonical event ID
- provider player ID -> canonical player ID where player context is used
- bookmaker ID/name normalization

Rules:
- never merge entities solely by fuzzy name match without review/evidence;
- record mapping method and confidence/review state;
- preserve aliases;
- detect name collisions;
- test promoted/relegated and renamed teams.

## Deduplication

Canonical uniqueness examples:
- one canonical fixture per competition + season + event identity;
- multiple provider records may map to the same canonical fixture;
- odds observations remain distinct by bookmaker, market, outcome and snapshot time.

Do not deduplicate away legitimate price changes.

## Missing data

Never replace missing values with zero unless zero is semantically the true observed value.

Required distinctions:
- not provided by source
- endpoint unavailable
- field unsupported for competition
- record not yet published
- parse error
- verified zero value

Map these distinctions through F2 data-state contracts.

## Conflict handling

If providers disagree on decision-critical facts:
- retain both source observations;
- set conflict state appropriately;
- resolve only through documented source hierarchy/evidence;
- never silently choose whichever record arrived last.

## Provider corrections

When a provider changes a historical record:
- store new version;
- preserve old version if legally/technically possible;
- set supersession lineage;
- let F3 determine which version was usable at each historical cutoff.

## Initial ingestion priorities

1. competitions/seasons
2. teams
3. fixtures/event times
4. final results
5. historical Phase 1 odds
6. provider timestamp metadata
7. lineups/context for prospective capture
8. optional prior-match stats after PIT audit

## Data-quality checks

At minimum:
- schema validation
- timezone validation
- duplicate fixture detection
- home/away consistency
- impossible score checks
- result/status consistency
- odds positivity/format validation
- bookmaker/market completeness metrics
- event-time changes
- missingness profile
- provider revision rate
- entity-resolution exceptions

## Football pilot acceptance dataset

Must satisfy the manifest in:
`docs/research/FOOTBALL_PILOT_DATASET_MANIFEST_v0.1.md`

Feature governance:
`docs/research/FOOTBALL_FEATURE_GOVERNANCE_v0.1.md`

Provider evaluation:
`docs/research/FOOTBALL_PROVIDER_BAKEOFF_PLAN_v0.1.md`

## Required tests

1. provider payload -> normalized record.
2. normalized -> canonical mapping.
3. external IDs preserved.
4. raw snapshot lineage preserved.
5. duplicate fixture handling.
6. conflicting provider observation handling.
7. missing field remains missing.
8. zero value not confused with missing.
9. odds snapshots retain bookmaker + timestamp granularity.
10. provider correction creates version, not destructive overwrite.
11. F3 PIT replay excludes later revisions.
12. deterministic dataset rebuild from fixed raw snapshots.
13. source taxonomy mapping.
14. unsupported competition feature marked explicitly.
15. malformed payload fails visibly.
16. secret/API credentials never written to repository/logs.

## Secrets

Credentials:
- environment/secret store only;
- never commit to Git;
- redact from logs;
- rotate immediately if exposed.

## Observability

Minimum structured telemetry:
- provider
- endpoint
- ingestion run ID
- request count
- error count
- row count
- latency
- last successful receipt time
- missingness anomalies
- revision count

Do not add a heavy monitoring stack unless needed.

## Explicit non-goals

F4 does not:
- choose Football model champion;
- implement production features beyond validated materialization plumbing;
- define calibration;
- define P_safe;
- qualify bets;
- build parlay logic;
- build frontend.

## Acceptance

F4 first milestone is green only when:
- at least one Football fixture/results source is integrated;
- at least one historical Phase 1 odds source is integrated or explicitly blocked with evidence;
- EPL sample can be rebuilt deterministically;
- entity resolution passes;
- raw-to-canonical provenance is complete;
- PIT replay tests pass;
- missingness/conflict/revision checks pass;
- no credential leakage exists.
