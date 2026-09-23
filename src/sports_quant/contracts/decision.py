"""Business decision states and their precedence.

BLOCKED > REVIEW > WAIT > NO_BET > QUALIFIED. NO_BET is a normal, native result.
"""

from __future__ import annotations

from collections.abc import Iterable

from sports_quant.contracts.common import CanonicalEnum, ContractError


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
    """Return the highest-precedence state.

    An empty input is rejected: absence of evaluations never yields QUALIFIED.
    """

    collected = tuple(states)
    if not collected:
        raise ContractError("NO_STATES", "at least one decision state is required")
    return max(collected, key=lambda state: state.precedence)
