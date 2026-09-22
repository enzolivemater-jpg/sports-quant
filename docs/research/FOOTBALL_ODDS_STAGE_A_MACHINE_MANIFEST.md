# EPL 2024/25 Historical Odds Stage A — Machine Manifest

The committed machine-readable request plan is:

`data/manifests/football_odds_stage_a_epl_2024_25.json`

It contains:
- 23 distinct kickoff groups from EPL Matchweeks 1–4;
- Europe/London local kickoff time;
- UTC kickoff time;
- T-24h;
- T-1h;
- T-15m;
- 69 planned historical snapshot requests;
- `soccer_epl`;
- `h2h` + `totals`;
- one initial bookmaker region (`eu`).

Validation:

```bash
python scripts/research/validate_stage_a_manifest.py
```

The manifest is research-only.

It is not:
- a production decision-cutoff policy;
- proof that provider event times match the official fixture schedule;
- authorization to purchase historical API access;
- OD-24 resolution.

Provider-returned snapshot timestamps and event commence times remain evidence that must be captured and reconciled during the actual bake-off.
