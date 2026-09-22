# The Odds API Stage A — Research Reconciliation

Script:
`scripts/research/reconcile_odds_stage_a.py`

Purpose:
compare a captured The Odds API historical response against the fixed EPL MW1–MW4 fixture denominator.

## Safety rule

The reconciler never:
- fuzzy-matches team names;
- writes provider IDs into the canonical manifest;
- creates `canonical_event_id`;
- assigns `known_at`;
- treats kickoff alone as sufficient entity proof.

## Without an alias map

The tool groups provider events and official fixtures by exact UTC kickoff.

This is useful for:
- missing-event detection;
- event-count comparison;
- simultaneous-kickoff grouping;
- provider events outside the Stage A sample.

Every fixture remains `UNRESOLVED`.

## With an explicit provider label alias map

A JSON alias map may map:

`provider team label -> source_identity_team_key`

Example shape:

```json
{
  "Manchester United": "Man Utd",
  "Fulham": "Fulham"
}
```

Such a map must be built from observed provider responses and documented evidence.

A fixture is research-resolved only when:
- kickoff UTC matches;
- mapped provider home team equals the official source identity home key;
- mapped provider away team equals the official source identity away key;
- exactly one provider event satisfies that pair.

No Levenshtein, substring or LLM guess is permitted.

## Example

```bash
python scripts/research/reconcile_odds_stage_a.py \
  --research-only \
  --payload data/research-probes/the-odds-api/<probe>/<capture>.json \
  --alias-map data/research-probes/the-odds-api/team_aliases.json \
  --output data/research-probes/the-odds-api/reconciliation/report.json
```

Local research outputs remain ignored by Git.

## Governance

A `RESOLVED_EXACT_ALIAS` result is provider-reconciliation evidence only.

F4 later owns canonical entity resolution and must independently satisfy its contracts/tests.
