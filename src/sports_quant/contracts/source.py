"""Canonical source taxonomy and explicit legacy normalization."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    require_non_empty,
)


class SourceTier(CanonicalEnum):
    OFFICIAL = "OFFICIAL"
    LICENSED_PRO = "LICENSED_PRO"
    TRUSTED_SPECIALIST = "TRUSTED_SPECIALIST"
    TRUSTED_JOURNALIST = "TRUSTED_JOURNALIST"
    AGGREGATOR = "AGGREGATOR"
    SOCIAL_UNVERIFIED = "SOCIAL_UNVERIFIED"


LEGACY_SOURCE_TIER_NORMALIZATION: Mapping[str, SourceTier] = MappingProxyType(
    {
        "LICENSED DATA": SourceTier.LICENSED_PRO,
        "LICENSED PROFESSIONAL": SourceTier.LICENSED_PRO,
        "SOCIAL": SourceTier.SOCIAL_UNVERIFIED,
        "SOCIAL/UNVERIFIED": SourceTier.SOCIAL_UNVERIFIED,
    }
)


def normalize_source_tier(value: str) -> SourceTier:
    """Map a canonical or approved legacy label to its canonical tier.

    Matching is exact. Canonical storage and deserialization accept canonical values
    only; legacy labels must pass through this function first.
    """

    legacy = LEGACY_SOURCE_TIER_NORMALIZATION.get(value)
    if legacy is not None:
        return legacy
    try:
        return SourceTier.parse(value)
    except ContractError as exc:
        raise ContractError(
            "UNKNOWN_SOURCE_TIER", f"{value!r} is neither canonical nor approved legacy"
        ) from exc


@dataclass(frozen=True, kw_only=True)
class SourceRef(Contract):
    """Identifies the source/provider of a record and, when available, its version."""

    source_id: str
    tier: SourceTier
    source_version: str | None

    def _validate(self) -> None:
        require_non_empty(self.source_id, "source_id")
        if self.source_version is not None:
            require_non_empty(self.source_version, "source_version")
