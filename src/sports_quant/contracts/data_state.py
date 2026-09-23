"""Four orthogonal data-state axes.

The axes are independent: no combination is forbidden and none is derived from
another. They must never be collapsed into a single status. Sports Intelligence
``ClaimType.CONFLICT`` is a different concept from ``ConflictState``.
"""

from __future__ import annotations

from dataclasses import dataclass

from sports_quant.contracts.common import CanonicalEnum, Contract


class QualityState(CanonicalEnum):
    VALID = "VALID"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"


class FreshnessState(CanonicalEnum):
    LIVE = "LIVE"
    RECENT = "RECENT"
    DELAYED = "DELAYED"
    STALE = "STALE"
    SUPERSEDED = "SUPERSEDED"


class VerificationState(CanonicalEnum):
    NOT_REQUIRED = "NOT_REQUIRED"
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    CROSS_CONFIRMED = "CROSS_CONFIRMED"


class ConflictState(CanonicalEnum):
    NONE = "NONE"
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


@dataclass(frozen=True, kw_only=True)
class DataState(Contract):
    quality: QualityState
    freshness: FreshnessState
    verification: VerificationState
    conflict: ConflictState
