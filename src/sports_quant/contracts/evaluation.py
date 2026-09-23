"""Immutable decision evaluation snapshot.

Kept separate from ``decision`` because it depends on ``gates``, which itself
depends on ``decision``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import (
    Contract,
    ContractError,
    require_non_empty,
    require_reason_code,
    require_unique,
)
from sports_quant.contracts.decision import DecisionState, combine_decision_states
from sports_quant.contracts.edge import EdgeAssessment
from sports_quant.contracts.gates import GateResult
from sports_quant.contracts.market import MarketDescriptor
from sports_quant.contracts.reproducibility import ReproducibilityRef


@dataclass(frozen=True, kw_only=True)
class DecisionEvaluation(Contract):
    """The decision for one market selection at one cutoff.

    ``state`` can never be more permissive than any gate outcome, QUALIFIED requires
    an edge assessment, and ``edge_safe < 0`` makes QUALIFIED impossible.
    """

    evaluation_id: str
    market: MarketDescriptor
    decision_cutoff_at: datetime
    evaluated_at: datetime
    edge: EdgeAssessment | None
    gate_results: tuple[GateResult, ...]
    state: DecisionState
    reason_codes: tuple[str, ...]
    reproducibility: ReproducibilityRef

    def _validate(self) -> None:
        require_non_empty(self.evaluation_id, "evaluation_id")
        for code in self.reason_codes:
            require_reason_code(code, "reason_codes")
        require_unique(self.reason_codes, "reason_codes")
        require_unique(tuple(gate.gate_id for gate in self.gate_results), "gate ids")

        for gate in self.gate_results:
            if gate.decision_cutoff_at is not None and gate.decision_cutoff_at != (
                self.decision_cutoff_at
            ):
                raise ContractError(
                    "GATE_CUTOFF_MISMATCH",
                    f"gate {gate.gate_id} was evaluated for a different decision cutoff",
                )

        gate_state = combine_decision_states(gate.outcome for gate in self.gate_results)
        if self.state.precedence < gate_state.precedence:
            raise ContractError(
                "STATE_MORE_PERMISSIVE_THAN_GATES",
                f"state {self.state} cannot override gate outcome {gate_state}",
            )
        if self.state is not DecisionState.QUALIFIED and not self.reason_codes:
            raise ContractError(
                "REASON_CODE_REQUIRED", "a non-QUALIFIED decision requires a reason code"
            )

        if self.state is DecisionState.QUALIFIED:
            if self.edge is None:
                raise ContractError(
                    "EDGE_REQUIRED_FOR_QUALIFIED", "QUALIFIED requires an edge assessment"
                )
            if self.edge.edge_safe < 0:
                raise ContractError(
                    "NEGATIVE_EDGE_SAFE_CANNOT_QUALIFY", "edge_safe < 0 cannot be QUALIFIED"
                )
