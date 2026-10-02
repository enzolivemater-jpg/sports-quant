"""Deterministic provider-identifier -> canonical-identifier mapping.

Resolution is an exact lookup of (provider, namespace, external id) in an explicit
table of curated mappings. There is no case folding, trimming, similarity scoring or
fallback: an identifier that is not in the table is ``UNMAPPED``, and one the table
maps to more than one canonical target is ``AMBIGUOUS``. Neither is ever guessed.

Each mapping records how it was established and its review state, so a mapping
cannot silently look more trustworthy than its evidence.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    require_non_empty,
    require_unique,
)


class MappingMethod(CanonicalEnum):
    EXACT_EXTERNAL_ID = "EXACT_EXTERNAL_ID"
    CURATED_ALIAS = "CURATED_ALIAS"


class ReviewState(CanonicalEnum):
    CURATED_PENDING_REVIEW = "CURATED_PENDING_REVIEW"
    REVIEWED = "REVIEWED"


class ResolutionStatus(CanonicalEnum):
    RESOLVED = "RESOLVED"
    UNMAPPED = "UNMAPPED"
    AMBIGUOUS = "AMBIGUOUS"


@dataclass(frozen=True, kw_only=True)
class EntityMapping(Contract):
    provider_id: str
    namespace: str
    external_id: str
    canonical_value: str
    method: MappingMethod
    review_state: ReviewState
    evidence: str

    def _validate(self) -> None:
        for name in ("provider_id", "namespace", "external_id", "canonical_value", "evidence"):
            require_non_empty(getattr(self, name), name)

    @property
    def key(self) -> tuple[str, str, str]:
        return self.provider_id, self.namespace, self.external_id


@dataclass(frozen=True, kw_only=True)
class Resolution(Contract):
    provider_id: str
    namespace: str
    external_id: str
    status: ResolutionStatus
    canonical_value: str | None
    candidates: tuple[str, ...]

    def _validate(self) -> None:
        if self.candidates != tuple(sorted(set(self.candidates))):
            raise ContractError("NON_CANONICAL_CANDIDATES", "candidates must be unique+sorted")
        expected = {
            ResolutionStatus.UNMAPPED: 0,
            ResolutionStatus.RESOLVED: 1,
        }.get(self.status)
        if expected is not None and len(self.candidates) != expected:
            raise ContractError("RESOLUTION_MISMATCH", f"{self.status} candidate count")
        if self.status is ResolutionStatus.AMBIGUOUS and len(self.candidates) < 2:
            raise ContractError("RESOLUTION_MISMATCH", "AMBIGUOUS needs several candidates")
        if (self.status is ResolutionStatus.RESOLVED) != (self.canonical_value is not None):
            raise ContractError("RESOLUTION_MISMATCH", "only RESOLVED carries a canonical value")


class MappingTable:
    """Immutable set of curated mappings with exact, order-independent resolution."""

    def __init__(self, mappings: Iterable[EntityMapping]) -> None:
        entries = tuple(sorted(mappings, key=lambda m: m.to_json()))
        require_unique(entries, "mappings")
        targets: dict[tuple[str, str, str], set[str]] = defaultdict(set)
        for mapping in entries:
            targets[mapping.key].add(mapping.canonical_value)
        self._entries = entries
        self._targets = {key: tuple(sorted(values)) for key, values in targets.items()}

    @property
    def entries(self) -> tuple[EntityMapping, ...]:
        return self._entries

    def resolve(self, provider_id: str, namespace: str, external_id: str) -> Resolution:
        candidates = self._targets.get((provider_id, namespace, external_id), ())
        if not candidates:
            status = ResolutionStatus.UNMAPPED
        elif len(candidates) == 1:
            status = ResolutionStatus.RESOLVED
        else:
            status = ResolutionStatus.AMBIGUOUS
        return Resolution(
            provider_id=provider_id,
            namespace=namespace,
            external_id=external_id,
            status=status,
            canonical_value=candidates[0] if status is ResolutionStatus.RESOLVED else None,
            candidates=candidates,
        )

    def collisions(self) -> tuple[tuple[str, str, str], ...]:
        """Keys mapped to more than one canonical value (they resolve AMBIGUOUS)."""

        return tuple(sorted(key for key, values in self._targets.items() if len(values) > 1))

    def aliases(self, namespace: str, canonical_value: str) -> tuple[tuple[str, str], ...]:
        """Every (provider, external id) mapped to ``canonical_value`` in ``namespace``."""

        return tuple(
            sorted(
                (m.provider_id, m.external_id)
                for m in self._entries
                if m.namespace == namespace and m.canonical_value == canonical_value
            )
        )
