# OpenFootball England — Results Baseline Source v0.1

Date: 2026-09-22

Status: VERIFIED_RESEARCH_BASELINE_CANDIDATE__NO_F4_APPROVAL

Provider/source:
- OpenFootball `openfootball/england`
- upstream Football.TXT data
- license: CC0 1.0 / public domain

## Purpose

Provide a zero-cost, permissively licensed source for historical Football fixture/result data used in:
- sequential Elo research;
- Poisson/Dixon-Coles baseline research;
- parser tests;
- result-label cross-checks;
- entity-name normalization research.

This source does **not** solve historical market odds, historical lineups, injuries, mutable context, or point-in-time bookmaker state.

## Direct repository verification

Repository inspected:
`openfootball/england`

EPL 2024/25 source file:
`2024-25/1-premierleague.txt`

Observed source blob SHA:
`ca0fe4923f0164d0f879f796ab0759253e13bc06`

Observed metadata in the file:
- competition: English Premier League 2024/25;
- date range: 2024-08-16 through 2025-05-25;
- teams: 20;
- matches: 380.

Direct line-pattern probe found 380 completed score records.

Observed fixture/result structure includes:
- matchday;
- date;
- kickoff time where present;
- home club;
- away club;
- full-time score;
- half-time score on many records.

## Historical depth

Current repository tree contains Premier League season files from at least:
- 2000/01 onward in the main season tree;
- older 1990s seasons under archive paths;
- current/recent seasons including 2024/25, 2025/26 and 2026/27.

Exact completeness must be verified per season before using a multi-season research dataset.

## License

The repository LICENSE is CC0 1.0 Universal.

The project README describes the schema, data and scripts as public domain and available for unrestricted reuse.

SPORTS QUANT research assessment:
- local storage: DOCUMENTED_GO;
- automated parsing: DOCUMENTED_GO;
- statistical-model research: DOCUMENTED_GO;
- commercial reuse under CC0 copyright/database-right waiver: DOCUMENTED_GO, subject to the CC0 limitations/disclaimers;
- accuracy warranty: NONE.

## PIT interpretation

Important distinction:

A completed historical result is usable as a label after the event and as prior-match sporting history for later fixtures.

However, the current Git repository state does not automatically prove:
- when a historical fixture time was originally published;
- when later schedule changes became known;
- when any correction was first available.

Therefore:

### Safe initial research use
For match i:
1. order completed historical matches by event date/time using a documented parsing policy;
2. compute pre-match Elo/rolling/result features only from completed matches strictly earlier than i;
3. freeze the feature row;
4. use match i result only afterward as the label/update.

### Not established by this source alone
- historical decision-time odds;
- historical first-publication timestamp;
- old schedule-revision chronology;
- injury/lineup/context known_at.

Do not map Git commit/update time to canonical historical `known_at`.

## Role in the two-lane Football strategy

### Retrospective sporting-history lane
Potential role:
- zero-cost result/fixture spine for baseline model R&D.

### Historical market lane
Role:
- NONE.

Use a dedicated historical odds source such as the current The Odds API candidate after bake-off.

### Prospective context lane
Role:
- NONE.

## Cross-source value

OpenFootball can be used to compare:
- team naming;
- fixture identity;
- result consistency;

against later provider samples.

Disagreement must be surfaced, not silently overwritten.

## Why it is useful now

It removes a dependency on paid broad-data providers for the earliest results-only model research.

It does **not** authorize F5 before F2/F3/F4 gates.

Research may prepare parsers/quality evidence, but production canonical ingestion remains F4.

## Football-Data.co.uk comparison

Football-Data.co.uk has richer betting-odds/statistical CSV history, including documented opening/closing odds in recent seasons.

However, its current public usage notice states the free data is intended for private individuals and excludes certain commercial/data-training/bot/scraper/AI uses.

SPORTS QUANT therefore does not adopt Football-Data.co.uk as an automated model-training source without clearer rights.

OpenFootball is preferred for the zero-cost results-only baseline because its CC0 status is explicit.

## OD-24 impact

OD-24 remains OPEN.

OpenFootball is a free research/result-baseline source and does not resolve the paid sports/odds provider decision.

## Current role state

- EPL 2024/25 result coverage: VERIFIED_PASS
- public-domain/CC0 licensing: VERIFIED_PASS
- results-only baseline research: VERIFIED_PASS
- historical odds: NOT_APPLICABLE
- mutable context PIT: NOT_APPLICABLE
- production provider role: NOT_DECIDED
