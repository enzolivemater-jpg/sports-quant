"""Records presented to the point-in-time kernel.

A ``PitRecord`` is one observation of one source version of one logical record. The
kernel never reads the record's value: ``payload_sha256`` binds the version to its
content, and all temporal, source and data-state information comes from the F2
``Provenance``.

Three identities are kept apart:

- source-version identity, ``SourceVersionRef`` = (``source_id``, ``revision_id``):
  which version the source says this is. Its content is ``payload_sha256``;
- observation: one ``PitRecord``, i.e. a source version as received, with its own
  temporal metadata, ``DataState`` and raw-snapshot lineage;
- audit digest: ``PitRecord.content_digest()``, over everything, used only to
  identify observations and for manifest integrity.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import Contract, ContractError, require_non_empty
from sports_quant.contracts.provenance import Provenance

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def require_sha256(value: str, field: str) -> None:
    if not _SHA256_RE.fullmatch(value):
        raise ContractError("INVALID_DIGEST", f"{field} must be a lowercase SHA-256 hex digest")


@dataclass(frozen=True, kw_only=True)
class RawSnapshotRef(Contract):
    """Lineage hook: the immutable raw response a record was normalized from."""

    source_id: str
    request_identity: str
    payload_sha256: str
    received_at: datetime
    ingestion_version: str

    def _validate(self) -> None:
        require_non_empty(self.source_id, "source_id")
        require_non_empty(self.request_identity, "request_identity")
        require_sha256(self.payload_sha256, "payload_sha256")
        require_non_empty(self.ingestion_version, "ingestion_version")


@dataclass(frozen=True, kw_only=True)
class SourceVersionRef(Contract):
    """Identity of a source version: a ``revision_id`` is scoped by its ``source_id``."""

    source_id: str
    revision_id: str

    def _validate(self) -> None:
        require_non_empty(self.source_id, "source_id")
        require_non_empty(self.revision_id, "revision_id")


@dataclass(frozen=True, kw_only=True)
class PitRecord(Contract):
    """One version of a logical record.

    ``logical_key`` is the SPORTS QUANT identity of the logical record (stable across
    revisions); ``revision_id`` is the source's identity for this version, ``None``
    when the source provides none (the version is then unresolved). The source is
    ``provenance.source.source_id``.
    """

    logical_key: str
    revision_id: str | None
    payload_sha256: str
    provenance: Provenance
    raw_snapshot: RawSnapshotRef | None

    def _validate(self) -> None:
        require_non_empty(self.logical_key, "logical_key")
        if self.revision_id is not None:
            require_non_empty(self.revision_id, "revision_id")
        require_sha256(self.payload_sha256, "payload_sha256")

    def source_version(self) -> SourceVersionRef | None:
        """Source-version identity, or ``None`` when the source gives no revision."""

        if self.revision_id is None:
            return None
        return SourceVersionRef(
            source_id=self.provenance.source.source_id, revision_id=self.revision_id
        )
