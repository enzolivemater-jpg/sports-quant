# StatsBomb Open Data — EPL 2015/16 Sandbox Probe

Date: 2026-09-22

Status: VERIFIED_RESEARCH_PROBE

Source repository:
`hudl/open-data`

Source files inspected:
- `data/competitions.json`
- `data/matches/2/27.json`
- `data/lineups/3754217.json`
- `data/events/3754217.json`

## Competition/season

Competition:
- England — Premier League
- competition_id: 2

Season:
- 2015/2016
- season_id: 27

The current StatsBomb Open Data competition list exposes EPL 2015/16 and 2003/04. EPL 2024/25 is not present in the inspected open competition manifest.

## Match-file probe

`data/matches/2/27.json`

Observed:
- 380 match records
- 20 unique team IDs
- earliest match date: 2015-08-08
- latest match date: 2016-05-17
- all 380 inspected records contain manager data
- all 380 inspected records contain referee data
- all 380 inspected records contain stadium data
- observed metadata data_version: 1.1.0

Observed top-level match fields include:
- match_id
- match_date
- kick_off
- competition
- season
- home_team
- away_team
- home_score
- away_score
- match_status
- match_status_360
- last_updated
- last_updated_360
- metadata
- match_week
- competition_stage
- stadium
- referee

## Event/lineup probe

Sample:
- match_id: 3754217
- Chelsea vs Arsenal
- match date: 2015-09-19
- final score: 2-0

Observed:
- 3,732 event records
- 18 lineup players for Chelsea
- 18 lineup players for Arsenal

Largest event-type counts in sample:
- Pass: 1,046
- Ball Receipt*: 963
- Carry: 814
- Pressure: 320
- Ball Recovery: 106
- Duel: 78
- Dribble: 52
- Clearance: 42
- Block: 41
- Goal Keeper: 34
- Shot: 33
- Dribbled Past: 33
- Foul Committed: 32
- Foul Won: 29
- Miscontrol: 27

Observed event fields include:
- id
- index
- period
- timestamp
- minute
- second
- type
- possession
- possession_team
- play_pattern
- team
- player
- position
- location
- duration
- related_events
- pass
- carry
- pressure
- shot
- goalkeeper
- duel
- dribble
- clearance
- foul fields
- substitution
- tactics
- and other event-specific nested structures

## Critical PIT finding

The open match file contains `last_updated` values that are years after the original 2015/16 fixtures.

Example inspected match:
- event date: 2015-09-19
- dataset `last_updated`: 2025-12-16T17:01:18.696515

Therefore:

`last_updated` in the currently published open dataset must **not** be treated as evidence that the match metadata, manager, referee, lineup or any other field was known at that timestamp before the historical event.

It is a dataset revision/update timestamp, not a historical publication-time reconstruction.

For SPORTS QUANT:
- match outcomes can be used as labels after completion;
- prior completed-match event data can be used in later fixtures if the modeling design only needs the event itself to have occurred before the later cutoff and the dataset is treated as retrospective sporting history;
- any claim that a mutable contextual field was known before a historical cutoff still requires independent PIT evidence;
- the sandbox is excellent for parser and feature-engineering R&D but does not solve historical context known_at.

## Implementation implication

The future StatsBomb Open adapter should preserve:
- source match_id
- source team/player IDs
- metadata data_version
- source last_updated
- raw snapshot reference/hash

But it must not map `last_updated` directly to canonical historical `known_at`.

## Result

Sandbox suitability:
- parser R&D: PASS
- event feature R&D: PASS
- lineup schema R&D: PASS
- EPL 2024/25 bake-off sample: NOT_AVAILABLE_IN_CURRENT_OPEN_MANIFEST
- standalone historical-context PIT source: FAIL / NOT_SUPPORTED_BY_THIS_PROBE
