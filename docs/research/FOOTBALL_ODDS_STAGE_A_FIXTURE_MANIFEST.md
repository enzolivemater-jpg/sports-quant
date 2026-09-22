# EPL 2024/25 Stage A — Fixture Identity Manifest

Machine-readable file:

`data/manifests/football_odds_stage_a_epl_2024_25_fixtures.json`

Scope:
- Premier League 2024/25
- Matchweeks 1–4
- 40 fixtures
- 20 official team labels
- exact official kickoff groups used by the 69-request historical-odds Stage A plan

Official source:
PremierLeague.com — "All 380 fixtures for 2024/25 Premier League season"
`https://www.premierleague.com/en/news/4040106`

The official page states that weekend and Bank Holiday fixtures without another listed time use 15:00 local, and that fixtures are subject to change.

## Identity policy

This is a source-identity reconciliation manifest, not F4 canonical entity resolution.

Therefore:
- official source labels are preserved;
- `canonical_event_id` is null;
- `provider_event_ids` starts empty;
- no canonical team ID is invented;
- provider event IDs may be attached only after home/away, competition/season and kickoff reconciliation;
- name match alone is insufficient for final canonical entity resolution.

## Validation

```bash
python scripts/research/validate_stage_a_fixtures.py
```

Checks:
- 40 fixtures total;
- 10 fixtures per matchweek;
- each team appears exactly once per matchweek;
- no duplicate fixture identity;
- every fixture maps to an existing Stage A kickoff group;
- fixture kickoff UTC equals the group's kickoff;
- canonical/provider IDs remain unresolved before the actual provider bake-off.

## Purpose

During The Odds API or other provider probes, this manifest gives a fixed denominator of 40 official fixtures.

Missing provider events must remain missing and must not be silently removed from coverage calculations.
