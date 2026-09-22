# Football Provider Probe Commands v0.1

Date: 2026-09-22

Status: READY_FOR_LOCAL_RESEARCH_USE

These commands use the research-only harness:
`scripts/research/capture_provider_json.py`

They are intentionally local/manual research commands. They do not belong to F4 production ingestion.

## Security rule

Never paste a real key into a URL or committed command.

Export secrets only into the local shell environment.

Raw responses are written under ignored `data/research-probes/`.

## API-Football

Official authentication:
- direct API base: `https://v3.football.api-sports.io/`
- request header: `x-apisports-key`

Local secret:

```bash
export API_FOOTBALL_KEY='...'
```

### Authentication/schema probe

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider api-football \
  --probe-name countries-auth-schema \
  --url 'https://v3.football.api-sports.io/countries' \
  --header-env 'x-apisports-key=API_FOOTBALL_KEY'
```

### EPL competition/season discovery

Do not initially hardcode an EPL provider ID from memory.

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider api-football \
  --probe-name england-leagues-2024 \
  --url 'https://v3.football.api-sports.io/leagues?country=England&season=2024' \
  --header-env 'x-apisports-key=API_FOOTBALL_KEY'
```

Resolve the Premier League provider ID from the captured response and record it in the probe evidence record.

Then continue the matrix in:
`FOOTBALL_PROVIDER_PROBE_EXECUTION_MATRIX_v0.1.md`.

Official auth reference:
https://www.api-football.com/news/post/how-to-get-started-with-api-football-the-complete-beginners-guide

## Sportmonks

Official authentication supports:
- query parameter `api_token`; or
- `Authorization` request header.

SPORTS QUANT research preference:
use the header so the token never becomes part of the request URL.

Local secret:

```bash
export SPORTMONKS_API_TOKEN='...'
```

### Authentication/schema probe

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider sportmonks \
  --probe-name fixtures-auth-schema \
  --url 'https://api.sportmonks.com/v3/football/fixtures' \
  --header-env 'Authorization=SPORTMONKS_API_TOKEN'
```

Before EPL-specific probes:
- query/inspect leagues through the provider API/docs;
- resolve the exact EPL provider league/season IDs from authenticated data;
- do not infer IDs from another vendor.

Official auth reference:
https://docs.sportmonks.com/v3/welcome/authentication

## Sportradar Soccer v4

Official authentication:
- `x-api-key` request header.

Local secret:

```bash
export SPORTRADAR_API_KEY='...'
```

### Competition/schema probe

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider sportradar \
  --probe-name soccer-v4-competitions \
  --url 'https://api.sportradar.com/soccer/trial/v4/en/competitions.json' \
  --header-env 'x-api-key=SPORTRADAR_API_KEY'
```

Then resolve:
- Premier League competition ID;
- season ID;
- coverage metadata;

from authenticated provider responses before deeper lineup/missing-player probes.

Official auth reference:
https://developer.sportradar.com/getting-started/docs/authentication

## The Odds API

Official historical endpoint:
`/v4/historical/sports/{sport}/odds`

EPL sport key:
`soccer_epl`

Historical access is paid.

Authentication is a query parameter named `apiKey`.

SPORTS QUANT MUST inject it with `--query-env`; never place the value inside `--url`.

Local secret:

```bash
export THE_ODDS_API_KEY='...'
```

### Historical Stage A command shape

Replace:
- `<REGION>` with the explicitly selected single Stage A region;
- `<ISO8601_CUTOFF>` with one planned historical cutoff.

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider the-odds-api \
  --probe-name epl-stage-a-historical \
  --url 'https://api.the-odds-api.com/v4/historical/sports/soccer_epl/odds?regions=<REGION>&markets=h2h,totals&oddsFormat=decimal&date=<ISO8601_CUTOFF>' \
  --query-env 'apiKey=THE_ODDS_API_KEY'
```

Do not execute the full Stage A loop until:
- historical-enabled access is active;
- pricing/quota is rechecked;
- Stage A spend is explicitly authorized.

Official references:
- https://the-odds-api.com/liveapi/guides/v4/
- https://the-odds-api.com/sports-odds-data/epl-odds.html

## Evidence recording

After each probe:
1. retain local raw capture;
2. copy the template:
   `docs/research/PROVIDER_PROBE_EVIDENCE_RECORD_TEMPLATE.md`;
3. fill only verified observations;
4. mark unknowns as UNKNOWN;
5. never assign canonical historical `known_at` from a probe script;
6. update issue #3 with non-secret findings only.

## Stop conditions

Stop a provider-role probe when:
- auth/plan does not expose the required EPL sample;
- timestamps cannot support the proposed role;
- historical versions required for the role are unavailable;
- licensing/storage constraints conflict with the role;
- quota economics are materially worse than planned;
- provider IDs/market records cannot be reconciled reliably.

A failed role test is useful evidence. Do not keep spending quota to force a provider to pass.
