# Football Historical Odds Bake-off — Stage A Sample v0.1

Date: 2026-09-22

Status: RESEARCH_SAMPLE__NO_PURCHASE_AUTHORIZED

Competition:
English Premier League

Season:
2024/25

Purpose:
Test The Odds API historical featured-market coverage, timestamp semantics, entity matching and PIT behavior at minimal quota cost before any full-season extraction.

## Sample

Use Matchweeks 1–4 from the official Premier League 2024/25 fixture list.

Total fixtures:
- 40

Official source:
- PremierLeague.com — "All 380 fixtures for 2024/25 Premier League season"

The official page states:
- the season contains 380 fixtures;
- weekend/Bank Holiday fixtures without another listed time use 15:00 local;
- midweek fixtures without another listed time use 19:45 local;
- fixtures are subject to change.

For Stage A, use the final fixture event timestamps observed in the historical odds provider response as the provider-side event-time reference and reconcile them to the official fixture identities.

## Distinct kickoff groups in MW1–MW4

From the official fixture schedule:

### Matchweek 1
Distinct kickoff timestamps:
1. Fri 16 Aug 2024 20:00
2. Sat 17 Aug 2024 12:30
3. Sat 17 Aug 2024 15:00
4. Sat 17 Aug 2024 17:30
5. Sun 18 Aug 2024 14:00
6. Sun 18 Aug 2024 16:30
7. Mon 19 Aug 2024 20:00

Count: 7

### Matchweek 2
Distinct kickoff timestamps:
1. Sat 24 Aug 2024 12:30
2. Sat 24 Aug 2024 15:00
3. Sat 24 Aug 2024 17:30
4. Sun 25 Aug 2024 14:00
5. Sun 25 Aug 2024 16:30

Count: 5

### Matchweek 3
Distinct kickoff timestamps:
1. Sat 31 Aug 2024 12:30
2. Sat 31 Aug 2024 15:00
3. Sat 31 Aug 2024 17:30
4. Sun 1 Sep 2024 13:30
5. Sun 1 Sep 2024 16:00

Count: 5

### Matchweek 4
Distinct kickoff timestamps:
1. Sat 14 Sep 2024 12:30
2. Sat 14 Sep 2024 15:00
3. Sat 14 Sep 2024 17:30
4. Sat 14 Sep 2024 20:00
5. Sun 15 Sep 2024 14:00
6. Sun 15 Sep 2024 16:30

Count: 6

Total distinct kickoff timestamps:
- 23

## Stage A decision cutoffs

For each distinct kickoff timestamp request historical snapshots at:

- T-24h
- T-1h
- T-15m

Markets:
- h2h
- totals

Region:
- one region initially

Requested odds format:
- decimal

## Quota estimate

Current documented historical featured-market cost:

`10 credits × markets × regions`

For two markets and one region:

`10 × 2 × 1 = 20 credits / snapshot request`

Without considering any cross-cutoff timestamp collisions:

`23 kickoff groups × 3 cutoffs = 69 historical requests`

Maximum planned Stage A cost:

`69 × 20 = 1,380 credits`

This is substantially below the current 20,000-credit entry historical plan.

Additional requests must be budgeted for:
- schema probes;
- retries;
- alternate region comparison if needed;
- event reconciliation failures.

A research safety budget of 2,000–3,000 credits is therefore more than sufficient for the planned Stage A test under the current documented quota model, assuming no provider pricing/quota change before execution.

## Why group by kickoff timestamp

The historical featured-market endpoint returns all covered games in the sport at the requested snapshot time.

Therefore one request can cover several fixtures whose decision cutoff is identical.

SPORTS QUANT must not issue one request per fixture when a single historical snapshot can cover the group.

## Stage A evidence to collect

For every requested snapshot:

- requested date/time;
- provider returned `timestamp`;
- `previous_timestamp`;
- `next_timestamp`;
- event IDs;
- event commence times;
- bookmakers;
- bookmaker update time where present;
- market-level update time where present;
- h2h completeness;
- totals line(s);
- decimal prices;
- raw payload hash;
- SPORTS QUANT retrieval `received_at`.

## Coverage success checks

For the 40 fixtures measure:

- event match rate;
- h2h availability rate at each cutoff;
- totals availability rate at each cutoff;
- bookmaker count distribution;
- bookmaker continuity across T-24h/T-1h/T-15m;
- missing fixture/market frequency;
- returned snapshot lag versus requested cutoff;
- market update age;
- duplicate/event-ID consistency;
- corrected response behavior if repeated later.

Do not silently drop uncovered fixtures from the denominator.

## PIT checks

1. returned provider snapshot must be <= requested historical date as documented;
2. wrapper snapshot time remains separate from market update time;
3. `next_timestamp` is navigation-only and excluded from decision-ready data;
4. historical corrections must not destructively overwrite prior raw retrievals;
5. no provider timestamp becomes canonical `known_at` until F3/F4 mapping is validated.

## Stage A exit criteria

Proceed to a larger EPL extraction only if:

- event reconciliation is reliable;
- Phase-1 markets have adequate coverage;
- timestamp semantics behave as documented;
- raw payload retention/replay is reproducible;
- no critical PIT ambiguity is discovered;
- quota economics remain acceptable.

Otherwise:
- stop;
- record failure mode;
- compare the next provider/role candidate.

## Governance

This sample is an engineering/provider bake-off.

It:
- does not select EPL as the most profitable league;
- does not resolve OD-04 sample-size requirements;
- does not resolve OD-07 no-vig Champion;
- does not close OD-24 provider selection;
- does not authorize a purchase by itself.
