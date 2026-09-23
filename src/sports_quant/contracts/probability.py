"""Probability contract: P_raw, P_calibrated and P_safe stay distinct.

Invariant: ``0 <= P_safe <= P_calibrated <= 1``. The production P_safe formula is
DEFERRED (OD-01) and is not defined here; ``p_safe_method`` only references it.
"""

from __future__ import annotations

from dataclasses import dataclass

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    require_non_empty,
    require_probability,
)
from sports_quant.contracts.reproducibility import ArtifactRef


class ProbabilityProducer(CanonicalEnum):
    """Who produced a probability value. Only SYSTEM_PIPELINE may produce P_safe."""

    SYSTEM_PIPELINE = "SYSTEM_PIPELINE"
    HUMAN = "HUMAN"
    LLM = "LLM"


@dataclass(frozen=True, kw_only=True)
class ProbabilityEstimate(Contract):
    selection_id: str
    p_raw: float
    p_calibrated: float
    p_safe: float
    p_safe_producer: ProbabilityProducer
    p_safe_method: ArtifactRef

    def _validate(self) -> None:
        require_non_empty(self.selection_id, "selection_id")
        require_probability(self.p_raw, "p_raw")
        require_probability(self.p_calibrated, "p_calibrated")
        require_probability(self.p_safe, "p_safe")
        if self.p_safe > self.p_calibrated:
            raise ContractError("P_SAFE_EXCEEDS_CALIBRATED", "P_safe must be <= P_calibrated")
        if self.p_safe_producer is not ProbabilityProducer.SYSTEM_PIPELINE:
            raise ContractError(
                "P_SAFE_DIRECT_ASSIGNMENT_PROHIBITED",
                f"final P_safe cannot be assigned by {self.p_safe_producer}",
            )
