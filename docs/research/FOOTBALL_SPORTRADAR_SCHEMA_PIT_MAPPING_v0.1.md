# Football Sportradar Soccer v4 Schema / PIT Mapping v0.1

Date: 2026-09-22

Status: RESEARCH_MAPPING__NO_F4_CODE

Provider:
Sportradar Soccer v4 / Soccer Extended v4

Provisional role:
- premium/licensed Football data candidate;
- technical coverage/PIT trial;
- production selection requires explicit contract/use/retention review.

## Purpose

Map documented Sportradar Soccer structures into future SPORTS QUANT canonical concepts while preventing misuse of response-generation timestamps as historical information-availability timestamps.

## Stable identity spine

Current documentation uses namespaced IDs including:
- sport event IDs: `sr:sport_event:...`
- competition IDs: `sr:competition:...`
- season IDs: `sr:season:...`
- competitor/team IDs: `sr:competitor:...`
- player IDs: `sr:player:...`

Current ID-handling documentation states season IDs do not change once created.

Research mapping:
- preserve all Sportradar external IDs verbatim;
- map them to SPORTS QUANT canonical IDs;
- never use names alone as canonical identity.

## Event scheduling

Sport-event records document:
- `start_time`
- `start_time_confirmed`
- since 2026, `date_confirmed`

Important distinction:
- a match date may be confirmed while exact kickoff time is not;
- `start_time` can therefore carry a date placeholder when `start_time_confirmed=false`.

SPORTS QUANT rule:
do not treat an unconfirmed start time as a final decision cutoff.

Canonical event scheduling should preserve:
- provider start time;
- date_confirmed;
- start_time_confirmed;
- every prospectively observed schedule revision.

## Response generated_at

Many Sportradar feeds contain top-level:
- `generated_at`

Examples in current documentation show:
- historical season schedules queried years later with a modern `generated_at`;
- season lineups;
- sport event lineups;
- summaries;
- season info.

Critical PIT rule:

`generated_at` means the API response/feed representation was generated at that time.

It does NOT automatically mean:
- the underlying historical lineup was first published then;
- the absence was first known then;
- the event schedule was first known then.

For a historical API request made today:
- generated_at is current retrieval/feed-generation metadata;
- it must not become historical known_at for the underlying old record.

Preserve separately:
- provider_generated_at;
- SPORTS QUANT received_at;
- underlying semantic event times/dates;
- future canonical known_at only when availability evidence is valid.

## Coverage metadata

Season Info exposes detailed coverage flags for competition and sport-event properties, including:
- schedules;
- missing_players;
- team_squads;
- lineups;
- formations;
- scores;
- statistical depths.

SPORTS QUANT should capture coverage metadata per competition/season.

As with other providers:
- coverage available != every record complete;
- coverage unavailable != zero.

## Historical data

Current Sportradar documentation exposes historical data through standard Soccer API feeds using:
- competition_id;
- season_id;
- player_id;
- sport_event_id.

Relevant feeds include:
- Competition Seasons;
- Season Lineups;
- Season Missing Players;
- Season Schedule;
- Season Summaries;
- Sport Event Lineups;
- Sport Event Summary;
- Sport Event Timeline.

This is useful for retrospective sporting history.

It does not by itself solve historical publication-time reconstruction.

The historical-data guide explicitly notes datasets are enhanced over time and some fields may be unavailable in old years/versions.

Therefore present-day historical responses may include the provider's current corrected/enhanced state.

## Lineups

Documented feeds:
- Sport Event Lineups;
- Season Lineups.

Current response structures expose:
- sport event ID;
- start time;
- competition/season context;
- player IDs;
- starter/played status;
- position;
- jersey number;
- captain where supported;
- lineups confirmed state in relevant feeds/change-log behavior.

Season Lineups TTL is currently documented as 30 seconds for the feed.

### PIT rule

A Season Lineups response queried today with a current `generated_at` cannot prove when the old match lineup first became available.

For retrospective model use:
- lineup may be used only at a historical cutoff if publication timing/version history can be defended.

For prospective use:
- poll/capture before kickoff;
- store raw responses immutably;
- record SPORTS QUANT received_at;
- preserve `lineups.confirmed` transitions where exposed.

## Missing players

Soccer Extended Season Missing Players exposes injured/missing players.

Current documentation:
- reasons include injured, suspended, on_loan, other;
- TTL/cache guidance currently 300 seconds;
- estimated_return_date is available in Extended for some players and may change as new information arrives.

### PIT distinction

Fields such as:
- start_date;
- reason;
- status;
- estimated_return_date

describe the provider's represented absence state.

They do NOT automatically establish:
- first publication timestamp;
- first public knowledge timestamp.

An estimated return date is explicitly mutable.

Therefore:
- capture prospectively;
- version changes;
- never backfill current estimate into an old cutoff.

## Feed corrections and history

Current historical documentation says datasets are continually enhanced.

Current docs reviewed do not establish that every prior version of a corrected historical record remains queryable.

SPORTS QUANT requirement:
unless old versions are demonstrably retrievable:
- use current historical records only for facts whose timing does not depend on revision chronology;
- use prospective raw snapshots for mutable decision-critical context.

## Simulations / replay

Sportradar added Soccer to Simulations in 2026.

Supported replay feeds include:
- Lineups
- Summary
- Timeline
- Season feeds
- Push events/statistics

Potential use:
- adapter/integration testing;
- deterministic replay of supported recordings.

Before using simulations as PIT evidence, verify:
- recording semantics;
- whether timing reproduces actual original publication chronology;
- whether recordings cover intended EPL events;
- contract/storage rights.

Do not equate "replayable" with "historically available to our simulated bettor" without that validation.

## Prospective trial plan

The default trial is useful for a small technical probe.

For selected upcoming Football fixtures:

### Early pre-match
Capture:
- season/competition coverage
- schedule/event state
- missing players

### T-90m through T-15m
Capture:
- lineups feed
- confirmed transition
- missing-player revisions
- event schedule confirmation

### After event
Capture:
- result/summary only for settlement;
- any correction behavior.

Required metadata:
- endpoint/feed
- external IDs
- generated_at
- SPORTS QUANT received_at
- payload hash
- coverage flags
- raw source version
- query parameters excluding key.

## Contractual constraint reminder

The separate licensing audit found material friction in standard reviewed terms:
- trial is evaluation only;
- production scope depends on order form;
- long-term retention/destruction provisions can conflict with reproducibility;
- modeling/betting decision-support permissions should be confirmed explicitly.

Therefore technical success does not equal OD-24 approval.

## Minimum future adapter tests

1. preserve all namespaced external IDs.
2. season ID stability mapping.
3. unconfirmed start time cannot act as final cutoff.
4. schedule changes create versions.
5. generated_at never auto-maps to historical known_at.
6. historical Season Lineups queried today cannot masquerade as original publication-time evidence.
7. lineup confirmed transition captured prospectively.
8. missing-player start/return dates remain semantic fields, not publication time.
9. estimated return date revisions preserved.
10. coverage false != zero.
11. current enhanced historical value cannot overwrite an old captured snapshot.
12. received_at independent from generated_at.
13. raw payload immutable.
14. trial/production license metadata retained in source registry later.
15. replay simulation cannot be treated as PIT evidence without recording-semantics validation.

## Current role assessment

Stable identities:
- DOCUMENTED_FIT

Historical sporting results/lineups:
- DOCUMENTED_AVAILABLE

Historical mutable-context publication chronology:
- NOT_ESTABLISHED

Prospective missing-player/lineup capture:
- DOCUMENTED_CANDIDATE

Simulation for adapter tests:
- DOCUMENTED_CANDIDATE

Production licensing/retention:
- NEEDS_WRITTEN_CONTRACT_CONFIRMATION

## OD-24

OPEN.

Sportradar remains worth technical evaluation, but it is not the default pilot provider until both PIT and contractual retention/model-use questions are resolved.
