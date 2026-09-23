"""Builders for F3 point-in-time kernel tests."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from sports_quant.contracts.data_state import (
    ConflictState,
    DataState,
    FreshnessState,
    QualityState,
    VerificationState,
)
from sports_quant.contracts.provenance import Provenance
from sports_quant.contracts.reproducibility import ArtifactKind, ArtifactRef, CodeVersion
from sports_quant.contracts.source import SourceRef, SourceTier
from sports_quant.contracts.time import KnownAtBasis, TemporalMetadata
from sports_quant.data.point_in_time.records import PitRecord, RawSnapshotRef

CUTOFF = datetime(2024, 8, 16, 12, 0, tzinfo=UTC)
KEY = "fixture-1:home-lineup"
CODE = CodeVersion(commit="30524e812b2b883cb6c032353b5c42573a285793")
DATASET = ArtifactRef(kind=ArtifactKind.SNAPSHOT, identifier="pit-test", version="1")
_UNSET = object()


def at(hours: float) -> datetime:
    """Instant ``hours`` after midnight UTC on the cutoff day (cutoff = at(12))."""

    return datetime(2024, 8, 16, tzinfo=UTC) + timedelta(hours=hours)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def data_state(
    quality: QualityState = QualityState.VALID,
    freshness: FreshnessState = FreshnessState.RECENT,
    verification: VerificationState = VerificationState.VERIFIED,
    conflict: ConflictState = ConflictState.NONE,
) -> DataState:
    return DataState(
        quality=quality, freshness=freshness, verification=verification, conflict=conflict
    )


def version(
    known_at: datetime | None,
    *,
    key: str = KEY,
    revision_id: str | None | object = _UNSET,
    payload: str | None = None,
    basis: KnownAtBasis = KnownAtBasis.SYSTEM_RECEIPT,
    received_at: datetime | None = None,
    published_at: datetime | None = None,
    valid_from: datetime | None = None,
    valid_to: datetime | None = None,
    expires_at: datetime | None = None,
    state: DataState | None = None,
    source_id: str = "provider-a",
    raw: bool = False,
) -> PitRecord:
    """One version. SYSTEM_RECEIPT basis implies received_at == known_at (F2 rule)."""

    stamp = known_at.isoformat() if known_at else "unknown"
    rev = f"rev@{stamp}" if revision_id is _UNSET else revision_id
    assert rev is None or isinstance(rev, str)
    payload = payload if payload is not None else f"value@{stamp}"
    if received_at is None:
        received_at = known_at if known_at is not None else at(0)
    temporal = TemporalMetadata(
        event_time=None,
        published_at=published_at,
        received_at=received_at,
        valid_from=valid_from,
        valid_to=valid_to,
        expires_at=expires_at,
        known_at=known_at,
        known_at_basis=basis if known_at is not None else None,
    )
    return PitRecord(
        logical_key=key,
        revision_id=rev,
        payload_sha256=sha(payload),
        provenance=Provenance(
            source=SourceRef(
                source_id=source_id, tier=SourceTier.LICENSED_PRO, source_version=None
            ),
            external_id="ext-1",
            temporal=temporal,
            data_state=state if state is not None else data_state(),
            critical=known_at is not None,
        ),
        raw_snapshot=(
            RawSnapshotRef(
                source_id=source_id,
                request_identity=f"GET /lineups?fixture=1#{stamp}",
                payload_sha256=sha(f"raw:{payload}"),
                received_at=received_at,
                ingestion_version="ingest-1",
            )
            if raw
            else None
        ),
    )
