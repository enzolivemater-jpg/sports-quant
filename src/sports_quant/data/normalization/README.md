# `data/normalization` — F4 provider/source normalization

Typed, source-specific records parsed from raw capture bytes. Labels, external IDs and
provider timestamps are kept verbatim; no entity resolution and no `known_at` here.
Structural problems fail visibly (`ContractError` with a stable code, line numbers for
text sources).

| Module | Source | State |
| --- | --- | --- |
| `openfootball.py` | OpenFootball Football.TXT season files | EXPERIMENTAL adapter, research-baseline source |
| `the_odds_api.py` | The Odds API historical odds response (documented shape) | EXPERIMENTAL, CANDIDATE provider; parses captured bytes only, live leg blocked |

OD-24 is OPEN: no source is approved. See `data/provenance/sources.py`.
