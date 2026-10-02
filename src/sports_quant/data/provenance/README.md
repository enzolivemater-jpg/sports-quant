# `data/provenance` — F4 source registry

`sources.py` records every Football source considered so far with its F2 `SourceTier`
(only for sources with an implemented adapter), its candidate/research role from the
provider evidence matrix, adapter state and live-ingestion state. Every source is
`NOT_APPROVED` (OD-24 OPEN); there is no ranking and F4 never arbitrates between sources.
