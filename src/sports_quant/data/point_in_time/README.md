# `data/point_in_time` — F3 point-in-time kernel

Answers: could this exact record version legitimately have been used at this exact
historical decision cutoff? Specification:
`docs/contracts/F3_POINT_IN_TIME_KERNEL_SPEC_DRAFT.md`.

| Module | Contents |
| --- | --- |
| `records.py` | `PitRecord` (one version of a logical record), `RawSnapshotRef` lineage hook |
| `eligibility.py` | `PitRejectionReason`, `rejection_reasons`, `evaluate_eligibility` |
| `selection.py` | `select_as_of` (per logical key), `RecordDecision`, dispositions |
| `manifest.py` | `materialize`, `PitManifest` (deterministic `content_hash`), `verify_replay` |
| `timezones.py` | `localize_provider_time` (explicit zone; ambiguous/nonexistent rejected) |

Eligibility depends only on temporal, validity and version-identity inputs. The F2
`DataState` is carried through unchanged and never affects eligibility.

## Rejection reasons and their relation to F2

| F3 `PitRejectionReason` | Source of the rule |
| --- | --- |
| `MISSING_KNOWN_AT` | F2 `require_critical_known_at`, error `KNOWN_AT_MISSING` (reported, not raised) |
| `KNOWN_AFTER_CUTOFF` | F2 `require_critical_known_at`, error `KNOWN_AT_AFTER_CUTOFF` (reported, not raised) |
| `NOT_YET_VALID_AT_CUTOFF` | `valid_from` after the cutoff (`valid_from` inclusive) |
| `EXPIRED_AT_CUTOFF` | `valid_to` before the cutoff (inclusive) or `expires_at` at/before it (exclusive) |
| `SOURCE_VERSION_UNRESOLVED` | the version has no `revision_id` |

The spec's `INVALID_TIMEZONE` is enforced where invalid times arise instead of per
record: F2 rejects naive datetimes when a contract is built (`NAIVE_DATETIME`), and
`localize_provider_time` rejects unknown zones and ambiguous/nonexistent DST wall
times (`INVALID_TIMEZONE`). A `PitRecord` therefore cannot carry an invalid time.

Key-level ambiguity (tied `known_at`, one `revision_id` with different content, or
an unidentified current version) makes the logical key `UNRESOLVED`: nothing is
selected and no tie is broken arbitrarily. All temporal comparisons are
instant-based (`contracts.common.instant`).
