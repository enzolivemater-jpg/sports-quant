# The Odds API Stage A — Snapshot Coverage Analysis

Script:
`scripts/research/analyze_odds_stage_a_snapshot.py`

Purpose:
measure what one captured historical snapshot actually covers without performing production market calculations.

Inputs:
- raw provider payload;
- capture metadata;
- research reconciliation report.

Outputs include:
- requested snapshot timestamp;
- provider-returned snapshot timestamp;
- lag in seconds;
- whether provider snapshot is at/before requested time;
- fixed expected fixture denominator;
- resolved/unresolved fixture count;
- h2h presence;
- complete 1X2 presence;
- totals presence;
- bookmaker-count distribution;
- totals lines observed;
- missing resolved provider IDs.

## Important denominator rule

The expected fixture count remains the official Stage A denominator.

Unresolved or missing fixtures are not silently removed.

## Explicit non-goals

The analyzer does not:
- select the main totals line;
- remove bookmaker margin;
- compute no-vig probabilities;
- calculate edge;
- assign `known_at`;
- approve The Odds API;
- resolve OD-07 or OD-24.

## Example

```bash
python scripts/research/analyze_odds_stage_a_snapshot.py \
  --research-only \
  --payload data/research-probes/the-odds-api/<probe>/<capture>.json \
  --metadata data/research-probes/the-odds-api/<probe>/<capture>.metadata.json \
  --reconciliation data/research-probes/the-odds-api/reconciliation/report.json \
  --output data/research-probes/the-odds-api/coverage/<probe>.json
```

All research outputs remain local/ignored.
