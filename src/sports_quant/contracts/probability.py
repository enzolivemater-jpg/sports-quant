"""Probability contract: P_raw, P_calibrated and P_safe stay distinct.

Invariant: ``0 <= P_safe <= P_calibrated <= 1``. The production P_safe formula is
DEFERRED (OD-01) and is not defined or referenced here.

The ban on human/LLM direct assignment of final P_safe is architectural: this
contract has no override, manual-adjustment or assigned-by field, Sports
Intelligence claims carry no probability, and no effect channel targets P_safe.
Proving which computation produced a value is left to later reproducibility
lineage once the P_safe method exists.
"""

from __future__ import annotations

from dataclasses import dataclass

from sports_quant.contracts.common import (
    Contract,
    ContractError,
    require_non_empty,
    require_probability,
)


@dataclass(frozen=True, kw_only=True)
class ProbabilityEstimate(Contract):
    selection_id: str
    p_raw: float
    p_calibrated: float
    p_safe: float

    def _validate(self) -> None:
        require_non_empty(self.selection_id, "selection_id")
        require_probability(self.p_raw, "p_raw")
        require_probability(self.p_calibrated, "p_calibrated")
        require_probability(self.p_safe, "p_safe")
        if self.p_safe > self.p_calibrated:
            raise ContractError("P_SAFE_EXCEEDS_CALIBRATED", "P_safe must be <= P_calibrated")
