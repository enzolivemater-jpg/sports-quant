"""PIT eligibility of a single record version at a decision cutoff.

Eligibility is decided only by temporal, validity and version-identity inputs. The
F2 ``DataState`` (quality, freshness, verification, conflict) is never consulted:
whether data is good enough to qualify a decision belongs to later gate layers.

The ``known_at`` rule is not re-implemented here: it is F2's
``require_critical_known_at``, whose error codes are mapped to F3 reasons.
Missing ``known_at`` makes any record ineligible, whether or not it is critical.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    instant,
    require_aware_datetime,
)
from sports_quant.contracts.time import KnownAtBasis, require_critical_known_at
from sports_quant.data.point_in_time.records import PitRecord, require_sha256


class PitRejectionReason(CanonicalEnum):
    """Why a version is not usable at a cutoff. Declaration order is canonical order."""

    MISSING_KNOWN_AT = "MISSING_KNOWN_AT"
    KNOWN_AFTER_CUTOFF = "KNOWN_AFTER_CUTOFF"
    NOT_YET_VALID_AT_CUTOFF = "NOT_YET_VALID_AT_CUTOFF"
    EXPIRED_AT_CUTOFF = "EXPIRED_AT_CUTOFF"
    SOURCE_VERSION_UNRESOLVED = "SOURCE_VERSION_UNRESOLVED"


_REASON_ORDER = {reason: index for index, reason in enumerate(PitRejectionReason)}

# F2 ContractError code -> F3 reason. Same rule, reported instead of raised.
F2_KNOWN_AT_CODE_TO_REASON = {
    "KNOWN_AT_MISSING": PitRejectionReason.MISSING_KNOWN_AT,
    "KNOWN_AT_AFTER_CUTOFF": PitRejectionReason.KNOWN_AFTER_CUTOFF,
}


def canonical_reasons(reasons: set[PitRejectionReason]) -> tuple[PitRejectionReason, ...]:
    return tuple(sorted(reasons, key=_REASON_ORDER.__getitem__))


@dataclass(frozen=True, kw_only=True)
class PitEligibility(Contract):
    decision_cutoff_at: datetime
    record_digest: str
    eligible: bool
    reasons: tuple[PitRejectionReason, ...]
    known_at: datetime | None
    known_at_basis: KnownAtBasis | None

    def _validate(self) -> None:
        require_sha256(self.record_digest, "record_digest")
        if self.reasons != canonical_reasons(set(self.reasons)):
            raise ContractError("NON_CANONICAL_REASONS", "reasons must be unique and ordered")
        if self.eligible == bool(self.reasons):
            raise ContractError(
                "ELIGIBILITY_MISMATCH", "a record is eligible exactly when it has no reasons"
            )


def rejection_reasons(
    record: PitRecord, decision_cutoff_at: datetime
) -> tuple[PitRejectionReason, ...]:
    """All reasons ``record`` cannot be used at ``decision_cutoff_at``, canonically ordered.

    Validity bounds: ``valid_from`` is inclusive, ``valid_to`` is inclusive and
    ``expires_at`` is exclusive (a record is expired at its ``expires_at`` instant).
    Absent bounds impose nothing.
    """

    require_aware_datetime(decision_cutoff_at, "decision_cutoff_at")
    temporal = record.provenance.temporal
    cutoff = instant(decision_cutoff_at)
    reasons: set[PitRejectionReason] = set()

    try:
        require_critical_known_at(temporal, decision_cutoff_at)
    except ContractError as exc:
        reasons.add(F2_KNOWN_AT_CODE_TO_REASON[exc.code])

    if temporal.valid_from is not None and cutoff < instant(temporal.valid_from):
        reasons.add(PitRejectionReason.NOT_YET_VALID_AT_CUTOFF)
    if temporal.valid_to is not None and cutoff > instant(temporal.valid_to):
        reasons.add(PitRejectionReason.EXPIRED_AT_CUTOFF)
    if temporal.expires_at is not None and cutoff >= instant(temporal.expires_at):
        reasons.add(PitRejectionReason.EXPIRED_AT_CUTOFF)
    if record.revision_id is None:
        reasons.add(PitRejectionReason.SOURCE_VERSION_UNRESOLVED)

    return canonical_reasons(reasons)


def evaluate_eligibility(record: PitRecord, decision_cutoff_at: datetime) -> PitEligibility:
    """Could this exact version legitimately have been used at this cutoff?"""

    reasons = rejection_reasons(record, decision_cutoff_at)
    temporal = record.provenance.temporal
    return PitEligibility(
        decision_cutoff_at=decision_cutoff_at,
        record_digest=record.content_digest(),
        eligible=not reasons,
        reasons=reasons,
        known_at=temporal.known_at,
        known_at_basis=temporal.known_at_basis,
    )
