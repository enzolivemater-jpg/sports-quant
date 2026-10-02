"""PIT materialization and its replay manifest.

``materialize`` applies as-of selection to every logical key of a batch at one
cutoff. The resulting ``PitManifest`` splits into a deterministic ``body`` and the
wall-clock ``created_at``: ``content_hash`` is the SHA-256 of the body's canonical
JSON, so replaying the same records at the same cutoff with the same code/dataset
references reproduces the same hash regardless of input order or run time.
The kernel never reads a clock; the caller supplies ``created_at``.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import (
    Contract,
    ContractError,
    require_aware_datetime,
    require_non_empty,
)
from sports_quant.contracts.reproducibility import (
    DATA_ARTIFACT_KINDS,
    ArtifactRef,
    CodeVersion,
    require_artifact_kind,
)
from sports_quant.data.point_in_time.eligibility import PitRejectionReason
from sports_quant.data.point_in_time.records import PitRecord, require_sha256
from sports_quant.data.point_in_time.selection import (
    RecordDecision,
    RecordDisposition,
    SelectionStatus,
    select_as_of,
)


@dataclass(frozen=True, kw_only=True)
class KeyOutcome(Contract):
    logical_key: str
    status: SelectionStatus
    selected_record_digest: str | None

    def _validate(self) -> None:
        require_non_empty(self.logical_key, "logical_key")
        if (self.status is SelectionStatus.SELECTED) != (self.selected_record_digest is not None):
            raise ContractError("SELECTION_MISMATCH", "only SELECTED keys carry a digest")
        if self.selected_record_digest is not None:
            require_sha256(self.selected_record_digest, "selected_record_digest")


@dataclass(frozen=True, kw_only=True)
class DispositionCount(Contract):
    disposition: RecordDisposition
    count: int


@dataclass(frozen=True, kw_only=True)
class ReasonCount(Contract):
    reason: PitRejectionReason
    count: int


@dataclass(frozen=True, kw_only=True)
class PitManifestBody(Contract):
    """Deterministic content of a materialization; everything except ``created_at``.

    Keys are ordered by ``logical_key``; decisions by (``logical_key``,
    ``record_digest``); counts list every disposition/reason in canonical order,
    including zeros. ``input_record_count`` counts inputs before exact-duplicate
    collapse; ``record_decisions`` has one entry per distinct version.
    """

    decision_cutoff_at: datetime
    code_version: CodeVersion
    dataset_ref: ArtifactRef
    input_record_count: int
    key_outcomes: tuple[KeyOutcome, ...]
    record_decisions: tuple[RecordDecision, ...]
    disposition_counts: tuple[DispositionCount, ...]
    reason_counts: tuple[ReasonCount, ...]

    def _validate(self) -> None:
        require_artifact_kind(self.dataset_ref, DATA_ARTIFACT_KINDS, "dataset_ref")
        keys = tuple(outcome.logical_key for outcome in self.key_outcomes)
        order = tuple((d.logical_key, d.record_digest) for d in self.record_decisions)
        if keys != tuple(sorted(set(keys))) or order != tuple(sorted(set(order))):
            raise ContractError("NON_CANONICAL_MANIFEST", "keys/decisions must be unique+ordered")
        if set(keys) != {logical_key for logical_key, _digest in order}:
            raise ContractError("NON_CANONICAL_MANIFEST", "every key needs decisions")
        if self.input_record_count < len(self.record_decisions):
            raise ContractError("COUNT_MISMATCH", "fewer inputs than distinct versions")
        selected = {
            (d.logical_key, d.record_digest)
            for d in self.record_decisions
            if d.disposition is RecordDisposition.SELECTED
        }
        outcomes = {
            (o.logical_key, o.selected_record_digest)
            for o in self.key_outcomes
            if o.selected_record_digest is not None
        }
        if selected != outcomes:
            raise ContractError("SELECTION_MISMATCH", "SELECTED versions must match key outcomes")
        if self.disposition_counts != _disposition_counts(self.record_decisions):
            raise ContractError("COUNT_MISMATCH", "disposition counts do not match decisions")
        if self.reason_counts != _reason_counts(self.record_decisions):
            raise ContractError("COUNT_MISMATCH", "reason counts do not match decisions")


@dataclass(frozen=True, kw_only=True)
class PitManifest(Contract):
    body: PitManifestBody
    content_hash: str
    created_at: datetime

    def _validate(self) -> None:
        if self.content_hash != self.body.content_digest():
            raise ContractError("CONTENT_HASH_MISMATCH", "content_hash must hash the body")


@dataclass(frozen=True, kw_only=True)
class PitMaterialization(Contract):
    manifest: PitManifest
    selected: tuple[PitRecord, ...]

    def _validate(self) -> None:
        expected = tuple(
            (o.logical_key, o.selected_record_digest)
            for o in self.manifest.body.key_outcomes
            if o.selected_record_digest is not None
        )
        actual = tuple((r.logical_key, r.content_digest()) for r in self.selected)
        if actual != expected:
            raise ContractError("SELECTION_MISMATCH", "selected records must match the manifest")


def materialize(
    records: Iterable[PitRecord],
    *,
    decision_cutoff_at: datetime,
    code_version: CodeVersion,
    dataset_ref: ArtifactRef,
    created_at: datetime,
) -> PitMaterialization:
    """Select, for every logical key, the version usable at the cutoff."""

    require_aware_datetime(decision_cutoff_at, "decision_cutoff_at")
    inputs = tuple(records)
    by_key: dict[str, list[PitRecord]] = defaultdict(list)
    for record in inputs:
        by_key[record.logical_key].append(record)
    selections = [select_as_of(by_key[key], decision_cutoff_at) for key in sorted(by_key)]

    decisions = tuple(decision for selection in selections for decision in selection.decisions)
    body = PitManifestBody(
        decision_cutoff_at=decision_cutoff_at,
        code_version=code_version,
        dataset_ref=dataset_ref,
        input_record_count=len(inputs),
        key_outcomes=tuple(
            KeyOutcome(
                logical_key=selection.logical_key,
                status=selection.status,
                selected_record_digest=(
                    selection.selected.content_digest() if selection.selected else None
                ),
            )
            for selection in selections
        ),
        record_decisions=decisions,
        disposition_counts=_disposition_counts(decisions),
        reason_counts=_reason_counts(decisions),
    )
    return PitMaterialization(
        manifest=PitManifest(body=body, content_hash=body.content_digest(), created_at=created_at),
        selected=tuple(s.selected for s in selections if s.selected is not None),
    )


def verify_replay(manifest: PitManifest, records: Iterable[PitRecord]) -> None:
    """Re-materialize ``records`` with the manifest's inputs; the hash must match."""

    replayed = materialize(
        records,
        decision_cutoff_at=manifest.body.decision_cutoff_at,
        code_version=manifest.body.code_version,
        dataset_ref=manifest.body.dataset_ref,
        created_at=manifest.created_at,
    )
    if replayed.manifest.content_hash != manifest.content_hash:
        raise ContractError("REPLAY_MISMATCH", "replay does not reproduce the manifest")


def _disposition_counts(decisions: tuple[RecordDecision, ...]) -> tuple[DispositionCount, ...]:
    return tuple(
        DispositionCount(
            disposition=disposition,
            count=sum(1 for d in decisions if d.disposition is disposition),
        )
        for disposition in RecordDisposition
    )


def _reason_counts(decisions: tuple[RecordDecision, ...]) -> tuple[ReasonCount, ...]:
    return tuple(
        ReasonCount(reason=reason, count=sum(1 for d in decisions if reason in d.reasons))
        for reason in PitRejectionReason
    )
