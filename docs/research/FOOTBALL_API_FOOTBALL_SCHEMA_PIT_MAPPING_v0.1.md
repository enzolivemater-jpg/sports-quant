# Football API-Football Schema / PIT Mapping v0.1

Date: 2026-09-22

Status: RESEARCH_MAPPING__NO_F4_CODE

Provider:
API-Football / API-Sports

Provisional role:
- low-cost prospective Football context capture;
- fixture/entity/schema probe;
- NOT primary historical odds archive.

## Purpose

Map the provider's documented fixture, lineup, injury and odds behavior into the future SPORTS QUANT data layer without treating current API state as historical point-in-time evidence.

## Competition coverage gate

Current API guidance exposes coverage flags by league/season for categories including:
- events;
- lineups;
- fixture statistics;
- player statistics;
- standings;
- players;
- injuries;
- predictions;
- odds.

SPORTS QUANT rule:
before requesting a decision-critical category for a competition/season:
1. inspect its coverage flag;
2. store the observed capability;
3. distinguish unsupported data from temporarily missing data.

A true coverage flag means the provider aims to collect that data. It is not a guarantee that every fixture is complete.

Therefore:
- unsupported != zero;
- supported != guaranteed present.

## Fixture spine

The official guide describes `fixture.id` as the central/master key.

A full-season request can return all league fixtures:

`/fixtures?league=<league>&season=<season>`

Documented fixture context includes:
- fixture ID;
- date/time;
- venue;
- status;
- teams;
- scores/results depending on event state.

Research mapping:

| API-Football field/concept | SPORTS QUANT target | Rule |
|---|---|---|
| fixture.id | provider_event_id | Preserve verbatim. |
| fixture.date/time | event_time_candidate | Request/normalize UTC where possible. |
| fixture.status | provider event state | Do not expose future final status to pre-match materialization. |
| team IDs | provider team IDs | Resolve to canonical teams. |
| league/season IDs | provider competition/season IDs | Resolve explicitly. |

## Timezone policy

The API supports a timezone parameter for fixtures and injuries.

SPORTS QUANT research/prod preference:
- request canonical UTC for ingestion when supported;
- convert only at presentation boundaries;
- preserve the provider field as received in raw payload.

Do not mix provider-local and UTC timestamps without explicit timezone metadata.

## Lineups

Endpoint:
`/fixtures/lineups?fixture=<fixture_id>`

Documented data includes:
- both teams;
- formation;
- starting XI;
- bench;
- coach;
- grid position / player placement.

Current official guide contains two timing descriptions:
- lineups "typically become available 20 to 40 minutes before kickoff" in the endpoint explanation;
- a later polling recommendation describes lineups as "typically available 30–60 minutes before kickoff".

SPORTS QUANT conclusion:
DO NOT hardcode a lineup publication offset.

Instead measure actual first-observed availability prospectively.

### Prospective lineup capture

For selected Football fixtures poll/check at:
- T-90m
- T-75m
- T-60m
- T-45m
- T-30m
- T-15m

Stop repeated lineup polling after the first confirmed complete lineup if provider documentation/observed behavior confirms the lineup record no longer changes.

Store:
- fixture ID;
- teams;
- lineup payload;
- provider fields;
- SPORTS QUANT received_at;
- raw payload hash;
- ingestion version.

Canonical known_at is assigned only under approved F3/F4 rules.

### Historical lineup rule

A final lineup retrievable today is not evidence it was available at T-90m/T-60m historically.

Do not use historical final lineup at a simulated cutoff unless publication availability is defensible.

## Injuries

Endpoint:
`/injuries`

Filter options documented include:
- league + season;
- fixture;
- team;
- player;
- date;
- timezone.

Documented data includes:
- player;
- team;
- fixture context;
- type = Injury or Suspension;
- reason.

Current official update cadence:
- approximately every 4 hours.

### PIT rule

An injury record retrieved today does not prove:
- when the condition was first reported;
- when API-Football first exposed it;
- when a bettor could have known it.

For prospective use:
capture repeated immutable snapshots with SPORTS QUANT `received_at`.

For historical model features:
exclude injury state unless historical availability at the simulated cutoff is defensible.

## Sidelined history

The provider also exposes long-term `/sidelined` history with:
- type;
- start date;
- end date.

As with Sportmonks:
- start/end dates are semantic absence dates;
- they are not publication timestamps.

Never map sidelined start_date directly to `known_at`.

## Pre-match odds

Endpoint:
`/odds`

Current official behavior:
- pre-match odds generally available 1–14 days before a fixture;
- update cadence around every 3 hours;
- only the last 7 days of odds history are retained;
- endpoint pagination is 10 results/page.

Critical implication:
API-Football cannot be the project's long-term historical odds backbone if data is not captured prospectively.

Potential prospective role:
- extra bookmaker/market observations;
- cross-provider consensus challenger;
- short-window line-movement capture.

## Live odds

Endpoint:
`/odds/live`

Current official guide:
- in-play;
- no historical retention.

SPORTS QUANT V1 Football pilot is pre-match-first.

Do not expand into live betting merely because the endpoint exists.

## Provider predictions

Endpoint:
`/predictions?fixture=<fixture_id>`

The provider exposes its own forecast outputs including:
- winner;
- home/draw/away percentages;
- goals/under-over information;
- comparison metrics.

SPORTS QUANT rule:
this is a third-party model output.

It must never:
- become P_safe;
- silently override our model;
- be treated as ground truth.

Potential later research use:
- external challenger/model-agreement input;
- only after PIT timing, calibration quality and leakage risk are assessed.

OD-08/model-agreement rules remain open.

## Update cadences documented in current guide

- fixtures/live events: approximately 15 seconds in live workflows;
- standings: approximately hourly;
- injuries: approximately every 4 hours;
- coach: daily;
- team statistics: roughly twice daily;
- predictions: approximately hourly;
- pre-match odds: approximately every 3 hours;
- lineup availability: shortly before kickoff, provider guide gives overlapping 20–40 and 30–60 minute guidance.

These are provider operational guidance, not SPORTS QUANT freshness thresholds.

Do not turn them into canonical freshness policy without validation.

## Prospective Football snapshot plan

For an upcoming EPL fixture:

### T-24h
Capture:
- fixture;
- coverage capability;
- injuries;
- odds;
- predictions only if research track enabled.

### T-6h
Capture:
- fixture changes;
- injuries;
- odds.

### T-90m
Capture:
- fixture;
- injuries;
- odds;
- first lineup check.

### T-75m / T-60m / T-45m / T-30m / T-15m
Capture/check:
- lineup availability;
- fixture status;
- injury revision;
- odds when provider cadence warrants it.

### Post-match
Capture only for:
- settlement;
- revision/correction study;
- labels.

Never feed post-match records backward into pre-match snapshots.

## Quota-fit hypothesis

Current free plan:
- 100 requests/day;
- all endpoint families;
- season restrictions apply.

For a small prospective EPL probe, 100/day is enough if requests are:
- grouped by league/date where possible;
- coverage checked once;
- lineups polled only around selected fixtures;
- repeated redundant calls avoided.

Do not choose API-Football as production provider solely because the free plan is convenient.

## Missing-data semantics

Explicitly distinguish:
- coverage flag false;
- endpoint returned zero records;
- fixture not yet published for category;
- temporary provider failure;
- pagination incomplete;
- data genuinely absent;
- true numerical zero.

The pagination object must always be checked before declaring a dataset complete.

## Raw capture metadata

Every prospective request should retain:
- provider;
- endpoint;
- parameters excluding secret;
- page number;
- provider IDs;
- response result count;
- paging metadata;
- SPORTS QUANT received_at;
- raw payload/hash;
- ingestion version;
- HTTP/error information;
- applicable coverage flags.

Never log API keys.

## Minimum future adapter tests

1. fixture ID preservation.
2. UTC/timezone-safe event time.
3. coverage false is not mapped to zero.
4. paging beyond page 1 is not silently ignored.
5. lineup first-observed time captured via SPORTS QUANT receipt.
6. no hardcoded 30/60-minute lineup publication assumption.
7. final lineup cannot leak to earlier cutoff.
8. injury current state cannot masquerade as historical publication state.
9. sidelined start_date != known_at.
10. odds older than provider retention window are explicitly unavailable.
11. live odds not assumed replayable.
12. provider predictions remain third-party model outputs.
13. missing != zero.
14. raw payload immutable/versioned.
15. secret absent from logs/artifacts.
16. provider updates create a new captured version instead of destructive overwrite.

## Current role assessment

Fixture/schedule probe:
- DOCUMENTED_FIT

Entity IDs:
- DOCUMENTED_FIT

Prospective injuries:
- DOCUMENTED_FIT

Prospective lineups:
- DOCUMENTED_FIT

Historical lineup publication chronology:
- NOT_ESTABLISHED

Historical injury publication chronology:
- NOT_ESTABLISHED

Long historical odds:
- FAIL_AS_PRIMARY_ROLE

Low-cost prospective capture:
- STRONG_CANDIDATE

Third-party predictions:
- RESEARCH_ONLY_CHALLENGER

## OD-24

OPEN.

Authenticated EPL coverage and prospective observation are still required before a provider role is approved.
