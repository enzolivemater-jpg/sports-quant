"""Sports Intelligence claim contract.

A claim's type never implies its verification state (FACT is not VERIFIED), and a
claim can only affect the approved effect channels. There is deliberately no
probability field: no claim, LLM or human interpretation can assign P_safe.
"""

from __future__ import annotations

from dataclasses import dataclass

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    require_non_empty,
    require_unique,
)
from sports_quant.contracts.entity import CanonicalEntityId
from sports_quant.contracts.provenance import Provenance


class ClaimType(CanonicalEnum):
    FACT = "FACT"
    EXPERT_ASSESSMENT = "EXPERT_ASSESSMENT"
    OPINION = "OPINION"
    RUMOR = "RUMOR"
    CONFLICT = "CONFLICT"


class EffectChannel(CanonicalEnum):
    VALIDATED_MODEL_FEATURES = "VALIDATED_MODEL_FEATURES"
    STRUCTURED_CONTEXT = "STRUCTURED_CONTEXT"
    UNCERTAINTY = "UNCERTAINTY"
    REVIEW_STATE = "REVIEW_STATE"
    RESTRICTIONS = "RESTRICTIONS"
    GATES = "GATES"
    NO_BET_REASONS = "NO_BET_REASONS"


@dataclass(frozen=True, kw_only=True)
class SportsIntelligenceClaim(Contract):
    """One structured claim. Verification lives in ``provenance.data_state``."""

    claim_id: str
    claim_type: ClaimType
    subjects: tuple[CanonicalEntityId, ...]
    statement: str
    provenance: Provenance
    effect_channels: tuple[EffectChannel, ...]

    def _validate(self) -> None:
        require_non_empty(self.claim_id, "claim_id")
        require_non_empty(self.statement, "statement")
        require_unique(self.subjects, "subjects")
        require_unique(self.effect_channels, "effect_channels")
