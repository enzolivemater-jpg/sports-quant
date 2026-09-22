# Football Provider Probe Commands v0.1

Date: 2026-09-22

Status: READY_FOR_CREDENTIALLED_RESEARCH

Purpose:
provide reproducible, low-risk commands for provider trials using the research-only capture harness.

These commands do not approve any provider and do not resolve OD-24.

## Global safety

Before every probe:

- use `scripts/research/capture_provider_json.py`;
- export the provider secret into an environment variable;
- never place the secret value directly in `--url`;
- use `--header-env` or `--query-env`;
- keep raw captures under ignored `data/research-probes/`;
- do not assign canonical `known_at`;
- record the result in `docs/research/PROVIDER_PROBE_EVIDENCE_RECORD_TEMPLATE.md`.

## API-Football

Official base URL:
`https://v3.football.api-sports.io/`

Official authentication:
request header `x-apisports-key`.

Environment:

```bash
export API_FOOTBALL_KEY='...'
```

### P1.1 — basic authenticated connectivity

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider api-football \
  --probe-name countries-connectivity \
  --url 'https://v3.football.api-sports.io/countries' \
  --header-env 'x-apisports-key=API_FOOTBALL_KEY'
```

### P1.2 — EPL league/season coverage

API-Football documentation currently uses league id `39` for the English Premier League.

For EPL 2024/25, season is represented by starting year `2024`.

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider api-football \
  --probe-name epl-2024-league-coverage \
  --url 'https://v3.football.api-sports.io/leagues?id=39&season=2024' \
  --header-env 'x-apisports-key=API_FOOTBALL_KEY'
```

Inspect:
- league/season IDs;
- coverage flags;
- injuries;
- lineups;
- statistics;
- odds availability flags.

### P1.3 — EPL 2024/25 fixture spine

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider api-football \
  --probe-name epl-2024-fixtures \
  --url 'https://v3.football.api-sports.io/fixtures?league=39&season=2024' \
  --header-env 'x-apisports-key=API_FOOTBALL_KEY'
```

Validate:
- expected fixture count;
- fixture IDs;
- team IDs;
- ISO fixture date;
- Unix timestamp;
- timezone;
- paging;
- postponed/cancelled state behavior.

Do not treat current final results/status as pre-match information.

### P1.4 — selected fixture lineups

After obtaining a real `fixture_id` from P1.3:

```bash
export API_FOOTBALL_FIXTURE_ID='<fixture_id>'

python scripts/research/capture_provider_json.py \
  --research-only \
  --provider api-football \
  --probe-name selected-fixture-lineup \
  --url "https://v3.football.api-sports.io/fixtures/lineups?fixture=${API_FOOTBALL_FIXTURE_ID}" \
  --header-env 'x-apisports-key=API_FOOTBALL_KEY'
```

For prospective matches repeat captures around the documented probe windows in the existing PIT mapping.

A historical final lineup retrieved today is not historical publication-time evidence.

### P1.5 — selected fixture injuries

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider api-football \
  --probe-name selected-fixture-injuries \
  --url "https://v3.football.api-sports.io/injuries?fixture=${API_FOOTBALL_FIXTURE_ID}" \
  --header-env 'x-apisports-key=API_FOOTBALL_KEY'
```

Do not map injury dates to historical `known_at`.

---

## Sportmonks Football API v3

Official Football base:
`https://api.sportmonks.com/v3/football`

Official authentication supports query parameter `api_token`.
Use query environment injection so the token is not typed into the URL.

Environment:

```bash
export SPORTMONKS_TOKEN='...'
```

### P2.1 — fixtures connectivity/schema

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider sportmonks \
  --probe-name fixtures-connectivity \
  --url 'https://api.sportmonks.com/v3/football/fixtures' \
  --query-env 'api_token=SPORTMONKS_TOKEN'
```

Inspect:
- fixture ID;
- league/season/team IDs;
- `starting_at`;
- `starting_at_timestamp`;
- `last_processed_at`;
- `has_odds`;
- paging/links.

### P2.2 — fixture by ID

After selecting a fixture ID from P2.1:

```bash
export SPORTMONKS_FIXTURE_ID='<fixture_id>'

python scripts/research/capture_provider_json.py \
  --research-only \
  --provider sportmonks \
  --probe-name selected-fixture \
  --url "https://api.sportmonks.com/v3/football/fixtures/${SPORTMONKS_FIXTURE_ID}" \
  --query-env 'api_token=SPORTMONKS_TOKEN'
```

Then repeat with documented includes only when needed for the specific evidence question.

Do not request every include by default.

### P2.3 — latest-updated fixture behavior

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider sportmonks \
  --probe-name latest-updated-fixtures \
  --url 'https://api.sportmonks.com/v3/football/fixtures/latest' \
  --query-env 'api_token=SPORTMONKS_TOKEN'
```

Use only to study update/change behavior.
Do not equate a current update signal with historical publication time.

---

## Sportradar Soccer v4

Official trial URL pattern:
`https://api.sportradar.com/soccer/trial/v4/en/...json`

Official authentication:
request header `x-api-key`.

Environment:

```bash
export SPORTRADAR_API_KEY='...'
```

### P3.1 — competition list / connectivity

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider sportradar \
  --probe-name soccer-competitions \
  --url 'https://api.sportradar.com/soccer/trial/v4/en/competitions.json' \
  --header-env 'x-api-key=SPORTRADAR_API_KEY'
```

Premier League competition ID is documented as:
`sr:competition:17`.

### P3.2 — seasons

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider sportradar \
  --probe-name soccer-seasons \
  --url 'https://api.sportradar.com/soccer/trial/v4/en/seasons.json' \
  --header-env 'x-api-key=SPORTRADAR_API_KEY'
```

Resolve the exact EPL season ID from provider data rather than hardcoding a current-season ID.

### P3.3 — selected season info

After resolving the season ID:

```bash
export SPORTRADAR_SEASON_ID='<sr:season:...>'

python scripts/research/capture_provider_json.py \
  --research-only \
  --provider sportradar \
  --probe-name epl-season-info \
  --url "https://api.sportradar.com/soccer/trial/v4/en/seasons/${SPORTRADAR_SEASON_ID}/info.json" \
  --header-env 'x-api-key=SPORTRADAR_API_KEY'
```

Inspect:
- coverage properties;
- schedules;
- missing players;
- team squads;
- lineups;
- scores;
- `generated_at`.

Do not map response `generated_at` directly to historical `known_at`.

### P3.4 — selected season schedule

```bash
python scripts/research/capture_provider_json.py \
  --research-only \
  --provider sportradar \
  --probe-name epl-season-schedule \
  --url "https://api.sportradar.com/soccer/trial/v4/en/seasons/${SPORTRADAR_SEASON_ID}/schedules.json" \
  --header-env 'x-api-key=SPORTRADAR_API_KEY'
```

Preserve:
- sport-event IDs;
- start time;
- `start_time_confirmed`;
- `date_confirmed` when present.

---

## The Odds API v4

Official historical featured-market endpoint:

`GET /v4/historical/sports/{sport}/odds`

EPL sport key:
`soccer_epl`

Historical access is paid.

Authentication:
query parameter `apiKey`.

Environment:

```bash
export THE_ODDS_API_KEY='...'
```

### P4.0 — do not execute until Stage A spend is approved

Use:
`docs/research/FOOTBALL_ODDS_BAKEOFF_STAGE_A_SAMPLE_v0.1.md`

Initial markets:
- `h2h` = 1X2;
- `totals` = over/under totals.

Initial region:
- one region only.

### P4.1 — one historical schema/timestamp probe

Set a historical ISO-8601 snapshot timestamp from the Stage A plan:

```bash
export ODDS_SNAPSHOT_AT='<YYYY-MM-DDTHH:MM:SSZ>'

python scripts/research/capture_provider_json.py \
  --research-only \
  --provider the-odds-api \
  --probe-name epl-historical-schema \
  --url "https://api.the-odds-api.com/v4/historical/sports/soccer_epl/odds?regions=eu&markets=h2h,totals&oddsFormat=decimal&date=${ODDS_SNAPSHOT_AT}" \
  --query-env 'apiKey=THE_ODDS_API_KEY'
```

Collect:
- requested date;
- returned wrapper timestamp;
- previous/next timestamps;
- event IDs;
- commence times;
- bookmaker IDs;
- bookmaker/market last-update times;
- h2h completeness;
- totals points/lines;
- payload hash;
- received_at.

The documented endpoint returns the closest historical snapshot equal to or earlier than the requested date.

### P4.2 — Stage A

Only after P4.1 passes:
- run 23 kickoff groups;
- T-24h;
- T-1h;
- T-15m;
- h2h + totals;
- one region.

Keep all misses/errors in the denominator.

---

## Evidence completion

After each probe, create a result from:

`docs/research/PROVIDER_PROBE_EVIDENCE_RECORD_TEMPLATE.md`

Allowed evidence statuses:
- VERIFIED_PASS
- VERIFIED_FAIL
- PARTIAL
- DOCUMENTED_NOT_PROBED
- UNKNOWN
- NOT_APPLICABLE

Never use a numeric vendor score.

## Sources verified for command syntax

- API-Football official beginner guide / API-Football documentation.
- Sportmonks API 3.0 authentication and fixture documentation.
- Sportradar official authentication and Soccer v4 documentation.
- The Odds API v4 historical odds documentation.

Re-check provider docs immediately before paid execution because endpoint behavior, pricing and quotas may change.
