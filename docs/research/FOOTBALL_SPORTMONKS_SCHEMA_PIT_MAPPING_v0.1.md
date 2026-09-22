# Football Sportmonks Schema / PIT Mapping v0.1

Date: 2026-09-22

Status: RESEARCH_MAPPING__NO_F4_CODE

Provider candidate:
Sportmonks Football API v3

Provisional role:
- broad fixture/context/statistics provider;
- prospective lineup/sidelined/context capture;
- not yet approved for historical decision-critical mutable context.

## Purpose

Map Sportmonks Football entities into the future SPORTS QUANT Football data layer while distinguishing:
- event time;
- provider processing/update metadata;
- contextual validity dates;
- actual information availability;
- SPORTS QUANT receipt time.

No provider date may be silently promoted to canonical `known_at`.

## Fixture spine

Current official documentation identifies the fixture as the central Football API entity.

Documented base fixture fields include:
- fixture ID;
- league ID;
- season ID;
- stage/round/group IDs;
- venue ID;
- starting datetime;
- match state;
- result information;
- odds availability;
- `last_processed_at`.

Research mapping:

| Sportmonks field | SPORTS QUANT target | Rule |
|---|---|---|
| `id` | `provider_event_id` | Preserve verbatim. |
| `league_id` | provider competition ID | Resolve to canonical competition. |
| `season_id` | provider season ID | Resolve to canonical season. |
| `starting_at` | `event_time_candidate` | Normalize explicitly to timezone-aware UTC. |
| `state_id` | provider event state | Map through provider adapter, not directly to labels. |
| `result_info` | post-event result metadata | Must never enter pre-match features. |
| `has_odds` | provider capability flag | Not evidence that historical odds are available at every cutoff. |
| `last_processed_at` | `provider_fixture_last_processed_at` | Preserve as provider processing metadata; do not automatically use as known_at for nested context. |

## Fixture update feed

Sportmonks documents a "Latest Updated Fixtures" endpoint returning fixtures updated within the last 10 seconds.

Potential prospective use:
- efficient live/update polling;
- detect fixture/state changes;
- trigger immutable SPORTS QUANT snapshots.

PIT rule:
the fact that a fixture was returned as recently updated may establish a provider-side update signal at retrieval time, but the exact semantic of each nested entity still needs separate handling.

## Participants / entity resolution

Future canonical mapping must preserve:
- Sportmonks team IDs;
- team names;
- home/away location;
- fixture ID;
- canonical team IDs.

Do not entity-match teams by display name alone.

Sportmonks' stable numeric IDs are useful provider keys, but canonical SPORTS QUANT identity remains provider-independent.

## Confirmed lineups

Current Sportmonks documentation exposes fixture `lineups`.

Documented fields include:
- player_id;
- team_id;
- position_id;
- formation_field;
- type_id;
- formation_position;
- player_name;
- jersey_number.

Current documentation identifies:
- type_id 11 = starting player;
- type_id 12 = substitute.

Current implementation guidance states confirmed lineups are typically available around 60–75 minutes before kickoff.

Research mapping:

| Sportmonks field | SPORTS QUANT target |
|---|---|
| player_id | provider_player_id |
| team_id | provider_team_id |
| type_id | lineup_role |
| position_id | provider_position_id |
| formation_position | provider formation order |
| formation_field | provider formation grid |
| jersey_number | jersey number |

Critical PIT rule:
a lineup contained in a historical/current fixture payload does not prove when that lineup first became available historically.

For prospective capture:
- poll/snapshot before kickoff;
- set SPORTS QUANT `received_at`;
- preserve raw payload;
- derive canonical `known_at` under F3/F4 approved policy.

For retrospective backtests:
- do not use final lineup at a simulated cutoff unless historical source availability at/before that cutoff is defensible.

## Expected lineups

Sportmonks separately exposes Premium Expected Lineups.

Current docs state:
- expected lineups are model-generated predictions;
- they are distinct from official/confirmed lineups;
- availability timing varies by subscription/product;
- `lineup_confirmed` on the fixture is the distinction between prediction and confirmed lineup.

Canonical distinction required:
- EXPECTED_LINEUP
- CONFIRMED_LINEUP

Never overwrite one with the other.

Prediction source provenance must be preserved because Sportmonks expected lineup is itself a model output, not an official fact.

Potential SPORTS QUANT use:
- structured context;
- challenger feature after prospective validation.

Do not treat expected lineup as verified official lineup.

## Sidelined / injuries / suspensions

Current Sportmonks `sidelined` records document:
- player ID;
- team ID;
- season ID;
- type ID;
- category;
- start date;
- end date when known;
- games missed;
- completed flag.

Includes:
- fixture.sidelined
- team.sidelined
- team.sidelinedHistory
- player.sidelined

### Critical temporal distinction

`start_date` means start of an unavailability period.

It does NOT necessarily mean:
- date/time the injury was first reported;
- date/time Sportmonks first received the information;
- date/time a bettor could know the information.

Likewise:
- `end_date` is not publication time;
- `completed` is current/record state, not historical announcement time.

Therefore historical sidelined records cannot directly establish canonical `known_at`.

### Prospective policy

For every captured sidelined response record:
- provider entity IDs;
- semantic start/end dates;
- provider type/category;
- SPORTS QUANT received_at;
- raw payload hash;
- retrieval endpoint/include;
- ingestion version;
- future known_at/known_at_basis after approved F3/F4 mapping.

This progressively creates a genuine historical availability dataset.

## Corrections / mutable state

Sportmonks publicly states that when corrections occur, fixture/event data updates in place under the same IDs.

PIT implication:
- stable IDs are useful;
- current API state may reflect a correction that was not known at an earlier historical cutoff;
- current corrected values must not overwrite SPORTS QUANT's previously captured raw snapshot.

Prospective F4 should use append/version semantics:
- old raw response immutable;
- new retrieval stored as a new source version;
- F3 later selects the version legitimately known at each cutoff.

## Prematch news

Fixtures support `prematchNews`.

Potential use:
- structured contextual evidence;
- Sports Intelligence input.

Before production use, audit:
- article/source provenance;
- publication timestamps;
- update semantics;
- licensing/display constraints;
- coverage consistency.

No narrative/news field may directly assign P_safe.

## Weather

Fixture includes support `weatherReport`.

Potential later feature:
- weather at/near fixture.

Required before use:
- distinguish forecast issue time from event valid time;
- capture forecast revision history;
- evaluate OOS incremental value.

Current weather value retrieved after the match must never be used as if it were the historical forecast.

## Odds

Sportmonks supports regular odds and Premium Odds.

Current Premium Odds documentation states:
- 120+ bookmakers;
- 42 markets;
- pre-match update cadence around one minute;
- opening odds + every change;
- odds history up to seven days after kickoff;
- last-updated timestamp per odds entry.

Research implication:
- potentially strong prospective market feed;
- useful short-window replay if captured promptly;
- not by itself a long-term historical odds archive when history is only retained for a limited period.

Current project strategy therefore remains:
- The Odds API first historical-market candidate;
- Sportmonks broad/context candidate;
- compare Sportmonks odds later for prospective/consensus value.

## Fixture includes relevant to SPORTS QUANT

Potential research includes:
- participants
- lineups
- expectedLineups
- sidelined
- prematchNews
- weatherReport
- referees
- coaches
- statistics
- xGFixture
- odds / premiumOdds

Do not request every include by default.

F4 should prefer minimal endpoint payloads because:
- larger responses cost rate-limit capacity;
- it reduces schema complexity;
- it makes provenance and missingness easier to audit.

## Canonical timestamp candidates to preserve

At minimum when present:
- event `starting_at`
- fixture `last_processed_at`
- nested entity update timestamps if available
- semantic sidelined `start_date`
- semantic sidelined `end_date`
- odds entry update time
- SPORTS QUANT `received_at`
- future canonical `known_at`
- future `known_at_basis`
- decision cutoff

Never collapse:
- event time
- semantic validity period
- provider update time
- information availability time
- retrieval time.

## Stage B prospective provider probe

A free/trial probe should select a small set of upcoming EPL fixtures and poll:

### T-24h
- fixture/participants
- sidelined
- expected lineup if available
- weather if available
- odds if available

### T-90m
- same snapshot

### T-75m
- same snapshot

### T-60m
- confirmed lineup status
- lineups

### T-30m
- confirmed lineup
- sidelined/context revisions
- odds

### Post-kickoff / post-match
For research only:
- settlement/result
- correction behavior

Purpose:
measure when each field actually appears and how it changes.

This prospective probe can establish real `received_at` evidence even when historical publication chronology is unavailable.

## Minimum future adapter tests

1. fixture IDs preserved.
2. event times timezone-normalized.
3. result_info unavailable to pre-match feature materialization.
4. last_processed_at retained separately from known_at.
5. expected and confirmed lineups never conflated.
6. lineup starter/substitute types mapped explicitly.
7. sidelined start_date never treated as publication time.
8. missing end_date preserved as unknown/open, not invented.
9. completed state does not rewrite old snapshots.
10. provider correction creates new SPORTS QUANT source version.
11. stable provider IDs map deterministically to canonical IDs.
12. received_at recorded on every prospective snapshot.
13. raw hash retained.
14. mutable nested entity updates do not destructively overwrite old source versions.
15. premium odds history retention limitation is surfaced.
16. no nested provider timestamp becomes canonical known_at without approved rule.

## Current role assessment

Fixture/results spine:
- DOCUMENTED_FIT

Entity IDs:
- DOCUMENTED_FIT

Confirmed lineup prospective capture:
- DOCUMENTED_FIT

Expected lineup:
- DOCUMENTED_FIT_AS_MODELLED_CONTEXT

Sidelined prospective capture:
- DOCUMENTED_FIT

Historical sidelined known_at:
- NOT_ESTABLISHED

Historical final-lineup availability time:
- NOT_ESTABLISHED

Correction-safe retrospective mutable context:
- NOT_ESTABLISHED_WITHOUT_OWN_SNAPSHOTS

Premium odds prospective use:
- DOCUMENTED_CANDIDATE

Long-term odds history:
- NOT_PRIMARY_ROLE

## OD-24

OPEN.

This mapping strengthens Sportmonks' candidate role for broad Football and prospective context, but authenticated EPL coverage/timestamp/revision tests are still required.
