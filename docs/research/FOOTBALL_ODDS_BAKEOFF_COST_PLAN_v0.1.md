# Football Historical Odds Bake-off Cost Plan v0.1

Date: 2026-09-22

Status: RESEARCH_PLAN__NO_PURCHASE_AUTHORIZED

Candidate provider:
The Odds API

## Current documented quota model

Historical featured-market request cost:

`credits = 10 × number_of_markets × number_of_regions`

Initial SPORTS QUANT markets:
- h2h / Football 1X2
- totals / main total goals

Initial bake-off region:
- one region only

Therefore:
- two markets × one region = 20 credits per historical snapshot request.

Current public entry historical plan:
- 20,000 credits/month
- USD 30/month

At 20 credits per request, that plan supports up to:
- 1,000 historical snapshot requests

before other quota usage.

## Important optimization

The historical endpoint returns all covered games at a requested snapshot timestamp.

Therefore SPORTS QUANT should NOT issue one request per match when several fixtures share the same decision timestamp.

Extraction should be grouped by unique:
- requested timestamp
- market set
- bookmaker region

This can reduce quota materially.

## Stage A — Cheap semantics/coverage proof

Before buying enough quota for a full season, test a small fixed EPL 2024/25 subset.

Recommended research subset:
- approximately 40 fixtures
- representative dates/months
- three cutoffs:
  - T-24h
  - T-1h
  - T-15m
- markets:
  - h2h
  - totals
- one region

Worst-case if every fixture required a unique request at every cutoff:
- 40 × 3 = 120 snapshot requests
- 120 × 20 = 2,400 credits

In practice grouping shared kickoff times may reduce this further.

Stage A validates:
- EPL event matching
- h2h coverage
- totals coverage
- bookmaker availability
- snapshot timestamp semantics
- nearest-at-or-before behavior
- missing/empty response behavior
- entity stability
- historical correction observations where detectable

## Stage B — Full six-cutoff provider bake-off

Canonical research cutoffs:
- T-24h
- T-6h
- T-1h
- T-30m
- T-15m
- nearest defensible pre-kickoff observation

Naive worst-case for all 380 EPL fixtures:
- 380 × 6 = 2,280 snapshot requests
- 2,280 × 20 = 45,600 credits

This is deliberately a pessimistic upper bound because it ignores timestamp grouping.

Do NOT buy quota based on this upper bound before computing the number of unique requested timestamps.

## Entry-plan capacity

At two markets / one region:
- 20,000 credits / 20 credits = 1,000 snapshot requests.

For six cutoffs, this supports up to roughly 166 unique kickoff/cutoff groups before consuming the full plan allocation.

Whether the entire EPL 2024/25 six-cutoff extraction fits in the USD 30 plan must be computed from the actual kickoff schedule and grouping strategy rather than guessed.

## Extraction algorithm

Before paid extraction:

1. obtain canonical EPL fixture schedule;
2. normalize event_time to UTC;
3. generate requested cutoff timestamps per fixture;
4. deduplicate identical timestamps;
5. group by market/region configuration;
6. estimate exact credit cost;
7. reserve a safety margin for retries/coverage probes;
8. only then choose plan size.

## Region strategy

Start with one bookmaker region for the provider bake-off.

Reason:
- PIT semantics and coverage can be validated without paying for several regions.

Only expand to multiple regions/bookmaker sets if:
- bookmaker continuity is insufficient;
- consensus robustness materially benefits;
- marginal cost is justified.

The production consensus design remains a later market-engine decision.

## Purchase rule

No recurring or larger plan should be purchased merely because it exists.

First paid step should be the smallest historical-enabled plan that can complete the Stage A proof.

Escalate only after:
- schema works;
- coverage is acceptable;
- PIT semantics are confirmed;
- licensing remains acceptable;
- exact full extraction cost is computed.

## OD-24

This plan does not close OD-24.

It reduces the cost of gathering the evidence required to close it.
