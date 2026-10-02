# `data/ingestion` — F4 Football data layer flow

Specification: `docs/contracts/F4_FOOTBALL_DATA_LAYER_SPEC_DRAFT.md` (issue #7).

```
source file / response bytes
  -> RawCapture + RawSnapshotStore          (data/snapshots: immutable, hashed, redacted)
  -> typed source records                   (data/normalization)
  -> canonical Football records             (data/canonical, data/entity_resolution)
  -> CanonicalObservation = record + F3 PitRecord (provenance, revision, raw lineage)
  -> F3 materialize at a cutoff             (data/point_in_time, unchanged)
  -> FootballPitDataset + build manifest    (feature-ready rows, deterministic hash)
```

| Module | Contents |
| --- | --- |
| `football.py` | `build_football` (captures → `FootballBuild`: observations, issues, gaps, conflicts, unresolved identifiers); `openfootball_capture`; `git_blob_sha`; `detect_conflicts` |
| `dataset.py` | `materialize_football` (F3 only); `build_manifest` / `FootballBuildManifest` (reproducibility evidence) |

## Rules

- `known_at` is `SYSTEM_RECEIPT` only (= `received_at`). Provider timestamps, Git history
  and dataset `last_updated` values are kept as data and never become `known_at`; no
  `VERIFIED_SOURCE_AVAILABILITY` mapping is approved. Data captured retrospectively is
  therefore not usable at earlier historical cutoffs (fail closed).
- Source versions: OpenFootball revision = Git blob id of the file; odds revision = the
  provider snapshot timestamp. A correction is a new revision; nothing is overwritten.
- Conflicts (different content across sources, or within one source version) are
  reported with every observation retained; F3 leaves such keys `UNRESOLVED`.
- A record present in an earlier file revision but absent from a later one is reported
  (`RECORD_ABSENT_IN_LATER_REVISION`); F2/F3 define no deletion, so it is not applied.
- `DataState`: quality from value states; freshness `DELAYED` for
  `RETROSPECTIVE_ARCHIVE` captures (no freshness windows are defined, OD-13);
  verification `UNVERIFIED`; conflict `NONE` (conflicts live in the build report).
- Odds: Phase 1 only; 1X2 outcomes mapped by label, never array order; a totals market
  is `FOOTBALL_TOTAL_GOALS_MAIN` only when it carries exactly one line; the provider's
  next-snapshot timestamp never enters canonical records.

The build reads no clock and fetches nothing. Same captures + mappings + context ⇒
same build; the manifest hash excludes run identity and wall-clock times.

CLIs (no network): `scripts/data/capture_openfootball_season.py`,
`scripts/data/rebuild_football_dataset.py`.
