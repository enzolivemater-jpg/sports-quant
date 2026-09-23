"""Business decision states, their precedence, and the edge invariant.

BLOCKED > REVIEW > WAIT > NO_BET > QUALIFIED. NO_BET is a normal, native result.
Deciding a state (gate sets, gate aggregation, S-Tier) is a later phase.
"""

from __future__ import annotations

from collections.abc import Iterable

from sports_quant.contracts.common import CanonicalEnum, ContractError
from sports_quant.contracts.edge import EdgeAssessment


class DecisionState(CanonicalEnum):
    QUALIFIED = "QUALIFIED"
    WAIT = "WAIT"
    REVIEW = "REVIEW"
    NO_BET = "NO_BET"
    BLOCKED = "BLOCKED"

    @property
    def precedence(self) -> int:
        """Higher value wins when states are combined."""

        return _PRECEDENCE[self]


_PRECEDENCE = {
    DecisionState.QUALIFIED: 0,
    DecisionState.NO_BET: 1,
    DecisionState.WAIT: 2,
    DecisionState.REVIEW: 3,
    DecisionState.BLOCKED: 4,
}


def combine_decision_states(states: Iterable[DecisionState]) -> DecisionState:
    """Apply canonical precedence: return the highest-precedence state.

    The precedence of an empty collection is undefined, so it is rejected.
    """

    collected = tuple(states)
    if not collected:
        raise ContractError("NO_STATES", "at least one decision state is required")
    return max(collected, key=lambda state: state.precedence)


def require_edge_permits_state(state: DecisionState, edge: EdgeAssessment) -> None:
    """Canonical invariant: ``edge_safe < 0`` makes QUALIFIED impossible.

    No stricter positive threshold is implied (OD-06).
    """

    if state is DecisionState.QUALIFIED and edge.edge_safe < 0:
        raise ContractError(
            "NEGATIVE_EDGE_SAFE_CANNOT_QUALIFY", "edge_safe < 0 cannot be QUALIFIED"
        )
