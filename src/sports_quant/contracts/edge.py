"""Edge contract.

``edge_calibrated = P_calibrated - P_market_no_vig`` and
``edge_safe = P_safe - P_market_no_vig``. No-vig computation (OD-07) and any
stricter positive edge threshold (OD-06) are out of scope.
"""

from __future__ import annotations

from dataclasses import dataclass

from sports_quant.contracts.common import Contract, ContractError, require_probability
from sports_quant.contracts.probability import ProbabilityEstimate


@dataclass(frozen=True, kw_only=True)
class EdgeAssessment(Contract):
    probability: ProbabilityEstimate
    p_market_no_vig: float
    edge_calibrated: float
    edge_safe: float

    @classmethod
    def from_probabilities(
        cls, probability: ProbabilityEstimate, p_market_no_vig: float
    ) -> EdgeAssessment:
        return cls(
            probability=probability,
            p_market_no_vig=p_market_no_vig,
            edge_calibrated=probability.p_calibrated - p_market_no_vig,
            edge_safe=probability.p_safe - p_market_no_vig,
        )

    def _validate(self) -> None:
        require_probability(self.p_market_no_vig, "p_market_no_vig")
        if self.edge_calibrated != self.probability.p_calibrated - self.p_market_no_vig:
            raise ContractError(
                "EDGE_FORMULA_MISMATCH",
                "edge_calibrated must equal P_calibrated - P_market_no_vig",
            )
        if self.edge_safe != self.probability.p_safe - self.p_market_no_vig:
            raise ContractError(
                "EDGE_FORMULA_MISMATCH", "edge_safe must equal P_safe - P_market_no_vig"
            )
