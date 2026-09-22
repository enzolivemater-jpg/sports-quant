# Football Historical Odds Snapshot Schema Mapping v0.1

Date: 2026-09-22

Status: RESEARCH_MAPPING__NO_F4_CODE

Provider candidate:
The Odds API

Scope:
- Football / EPL engineering bake-off
- Phase 1 markets only:
  - FOOTBALL_1X2
  - FOOTBALL_TOTAL_GOALS_MAIN

## Purpose

Map the provider's documented historical odds response into the future SPORTS QUANT canonical data layer without collapsing distinct provider timestamps into a fabricated `known_at`.

This document is research/design input for F4. It does not approve the provider and does not implement a provider adapter.

## Provider historical response envelope

Current official documentation shows the historical featured-market endpoint returning:

- `timestamp`
- `previous_timestamp`
- `next_timestamp`
- `data`

The requested historical `date` is not necessarily the returned snapshot timestamp.

Documented behavior:
the API returns the closest snapshot equal to or earlier than the requested historical date.

Therefore preserve both:
- requested query timestamp;
- returned provider snapshot timestamp.

Do not silently treat them as identical.

## Event mapping

Provider -> SPORTS QUANT research mapping:

| Provider field | Canonical target | Rule |
|---|---|---|
| `data[].id` | `provider_event_id` | Preserve verbatim as provider external ID. |
| `data[].sport_key` | `provider_sport_key` | EPL documented key is `soccer_epl`; canonical sport remains FOOTBALL. |
| `data[].sport_title` | `provider_sport_title` | Descriptive provider metadata only. |
| `data[].commence_time` | `event_time_candidate` | UTC ISO timestamp; canonical event identity still requires entity resolution. |
| `data[].home_team` | provider home-team label | Never use name alone as final canonical team identity. |
| `data[].away_team` | provider away-team label | Same rule. |

Future F4 must map `provider_event_id` to `canonical_event_id` through deterministic entity resolution.

## Snapshot-time mapping

### Provider wrapper timestamp

`timestamp`

Canonical research field:
- `provider_snapshot_at`

Meaning:
- identity/time of the historical snapshot returned by the provider.

This is the strongest documented candidate for the point-in-time market snapshot reference because the provider explicitly defines the historical endpoint as returning the closest snapshot at or before the requested date.

However:
- F4/F3 must still validate exact semantics before using it as canonical `known_at`;
- it must not be silently copied into `known_at` merely because it is a timestamp.

### Previous snapshot timestamp

`previous_timestamp`

Canonical research field:
- `provider_previous_snapshot_at`

Purpose:
- navigation/audit metadata;
- useful for proving snapshot spacing.

It is not an odds observation by itself.

### Next snapshot timestamp

`next_timestamp`

Canonical research field:
- `provider_next_snapshot_at`

Critical rule:
- navigation metadata only;
- MUST NOT become a feature, decision input or evidence available at the historical cutoff;
- its existence in a response retrieved today must not create future leakage.

Future adapters should keep it outside feature-ready decision data.

### SPORTS QUANT receipt time

Not supplied by provider.

Canonical field:
- `received_at`

Set by SPORTS QUANT at actual retrieval time.

For retrospective historical queries, `received_at` may be years after the historical snapshot. Therefore:
- `received_at` is provenance/retrieval evidence;
- it is NOT a substitute for the historical provider snapshot time.

## Bookmaker mapping

Provider `bookmakers[]`:

| Provider field | Canonical target | Rule |
|---|---|---|
| `key` | `bookmaker_external_id` | Stable provider key candidate; preserve verbatim. |
| `title` | `bookmaker_display_name` | Descriptive; do not use alone as identity. |
| `last_update` | `bookmaker_last_update_at` | Preserve when present. Current docs mark bookmaker-level last_update deprecated. |
| `markets` | nested market observations | Normalize separately. |

Current official docs state market-level `last_update` is the preferred field because markets can update independently.

Therefore future code must not assume every market under one bookmaker shares a single update time.

## Market mapping

Provider `markets[]`:

| Provider field | Canonical target | Rule |
|---|---|---|
| `key=h2h` | `FOOTBALL_1X2` candidate mapping | For soccer, requires three outcomes including Draw when bookmaker provides a complete 1X2 set. |
| `key=totals` | `FOOTBALL_TOTAL_GOALS_MAIN` candidate mapping | Only the canonical main line may qualify; alternate/extra lines must not be silently merged. |
| `last_update` | `market_last_update_at` | Preserve separately from provider snapshot time. |
| `outcomes` | canonical outcome observations | Normalize below. |

The final provider-market-to-canonical-market mapping belongs to F4 contract/adapter implementation and must be tested.

## 1X2 outcome mapping

Provider `h2h` outcomes:

Typical documented soccer names:
- home-team name
- away-team name
- `Draw`

Canonical target:
- HOME
- DRAW
- AWAY

Requirements:
- map team-name outcomes through the resolved canonical event identity;
- do not infer HOME/AWAY from outcome array ordering;
- require a complete mutually exclusive outcome set before no-vig use;
- retain original provider outcome name.

Provider `price`:
- `decimal_odds` when request uses `oddsFormat=decimal`.

SPORTS QUANT should request decimal format explicitly for the pilot to avoid representation ambiguity.

## Total-goals mapping

Provider `totals` outcomes:

Typical documented fields:
- `name`: Over / Under
- `price`: decimal odds
- `point`: total-goals line, e.g. 2.5

Canonical target:
- market_family = FOOTBALL_TOTAL_GOALS_MAIN
- outcome_key = OVER or UNDER
- line = provider `point`
- decimal_odds = provider `price`

Critical rule:
the same event/bookmaker may expose multiple totals lines in some endpoint/market configurations.

Future F4 must identify the provider's canonical/main totals line rather than assuming every `totals` record is `FOOTBALL_TOTAL_GOALS_MAIN`.

If the provider's featured endpoint returns exactly one totals line per bookmaker, that behavior must be verified empirically in the EPL bake-off before becoming an invariant.

## Required raw timestamp fields in the canonical odds observation lineage

Preserve at minimum:

- `requested_snapshot_at`
- `provider_snapshot_at`
- `provider_previous_snapshot_at`
- `provider_next_snapshot_at` as navigation-only metadata
- `bookmaker_last_update_at` when present
- `market_last_update_at` when present
- `received_at`
- future canonical `known_at`
- future `known_at_basis`
- `decision_cutoff_at` when materialized for a decision

Do not collapse these columns.

## Candidate known_at policy — NOT YET CANONICAL

For historical odds snapshots, a plausible candidate is:

- source availability evidence = `provider_snapshot_at`;
- `known_at_basis = VERIFIED_SOURCE_AVAILABILITY`.

But this mapping is NOT approved by this research document.

F3/F4 implementation/review must first establish:
1. whether the returned snapshot timestamp represents provider-recorded market state at that instant;
2. how market-level updates relative to wrapper timestamp should be interpreted;
3. whether later provider corrections can alter the data returned for an old snapshot;
4. whether the provider exposes prior revisions after correction.

Until those tests pass:
- retain `provider_snapshot_at` as source metadata;
- do not claim it is canonical `known_at` automatically.

## Raw payload lineage

For every historical request preserve:

- provider = THE_ODDS_API
- endpoint identity/version
- sport key
- regions requested
- markets requested
- odds format
- requested historical date
- provider snapshot timestamp
- HTTP retrieval metadata where appropriate
- SPORTS QUANT `received_at`
- raw payload or legally permitted immutable equivalent
- payload hash
- ingestion code version
- adapter/schema version

The provider's current terms explicitly permit storage/retention and ML/research use, subject to their redistribution restrictions, as recorded in the licensing audit.

## Canonical observation key proposal

Research candidate for uniqueness:

`canonical_event_id + provider + bookmaker_external_id + market_family + market_instance + outcome_key + provider_snapshot_at`

For totals, `market_instance` must include the line.

Do not use bookmaker `last_update` alone as a uniqueness key:
multiple observations/snapshots may reference the same bookmaker update.

## Staleness diagnostics

At a decision cutoff, preserve enough timestamps to compute diagnostics such as:

- snapshot age relative to cutoff;
- market update age relative to snapshot/cutoff;
- bookmaker update age when market update unavailable.

Exact staleness thresholds remain governed elsewhere and must not be invented in F4.

## Historical navigation leakage rule

`next_timestamp` exists because the historical API is queried retrospectively.

It may reveal that another later snapshot exists.

Therefore:
- keep it only in raw/provider audit metadata;
- exclude it from canonical feature tables;
- exclude it from models;
- exclude it from gate inputs;
- exclude it from historical decision logic.

This should receive an explicit anti-leakage test.

## Minimum adapter tests later required

1. historical wrapper timestamps parsed as timezone-aware UTC;
2. requested timestamp preserved separately from returned snapshot;
3. returned snapshot <= requested timestamp;
4. next_timestamp never enters decision-ready records;
5. event ID preserved;
6. home/away outcomes mapped by canonical event teams, not array order;
7. Draw required for complete 1X2 market;
8. totals Over/Under and point parsed correctly;
9. incomplete market cannot be no-vigged silently;
10. market_last_update preferred/preserved when present;
11. deprecated bookmaker_last_update preserved but not treated as the only market timestamp;
12. received_at recorded independently;
13. raw payload hash stable for identical payload;
14. corrected historical retrieval produces a new raw snapshot/version rather than destructive overwrite;
15. no timestamp is automatically promoted to canonical known_at without the approved mapping rule.

## Current result

Schema compatibility for Football Phase 1:
- 1X2: DOCUMENTED_SCHEMA_FIT
- totals: DOCUMENTED_SCHEMA_FIT
- historical snapshot navigation: DOCUMENTED_SCHEMA_FIT
- exact known_at mapping: REQUIRES_BAKEOFF_VALIDATION
- revision/correction semantics: REQUIRES_BAKEOFF_VALIDATION
- EPL 2024/25 exact bookmaker continuity: REQUIRES_AUTHENTICATED_BAKEOFF

OD-24 remains OPEN.
