"""As-of version selection for one logical record.

A logical record is observed as ``PitRecord`` observations. Each identified
observation belongs to a source version, ``SourceVersionRef`` = (``source_id``,
``revision_id``), whose content is ``payload_sha256``. ``DataState``, receipt and
raw-snapshot lineage belong to the observation, never to the source version.

Algorithm for the observations of one ``logical_key`` at a cutoff:

1. Exact duplicates (identical record content) collapse to one observation.
2. Every observation is evaluated for PIT eligibility (``rejection_reasons``).
3. Only observations known at or before the cutoff (*visible*) can influence the
   outcome, so a replay equals what a live evaluation at the cutoff would have
   produced. Observations known later, or without ``known_at``, are REJECTED and
   nothing else.
4. Source-content conflict: if one source version has visible observations with
   different ``payload_sha256``, the key is UNRESOLVED.
5. Candidates are the source versions with at least one eligible visible
   observation. A source version is usable from its earliest eligible observation.
   The selected source version is the candidate usable latest, provided every
   eligible observation of every other candidate is known strictly before that
   instant. Otherwise the order of the candidates is ambiguous (a tie, or an older
   version observed again afterwards) and the key is UNRESOLVED.
6. An unidentified observation (no ``revision_id``) that is visible and otherwise
   eligible, known at or after the selected version became usable (or at all, when
   no candidate exists), makes the key UNRESOLVED: it may be a newer version.
7. Otherwise the earliest eligible observation of the selected source version is
   SELECTED (ties: smallest record digest); its other eligible observations are
   DUPLICATE_OBSERVATION and eligible observations of other source versions are
   ELIGIBLE_NOT_LATEST. With no candidate the key is NO_ELIGIBLE_VERSION.

Knowing a version does not supersede another: an observation that is not yet
valid or expired at the cutoff is REJECTED and does not affect the others. No step
depends on input order or on ``DataState``, and ambiguities yield UNRESOLVED
instead of a guessed version.
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
from sports_quant.data.point_in_time.records import PitRecord, SourceVersionRef, require_sha256


class RecordDisposition(CanonicalEnum):
    SELECTED = "SELECTED"
    DUPLICATE_OBSERVATION = "DUPLICATE_OBSERVATION"
    ELIGIBLE_NOT_LATEST = "ELIGIBLE_NOT_LATEST"
    REJECTED = "REJECTED"
    UNRESOLVED = "UNRESOLVED"


class SelectionStatus(CanonicalEnum):
    SELECTED = "SELECTED"
    NO_ELIGIBLE_VERSION = "NO_ELIGIBLE_VERSION"
    UNRESOLVED = "UNRESOLVED"


@dataclass(frozen=True, kw_only=True)
class RecordDecision(Contract):
    """What happened to one distinct observation, with its source/version lineage."""

    logical_key: str
    record_digest: str
    source_id: str
    revision_id: str | None
    payload_sha256: str
    known_at: datetime | None
    raw_payload_sha256: str | None
    disposition: RecordDisposition
    reasons: tuple[PitRejectionReason, ...]

    def _validate(self) -> None:
        require_non_empty(self.logical_key, "logical_key")
        require_sha256(self.record_digest, "record_digest")
        require_sha256(self.payload_sha256, "payload_sha256")
        if self.reasons != canonical_reasons(set(self.reasons)):
            raise ContractError("NON_CANONICAL_REASONS", "reasons must be unique and ordered")
        if (self.disposition is RecordDisposition.REJECTED) != bool(self.reasons):
            raise ContractError(
                "DISPOSITION_MISMATCH", "a version is REJECTED exactly when it has reasons"
            )

    def source_version(self) -> tuple[str, str | None, str]:
        """(``source_id``, ``revision_id``, ``payload_sha256``) of the observation."""

        return self.source_id, self.revision_id, self.payload_sha256


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
        duplicates = [
            d for d in self.decisions if d.disposition is RecordDisposition.DUPLICATE_OBSERVATION
        ]
        if (self.status is SelectionStatus.SELECTED) != (self.selected is not None):
            raise ContractError("SELECTION_MISMATCH", "SELECTED status requires a selection")
        if self.selected is None:
            if chosen or duplicates:
                raise ContractError("SELECTION_MISMATCH", "no version may be SELECTED")
            return
        if [d.record_digest for d in chosen] != [self.selected.content_digest()]:
            raise ContractError("SELECTION_MISMATCH", "exactly the selected version is SELECTED")
        if any(d.source_version() != chosen[0].source_version() for d in duplicates):
            raise ContractError(
                "SELECTION_MISMATCH", "duplicate observations must share the selected version"
            )


def select_as_of(records: Iterable[PitRecord], decision_cutoff_at: datetime) -> AsOfSelection:
    """Select the version of one logical record that was usable at the cutoff."""

    require_aware_datetime(decision_cutoff_at, "decision_cutoff_at")
    cutoff = instant(decision_cutoff_at)
    observations = {record.content_digest(): record for record in records}
    if not observations:
        raise ContractError("NO_RECORDS", "as-of selection needs at least one version")
    keys = {record.logical_key for record in observations.values()}
    if len(keys) != 1:
        raise ContractError("MIXED_LOGICAL_KEYS", f"expected one logical key, got {sorted(keys)}")
    (logical_key,) = keys

    reasons = {
        digest: rejection_reasons(record, decision_cutoff_at)
        for digest, record in observations.items()
    }
    visible = [
        digest
        for digest, record in observations.items()
        if record.provenance.temporal.known_at is not None and _known_at(record) <= cutoff
    ]

    payloads: dict[SourceVersionRef, set[str]] = defaultdict(set)
    for digest in visible:
        source_version = observations[digest].source_version()
        if source_version is not None:
            payloads[source_version].add(observations[digest].payload_sha256)
    unresolved = any(len(content) > 1 for content in payloads.values())

    eligible: dict[SourceVersionRef, list[str]] = defaultdict(list)
    for digest in visible:
        source_version = observations[digest].source_version()
        if not reasons[digest] and source_version is not None:
            eligible[source_version].append(digest)
    usable_from = {
        source_version: min(_known_at(observations[digest]) for digest in digests)
        for source_version, digests in eligible.items()
    }

    selected_version: SourceVersionRef | None = None
    if not unresolved and eligible:
        latest = max(usable_from, key=usable_from.__getitem__)
        last_seen = {
            source_version: max(_known_at(observations[digest]) for digest in digests)
            for source_version, digests in eligible.items()
        }
        if all(last_seen[other] < usable_from[latest] for other in eligible if other != latest):
            selected_version = latest
        else:
            unresolved = True

    only_unidentified = (PitRejectionReason.SOURCE_VERSION_UNRESOLVED,)
    if any(
        reasons[digest] == only_unidentified
        and (
            selected_version is None
            or _known_at(observations[digest]) >= usable_from[selected_version]
        )
        for digest in visible
    ):
        unresolved = True

    selected_digest: str | None = None
    if unresolved:
        selected_version = None
    elif selected_version is not None:
        selected_digest = min(
            eligible[selected_version],
            key=lambda digest: (_known_at(observations[digest]), digest),
        )

    decisions = tuple(
        _decision(
            observations[digest],
            digest,
            reasons[digest],
            unresolved=unresolved,
            selected_digest=selected_digest,
            selected_version=selected_version,
        )
        for digest in sorted(observations)
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
        selected=observations[selected_digest] if selected_digest is not None else None,
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
    *,
    unresolved: bool,
    selected_digest: str | None,
    selected_version: SourceVersionRef | None,
) -> RecordDecision:
    if reasons:
        disposition = RecordDisposition.REJECTED
    elif unresolved:
        disposition = RecordDisposition.UNRESOLVED
    elif digest == selected_digest:
        disposition = RecordDisposition.SELECTED
    elif record.source_version() == selected_version:
        disposition = RecordDisposition.DUPLICATE_OBSERVATION
    else:
        disposition = RecordDisposition.ELIGIBLE_NOT_LATEST
    return RecordDecision(
        logical_key=record.logical_key,
        record_digest=digest,
        source_id=record.provenance.source.source_id,
        revision_id=record.revision_id,
        payload_sha256=record.payload_sha256,
        known_at=record.provenance.temporal.known_at,
        raw_payload_sha256=(
            record.raw_snapshot.payload_sha256 if record.raw_snapshot is not None else None
        ),
        disposition=disposition,
        reasons=reasons,
    )
