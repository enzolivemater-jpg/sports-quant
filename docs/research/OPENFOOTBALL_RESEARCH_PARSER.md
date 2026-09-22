# OpenFootball Research Parser

Script:
`scripts/research/parse_openfootball_results.py`

Status:
RESEARCH_ONLY — not F4 production ingestion.

## Intended source

Verified source:
- repository: `openfootball/england`
- path: `2024-25/1-premierleague.txt`
- verified blob SHA: `ca0fe4923f0164d0f879f796ab0759253e13bc06`
- expected matches: 380
- expected teams: 20
- license: CC0 1.0

## Why this parser exists

It lets Football model research prepare:
- sequential result history;
- Elo inputs;
- score-model inputs;
- parser/quality checks;

without waiting for a paid broad-data provider.

It does not create:
- canonical entity IDs;
- canonical event IDs;
- canonical known_at;
- historical market observations;
- injuries/lineups/context.

Production ingestion remains F4 after F2/F3 gates.

## Input format behavior

The verified 2024/25 file:
- repeats year explicitly at season start and at 1 January;
- omits the year on most other date lines;
- omits kickoff time on many rows that share the previous kickoff group;
- may omit half-time scores.

The parser therefore:
- carries forward the latest explicit year;
- carries forward kickoff time only within the current date;
- resets inherited kickoff time on a new date;
- preserves missing half-time score as null;
- fails if a match has no defensible current date/time.

## Timezone

The source timestamps do not encode an offset in each row.

The CLI requires an explicit timezone assumption rather than hiding one.

For EPL research use:
`--timezone Europe/London`

The output stores both:
- local date/time;
- the explicit timezone assumption;
- converted UTC event time.

This timezone mapping is research metadata, not historical information-availability evidence.

## Example

After obtaining the source file locally:

```bash
python scripts/research/parse_openfootball_results.py \
  --research-only \
  --input /path/to/1-premierleague.txt \
  --output data/research-probes/openfootball/epl-2024-25-results.json \
  --timezone Europe/London \
  --source-repository openfootball/england \
  --source-path 2024-25/1-premierleague.txt \
  --source-revision ca0fe4923f0164d0f879f796ab0759253e13bc06 \
  --expected-matches 380
```

The output directory is ignored by Git.

## PIT rule

Git publication/update time is not canonical historical `known_at`.

A completed result can act as:
- a label after that match;
- prior sporting history for later matches.

It cannot establish when mutable pre-match context was originally knowable.
