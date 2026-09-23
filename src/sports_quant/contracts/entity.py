"""Entity identifiers and provenance-safe references.

Entity resolution itself is implemented in a later phase.
"""

from __future__ import annotations

from dataclasses import dataclass

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    require_non_empty,
    require_unique,
)


class Sport(CanonicalEnum):
    """Sports in canonical scope: mandatory (Basketball, Football, MMA) plus the
    validation-only additions (Handball, Volleyball, Tennis)."""

    BASKETBALL = "BASKETBALL"
    FOOTBALL = "FOOTBALL"
    MMA = "MMA"
    HANDBALL = "HANDBALL"
    VOLLEYBALL = "VOLLEYBALL"
    TENNIS = "TENNIS"


class EntityKind(CanonicalEnum):
    COMPETITION = "COMPETITION"
    SEASON = "SEASON"
    EVENT = "EVENT"
    TEAM = "TEAM"
    PARTICIPANT = "PARTICIPANT"


@dataclass(frozen=True, kw_only=True)
class CanonicalEntityId(Contract):
    """SPORTS QUANT internal identifier; never a provider identifier."""

    sport: Sport
    kind: EntityKind
    value: str

    def _validate(self) -> None:
        require_non_empty(self.value, "value")


@dataclass(frozen=True, kw_only=True)
class ProviderEntityRef(Contract):
    """An external identifier as issued by one provider."""

    provider_id: str
    kind: EntityKind
    external_id: str

    def _validate(self) -> None:
        require_non_empty(self.provider_id, "provider_id")
        require_non_empty(self.external_id, "external_id")


@dataclass(frozen=True, kw_only=True)
class EntityRef(Contract):
    """Links a canonical identifier to the provider identifiers it was resolved from."""

    canonical_id: CanonicalEntityId
    provider_refs: tuple[ProviderEntityRef, ...]

    def _validate(self) -> None:
        for ref in self.provider_refs:
            if ref.kind is not self.canonical_id.kind:
                raise ContractError(
                    "ENTITY_KIND_MISMATCH",
                    f"provider ref kind {ref.kind} differs from {self.canonical_id.kind}",
                )
        require_unique(
            tuple((ref.provider_id, ref.external_id) for ref in self.provider_refs),
            "provider_refs",
        )
