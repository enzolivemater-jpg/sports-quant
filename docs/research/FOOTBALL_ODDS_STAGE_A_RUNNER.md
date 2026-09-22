# The Odds API Stage A Runner

Script:
`scripts/research/run_odds_stage_a.py`

Status:
RESEARCH_ONLY — no paid request is executed by default.

## Dry-run default

```bash
python scripts/research/run_odds_stage_a.py
```

This prints the first planned request and sends nothing.

Inspect a batch without sending:

```bash
python scripts/research/run_odds_stage_a.py --offset 0 --limit 5
```

Inspect all 69:

```bash
python scripts/research/run_odds_stage_a.py --all-stage-a
```

## Execute one historical request

Only after paid historical access exists:

```bash
export THE_ODDS_API_KEY='...'

python scripts/research/run_odds_stage_a.py \
  --execute \
  --ack-paid-provider-access \
  --max-credits 20
```

Because the default limit is 1, this cannot accidentally launch the whole Stage A plan.

## Execute a controlled batch

```bash
python scripts/research/run_odds_stage_a.py \
  --execute \
  --ack-paid-provider-access \
  --max-credits 100 \
  --offset 0 \
  --limit 5
```

## Execute all 69 Stage A snapshots

This requires two explicit confirmations:

```bash
python scripts/research/run_odds_stage_a.py \
  --execute \
  --ack-paid-provider-access \
  --all-stage-a \
  --confirm-request-count 69 \
  --max-credits 1380
```

The API key remains in the environment. The child capture harness injects it through `--query-env`; the key value is not written into the command URL or metadata.

## Failure policy

Execution stops on the first failed probe.

Reason:
- avoid silently burning paid quota after a schema/auth/timestamp failure;
- preserve the failure payload/evidence from the capture harness;
- investigate before continuing.

## Governance

This script:
- does not authorize a subscription/purchase;
- does not resolve OD-24;
- does not assign `known_at`;
- does not ingest production data;
- does not compute probabilities/edges;
- does not start F4.

Re-check provider pricing, quota and historical endpoint semantics immediately before any paid run.


## Mechanical credit cap

The machine manifest carries a research-only historical credit assumption.

At the current manifest value:
- one Stage A snapshot = 20 estimated credits;
- five snapshots = 100 estimated credits;
- all 69 snapshots = 1,380 estimated credits.

Paid execution now requires `--max-credits`.

If the selected batch estimate exceeds that cap, the runner exits before any request is sent.

The manifest assumption is explicitly marked:
`RECHECK_PROVIDER_DOCS_BEFORE_EXECUTION`.

Therefore the cap is a safety mechanism, not a claim that provider quota rules can never change.
