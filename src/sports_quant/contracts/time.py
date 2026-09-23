"""Temporal contract and contract-level point-in-time validation.

F2 defines validation semantics only. As-of selection, validity-window enforcement,
version selection and replay belong to the F3 point-in-time kernel.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import CanonicalEnum, Contract, ContractError


class KnownAtBasis(CanonicalEnum):
    """How ``known_at`` was established. No other basis may be introduced in F2."""

    SYSTEM_RECEIPT = "SYSTEM_RECEIPT"
    VERIFIED_SOURCE_AVAILABILITY = "VERIFIED_SOURCE_AVAILABILITY"


@dataclass(frozen=True, kw_only=True)
class TemporalMetadata(Contract):
    """Canonical timestamps of one piece of information.

    ``known_at`` is the earliest verifiable instant at which the information could
    legitimately be used by SPORTS QUANT. It is never inferred from other fields.
    """

    event_time: datetime | None
    published_at: datetime | None
    received_at: datetime | None
    valid_from: datetime | None
    valid_to: datetime | None
    expires_at: datetime | None
    known_at: datetime | None
    known_at_basis: KnownAtBasis | None

    def _validate(self) -> None:
        if (self.known_at is None) != (self.known_at_basis is None):
            raise ContractError(
                "KNOWN_AT_BASIS_MISMATCH",
                "known_at and known_at_basis must be provided together",
            )
        if (
            self.known_at is not None
            and self.known_at_basis is KnownAtBasis.SYSTEM_RECEIPT
            and self.received_at is not None
            and self.known_at < self.received_at
        ):
            raise ContractError(
                "KNOWN_AT_BEFORE_RECEIPT",
                "known_at based on SYSTEM_RECEIPT cannot precede received_at",
            )
        if (
            self.valid_from is not None
            and self.valid_to is not None
            and self.valid_from > self.valid_to
        ):
            raise ContractError("INVALID_VALIDITY_WINDOW", "valid_from must be <= valid_to")


def require_critical_known_at(temporal: TemporalMetadata, decision_cutoff_at: datetime) -> None:
    """Enforce the critical PIT rule ``known_at <= decision_cutoff_at``.

    Missing ``known_at`` is rejected rather than treated as usable.
    """

    if temporal.known_at is None:
        raise ContractError(
            "KNOWN_AT_MISSING",
            "critical information without a defensible known_at is not usable",
        )
    if temporal.known_at > decision_cutoff_at:
        raise ContractError(
            "KNOWN_AT_AFTER_CUTOFF",
            "critical information requires known_at <= decision_cutoff_at",
        )


@dataclass(frozen=True, kw_only=True)
class CriticalInformationUse(Contract):
    """Declares that critical information is used for a decision at a cutoff.

    Construction fails unless the information was legitimately known by the cutoff.
    """

    temporal: TemporalMetadata
    decision_cutoff_at: datetime

    def _validate(self) -> None:
        require_critical_known_at(self.temporal, self.decision_cutoff_at)
