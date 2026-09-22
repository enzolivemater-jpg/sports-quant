# Football Provider Bake-off Plan v0.1

Date: 2026-09-22

Status: READY_TO_EXECUTE_WHEN_CREDENTIALS_EXIST

OD-24 remains OPEN.

## Principle

Test providers before committing architecture or recurring spend.

Use free/trial access for schema, coverage and point-in-time semantics first. Pay only where historical market data cannot be evaluated otherwise.

## Stage 0 — Zero/minimal spend

### StatsBomb Open Data
Use the public open-data repository to:
- validate event and lineup parsing concepts;
- inspect competition/season/match/entity structure;
- test feature-research workflows.

Do not treat repository availability time as canonical historical known_at.

### API-Football Free
Current public pricing advertises:
- $0/month;
- 100 requests/day;
- all endpoints, with free-plan season limitations.

Test:
- competition coverage flags;
- fixtures;
- lineups;
- injuries;
- statistics;
- provider timestamps;
- entity ID stability;
- missing-data behavior.

Do not use it as the historical-odds backbone because current official guidance describes only seven days of pre-match odds retention.

### Sportradar Trial
Current developer documentation describes default API trials as:
- 30 days;
- 1,000 requests per rolling 30 days;
- 1 QPS.

Test:
- Soccer v4 competition and season coverage;
- lineups;
- missing players;
- historical season depth for the candidate pilot competition;
- generated/update timestamps;
- correction and revision semantics.

### Sportmonks Trial / Free Access
Current public pricing advertises:
- free access for testing;
- 14-day paid-feature trial;
- Starter from EUR 29/month for five selected leagues;
- broader data and historical-data options depending on plan/add-on.

Test:
- fixture object and IDs;
- lineups/formations;
- sidelined/injury information;
- statistics/xG availability;
- odds objects;
- last-update semantics;
- historical availability by league;
- revision behavior.

## Stage 1 — Historical market evidence

### The Odds API

Current public pricing/documentation:
- free plan does not include historical odds;
- first historical-enabled tier is currently advertised at USD 30/month with 20,000 credits;
- historical featured-market snapshots are documented from 2020-06-06;
- 10-minute intervals historically, 5-minute intervals from September 2022;
- historical endpoint returns the closest snapshot at or before the requested timestamp;
- historical request quota cost is documented as 10 credits per region per market.

This is the first provider where a small paid test is justified because the feature directly addresses SPORTS QUANT's historical market reconstruction requirement.

## Fixed bake-off experiment

Do not compare providers on different samples.

Select one well-covered top domestic Football league and a fixed completed date interval.

The exact competition remains unapproved until the sample-coverage check is complete.

For the same fixtures, test the following cutoffs where data exists:
- T-24h;
- T-6h;
- T-1h;
- T-30m;
- T-15m;
- nearest defensible pre-kickoff observation.

Initial market focus:
- Football 1X2;
- main total goals line.

These are already canonical Phase 1 Football market families.

## Evidence table to collect

For every provider/field:

- provider;
- endpoint;
- competition;
- season;
- event identifier;
- source timestamp;
- generated/update timestamp;
- SPORTS QUANT request timestamp;
- SPORTS QUANT received_at;
- candidate known_at_basis;
- whether historical as-of retrieval exists;
- whether corrected/backfilled values overwrite history;
- whether old revisions are retrievable;
- missingness;
- latency;
- rate-limit behavior;
- response determinism;
- raw-payload storage permission;
- derived-model-use permission;
- redistribution restrictions;
- cost.

## Hard fail conditions for a proposed historical role

A provider cannot be the historical source for a decision-critical field when:
- the value is only exposed as its latest/current state;
- historical revisions cannot be distinguished;
- no defensible availability time can be established;
- later corrections silently overwrite the historical value and no raw snapshot was stored at the time;
- licensing prohibits the required storage or model use.

Such a provider may still be usable prospectively if SPORTS QUANT captures immutable raw snapshots itself.

## Provisional role map to test

| Provider | Historical match/event research | Historical odds | Prospective context | Trial accessibility |
|---|---|---|---|---|
| StatsBomb Open Data | Yes, selective | No | No production assumption | Public/open |
| The Odds API | Results secondary | Strong candidate | Odds | Paid for history |
| Sportradar | Candidate | Separate odds products require audit | Strong candidate | 30-day trial |
| Sportmonks | Candidate | Requires history/granularity audit | Strong candidate | Free/trial |
| API-Football | Candidate with season limits | Weak for long history | Strong low-cost candidate | Free tier |

"Strong/weak candidate" here refers only to documented fit for the proposed provider role, not final data quality.

## Output of bake-off

Produce:
1. coverage matrix;
2. PIT-risk matrix;
3. license/storage matrix;
4. cost matrix;
5. recommended provider role(s);
6. explicit residual risks;
7. evidence for OD-24 resolution.

No provider is approved until that output exists.
