"""As-of version selection for one logical record.

Algorithm for the versions of one ``logical_key`` at a cutoff:

1. Exact duplicates (identical record content) collapse to one version.
2. Every version is evaluated for PIT eligibility.
3. Only versions known at or before the cutoff can influence the outcome, so a
   replay equals what a live evaluation at the cutoff would have produced. Versions
   known later, or without ``known_at``, are reported as REJECTED and nothing else.
4. Among those known versions: if one ``revision_id`` appears with different
   content, the key is UNRESOLVED. The *current* version is the one with the latest
   ``known_at``. If none exists: NO_ELIGIBLE_VERSION. If several share that
   ``known_at``: UNRESOLVED.
5. If the current version has no ``revision_id``: UNRESOLVED. If it is otherwise
   not usable (not yet valid / expired at the cutoff): NO_ELIGIBLE_VERSION. There is
   no fallback to an older version, which the current version superseded.
6. Otherwise the current version is SELECTED and older eligible versions are
   SUPERSEDED.

No step depends on input order, and ties are never broken arbitrarily: an
ambiguity yields UNRESOLVED instead of a guessed version.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    instant,
    require_aware_datetime,
    require_non_empty,
)
from sports_quant.data.point_in_time.eligibility import (
    PitRejectionReason,
    canonical_reasons,
    rejection_reasons,
)
from sports_quant.data.point_in_time.records import PitRecord, require_sha256


class RecordDisposition(CanonicalEnum):
    SELECTED = "SELECTED"
    SUPERSEDED = "SUPERSEDED"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


class SelectionStatus(CanonicalEnum):
    SELECTED = "SELECTED"
    NO_ELIGIBLE_VERSION = "NO_ELIGIBLE_VERSION"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, kw_only=True)
class RecordDecision(Contract):
    """What happened to one distinct version, with its source/version lineage."""

    logical_key: str
    record_digest: str
    revision_id: str | None
    source_id: str
    known_at: datetime | None
    raw_payload_sha256: str | None
    disposition: RecordDisposition
    reasons: tuple[PitRejectionReason, ...]

    def _validate(self) -> None:
        require_non_empty(self.logical_key, "logical_key")
        require_sha256(self.record_digest, "record_digest")
        if self.reasons != canonical_reasons(set(self.reasons)):
            raise ContractError("NON_CANONICAL_REASONS", "reasons must be unique and ordered")
        if (self.disposition is RecordDisposition.REJECTED) != bool(self.reasons):
            raise ContractError(
                "DISPOSITION_MISMATCH", "a version is REJECTED exactly when it has reasons"
            )


@dataclass(frozen=True, kw_only=True)
class AsOfSelection(Contract):
    logical_key: str
    decision_cutoff_at: datetime
    status: SelectionStatus
    selected: PitRecord | None
    decisions: tuple[RecordDecision, ...]

    def _validate(self) -> None:
        require_non_empty(self.logical_key, "logical_key")
        digests = tuple(decision.record_digest for decision in self.decisions)
        if digests != tuple(sorted(set(digests))) or not digests:
            raise ContractError(
                "NON_CANONICAL_DECISIONS", "decisions must be non-empty, unique and ordered"
            )
        if any(decision.logical_key != self.logical_key for decision in self.decisions):
            raise ContractError("MIXED_LOGICAL_KEYS", "decisions must share the logical key")
        chosen = [d for d in self.decisions if d.disposition is RecordDisposition.SELECTED]
        if (self.status is SelectionStatus.SELECTED) != (self.selected is not None):
            raise ContractError("SELECTION_MISMATCH", "SELECTED status requires a selection")
        if self.selected is None:
            if chosen:
                raise ContractError("SELECTION_MISMATCH", "no version may be SELECTED")
        elif [d.record_digest for d in chosen] != [self.selected.content_digest()]:
            raise ContractError("SELECTION_MISMATCH", "exactly the selected version is SELECTED")


def select_as_of(records: Iterable[PitRecord], decision_cutoff_at: datetime) -> AsOfSelection:
    """Select the version of one logical record that was usable at the cutoff."""

    require_aware_datetime(decision_cutoff_at, "decision_cutoff_at")
    cutoff = instant(decision_cutoff_at)
    versions = {record.content_digest(): record for record in records}
    if not versions:
        raise ContractError("NO_RECORDS", "as-of selection needs at least one version")
    keys = {record.logical_key for record in versions.values()}
    if len(keys) != 1:
        raise ContractError("MIXED_LOGICAL_KEYS", f"expected one logical key, got {sorted(keys)}")
    (logical_key,) = keys

    reasons = {digest: rejection_reasons(r, decision_cutoff_at) for digest, r in versions.items()}

    known = [
        digest
        for digest, record in versions.items()
        if record.provenance.temporal.known_at is not None and _known_at(record) <= cutoff
    ]
    digests_by_revision: dict[str, set[str]] = defaultdict(set)
    for digest in known:
        revision_id = versions[digest].revision_id
        if revision_id is not None:
            digests_by_revision[revision_id].add(digest)
    unresolved = any(len(digests) > 1 for digests in digests_by_revision.values())

    selected_digest: str | None = None
    if known and not unresolved:
        latest = max(_known_at(versions[digest]) for digest in known)
        current = [digest for digest in known if _known_at(versions[digest]) == latest]
        if len(current) > 1 or versions[current[0]].revision_id is None:
            unresolved = True
        elif not reasons[current[0]]:
            selected_digest = current[0]

    decisions = tuple(
        _decision(versions[digest], digest, reasons[digest], unresolved, selected_digest)
        for digest in sorted(versions)
    )
    if unresolved:
        status = SelectionStatus.UNRESOLVED
    elif selected_digest is not None:
        status = SelectionStatus.SELECTED
    else:
        status = SelectionStatus.NO_ELIGIBLE_VERSION
    return AsOfSelection(
        logical_key=logical_key,
        decision_cutoff_at=decision_cutoff_at,
        status=status,
        selected=versions[selected_digest] if selected_digest is not None else None,
        decisions=decisions,
    )


def _known_at(record: PitRecord) -> datetime:
    known_at = record.provenance.temporal.known_at
    if known_at is None:
        raise ContractError("KNOWN_AT_MISSING", "only versions with a known_at can be ordered")
    return instant(known_at)


def _decision(
    record: PitRecord,
    digest: str,
    reasons: tuple[PitRejectionReason, ...],
    unresolved: bool,
    selected_digest: str | None,
) -> RecordDecision:
    if reasons:
        disposition = RecordDisposition.REJECTED
    elif unresolved:
        disposition = RecordDisposition.UNRESOLVED
    elif digest == selected_digest:
        disposition = RecordDisposition.SELECTED
    else:
        disposition = RecordDisposition.SUPERSEDED
    return RecordDecision(
        logical_key=record.logical_key,
        record_digest=digest,
        revision_id=record.revision_id,
        source_id=record.provenance.source.source_id,
        known_at=record.provenance.temporal.known_at,
        raw_payload_sha256=(
            record.raw_snapshot.payload_sha256 if record.raw_snapshot is not None else None
        ),
        disposition=disposition,
        reasons=reasons,
    )
