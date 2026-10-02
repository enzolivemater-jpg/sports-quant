# `data/snapshots` — F4 immutable raw zone

| Module | Contents |
| --- | --- |
| `raw.py` | `RawCapture` (source, resource, redacted request parameters, `received_at`, provider timestamps, source revision, payload SHA-256/size, media type, HTTP status, ingestion version); `capture()`; `snapshot_ref()` → F3 `RawSnapshotRef` |
| `store.py` | `RawSnapshotStore`: write-once, content-addressed filesystem store; re-verifies hashes on every read |

Captures are never edited: a re-fetch or correction is a new capture. Credential-like
request parameters are redacted at capture time and an unredacted one cannot be
constructed; credentials in the resource string are rejected. See
`data/ingestion/README.md` for the full F4 flow.
