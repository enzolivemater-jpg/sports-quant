# `data/entity_resolution` — F4 deterministic entity resolution

| Module | Contents |
| --- | --- |
| `mapping.py` | `MappingTable`: exact (provider, namespace, external id) → canonical value lookup; `RESOLVED` / `UNMAPPED` / `AMBIGUOUS`; mapping method, review state and evidence per entry |
| `football_epl.py` | Curated EPL 2024/25 identities (competition, season, 20 teams) for the exact OpenFootball labels; canonical id helpers; league-fixture event identity |

No case folding, trimming, similarity or fallback. Unknown identifiers are reported,
colliding ones are ambiguous, and neither is guessed. Curated mappings stay
`CURATED_PENDING_REVIEW` until independent review.
