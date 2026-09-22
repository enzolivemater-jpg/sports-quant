# Free/Trial Football Provider Probe Runner

Status: RESEARCH_ONLY

Manifest:
`data/manifests/football_provider_probe_plan_v0.1.json`

Runner:
`scripts/research/run_provider_probes.py`

This runner covers only the current free/trial probes for:
- API-Football
- Sportmonks
- Sportradar

The Odds API historical Stage A remains separated because it can consume paid historical quota and has its own guarded runner.

## Default behavior

Dry-run one probe:

```bash
python scripts/research/run_provider_probes.py
```

Dry-run all API-Football probes:

```bash
python scripts/research/run_provider_probes.py \
  --provider api-football \
  --all-selected
```

No request is sent unless `--execute` is supplied.

## Execute

Example:

```bash
export API_FOOTBALL_KEY='...'

python scripts/research/run_provider_probes.py \
  --provider api-football \
  --execute \
  --ack-trial-quota
```

The runner stops at the first failed probe.

## Safety

Execution requires:
- explicit `--execute`;
- explicit `--ack-trial-quota`;
- required provider secret in environment.

The runner delegates raw capture to:
`scripts/research/capture_provider_json.py`

Therefore it inherits:
- HTTPS-only requests;
- environment-based secrets;
- no credentials embedded in URL;
- redacted metadata;
- ignored local raw payload storage;
- no canonical `known_at` assignment.

## Governance

This runner:
- is not F4;
- does not approve providers;
- does not resolve OD-24;
- does not normalize provider payloads into canonical SPORTS QUANT records;
- does not compute probabilities or betting outputs.

It exists solely to make the provider bake-off reproducible and harder to execute incorrectly.
