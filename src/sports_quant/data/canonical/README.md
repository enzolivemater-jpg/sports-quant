# `data/canonical` — F4 canonical Football records

| Module | Contents |
| --- | --- |
| `values.py` | `ValueState` (`OBSERVED`, `NOT_PROVIDED_BY_SOURCE`, `ENDPOINT_UNAVAILABLE`, `UNSUPPORTED_BY_SOURCE`, `NOT_YET_PUBLISHED`, `PARSE_ERROR`); `IntValue`/`DecimalValue`/`InstantValue`; `quality_state` → F2 `QualityState` |
| `football.py` | `FixtureRecord`, `MatchResultRecord` (label only), `OddsObservationRecord`, `BookmakerRef`, `phase_1_market` (Phase 1 families only) |

A canonical record is the payload of a PIT observation; its content digest is the F3
`payload_sha256`. Missing is never zero; a verified zero is `OBSERVED` with `0`.
