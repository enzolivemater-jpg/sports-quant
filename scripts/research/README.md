# Provider Research Probe Harness

Status: RESEARCH_ONLY

Script:
`scripts/research/capture_provider_json.py`

Purpose:
capture authenticated trial/free provider responses for the Football bake-off without building F4 early.

## What it records

- provider name;
- probe name;
- request time;
- SPORTS QUANT receipt time;
- redacted request URL;
- HTTP status;
- selected non-secret response metadata;
- raw response payload;
- SHA-256 payload hash;
- rate-limit headers where exposed.

Outputs are written under:

`data/research-probes/<provider>/<probe>/`

The `data/*` repository ignore rule keeps those payloads out of Git.

## What it deliberately does NOT do

It does not:
- assign `known_at`;
- map provider IDs to canonical IDs;
- normalize market records;
- compute features;
- compute probabilities;
- call F3/F4 code;
- approve a provider;
- resolve OD-24.

`received_at` is retrieval evidence only.

## Secret handling

Preferred mechanisms:

- header secret: `--header-env 'Header-Name=ENV_VAR_NAME'`
- query secret: `--query-env 'parameter_name=ENV_VAR_NAME'`

The secret value comes from the environment and is never intentionally written to metadata.

The harness rejects:
- plain HTTP;
- username/password credentials embedded in the URL;
- known sensitive query parameters supplied directly in `--url`.

This avoids putting provider key values directly into command-line URLs and reduces shell-history/process-list exposure.

Never paste provider keys into:
- GitHub issues;
- committed docs;
- screenshots;
- command-line URLs.

## Example shape

```bash
export PROVIDER_API_KEY='...'

python scripts/research/capture_provider_json.py \
  --research-only \
  --provider example-provider \
  --probe-name fixtures-schema \
  --url 'https://provider.example/v1/fixtures?league=39' \
  --query-env 'api_key=PROVIDER_API_KEY'
```

The example uses a placeholder provider intentionally. Use exact authenticated endpoint syntax from the provider's official documentation during the actual bake-off.

## Evidence discipline

For each probe:
- keep the raw capture local;
- summarize only non-secret observations into the corresponding research audit;
- preserve missingness and errors;
- do not cherry-pick only successful responses;
- do not infer historical publication time from current API state.

## Governance

Using this harness is allowed before F2 because it is provider research tooling only.

Production ingestion remains F4 and must use the approved F2/F3 contracts and PIT kernel.
