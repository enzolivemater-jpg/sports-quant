"""Decision precedence, negative-edge qualification ban and gate contracts."""

from __future__ import annotations

import dataclasses
import itertools
from datetime import timedelta

import pytest
from contract_builders import CUTOFF, evaluation, gate, probability

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.decision import DecisionState, combine_decision_states
from sports_quant.contracts.edge import EdgeAssessment
from sports_quant.contracts.evaluation import DecisionEvaluation
from sports_quant.contracts.gates import GateResult

ORDER = [
    DecisionState.BLOCKED,
    DecisionState.REVIEW,
    DecisionState.WAIT,
    DecisionState.NO_BET,
    DecisionState.QUALIFIED,
]


def test_precedence_order_is_canonical() -> None:
    assert sorted(DecisionState, key=lambda state: state.precedence, reverse=True) == ORDER


@pytest.mark.parametrize(("higher", "lower"), list(itertools.combinations(ORDER, 2)))
def test_higher_precedence_state_always_wins(higher: DecisionState, lower: DecisionState) -> None:
    assert combine_decision_states([lower, higher]) is higher
    assert combine_decision_states([higher, lower]) is higher


def test_combining_is_order_independent_over_all_permutations() -> None:
    for permutation in itertools.permutations(DecisionState):
        assert combine_decision_states(permutation) is DecisionState.BLOCKED


def test_no_states_never_yield_qualified() -> None:
    with pytest.raises(ContractError) as excinfo:
        combine_decision_states([])
    assert excinfo.value.code == "NO_STATES"


def test_valid_qualified_evaluation() -> None:
    assert evaluation().state is DecisionState.QUALIFIED


def test_negative_edge_safe_cannot_be_qualified() -> None:
    negative = EdgeAssessment.from_probabilities(probability(p_calibrated=0.55, p_safe=0.49), 0.5)
    assert negative.edge_safe < 0
    with pytest.raises(ContractError) as excinfo:
        evaluation(edge=negative)
    assert excinfo.value.code == "NEGATIVE_EDGE_SAFE_CANNOT_QUALIFY"


def test_negative_edge_safe_is_rejected_on_deserialization() -> None:
    payload = evaluation(
        edge=EdgeAssessment.from_probabilities(probability(p_safe=0.49), 0.5),
        state=DecisionState.NO_BET,
        reason_codes=("NEGATIVE_EDGE_SAFE",),
    ).to_dict()
    payload["state"] = "QUALIFIED"
    payload["reason_codes"] = []
    with pytest.raises(ContractError):
        DecisionEvaluation.from_dict(payload)


def test_negative_edge_safe_may_be_no_bet() -> None:
    negative = EdgeAssessment.from_probabilities(probability(p_safe=0.49), 0.5)
    result = evaluation(edge=negative, state=DecisionState.NO_BET, reason_codes=("NEGATIVE_EDGE",))
    assert result.state is DecisionState.NO_BET


def test_zero_edge_safe_is_not_blocked_by_contract() -> None:
    # A stricter positive minimum (OD-06) is deliberately not invented.
    zero = EdgeAssessment.from_probabilities(probability(p_calibrated=0.5, p_safe=0.5), 0.5)
    assert zero.edge_safe == 0
    assert evaluation(edge=zero).state is DecisionState.QUALIFIED


def test_qualified_requires_edge() -> None:
    with pytest.raises(ContractError) as excinfo:
        evaluation(edge=None)
    assert excinfo.value.code == "EDGE_REQUIRED_FOR_QUALIFIED"


@pytest.mark.parametrize("gate_outcome", ORDER[:-1])
def test_state_cannot_be_more_permissive_than_any_gate(gate_outcome: DecisionState) -> None:
    gates = (gate(), gate("DEPENDENCY_GATE", gate_outcome, ("GATE_FAILED",)))
    with pytest.raises(ContractError) as excinfo:
        evaluation(gate_results=gates)
    assert excinfo.value.code == "STATE_MORE_PERMISSIVE_THAN_GATES"
    for state in ORDER:
        if state.precedence >= gate_outcome.precedence:
            evaluation(gate_results=gates, state=state, reason_codes=("GATE_FAILED",))


def test_failed_gate_cannot_be_overridden_by_many_passing_gates() -> None:
    passing = tuple(gate(f"GATE_{index}") for index in range(50))
    blocked = gate("PIT_GATE", DecisionState.BLOCKED, ("PIT_VIOLATION",))
    with pytest.raises(ContractError):
        evaluation(gate_results=(*passing, blocked))


def test_evaluation_requires_at_least_one_gate() -> None:
    with pytest.raises(ContractError) as excinfo:
        evaluation(gate_results=())
    assert excinfo.value.code == "NO_STATES"


def test_non_qualified_decision_requires_reason_code() -> None:
    with pytest.raises(ContractError) as excinfo:
        evaluation(state=DecisionState.NO_BET)
    assert excinfo.value.code == "REASON_CODE_REQUIRED"


def test_gate_cutoff_must_match_evaluation_cutoff() -> None:
    other_cutoff = dataclasses.replace(gate(), decision_cutoff_at=CUTOFF - timedelta(hours=1))
    with pytest.raises(ContractError) as excinfo:
        evaluation(gate_results=(other_cutoff,))
    assert excinfo.value.code == "GATE_CUTOFF_MISMATCH"


def test_duplicate_gate_ids_are_rejected() -> None:
    with pytest.raises(ContractError):
        evaluation(gate_results=(gate(), gate()))


def test_evaluation_snapshot_is_immutable() -> None:
    result = evaluation()
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.state = DecisionState.BLOCKED  # type: ignore[misc]


def test_gate_result_serialization_round_trip() -> None:
    result = gate("DATA_QUALITY_GATE", DecisionState.REVIEW, ("OPEN_CONFLICT", "STALE_LINEUP"))
    payload = result.to_dict()
    assert payload == {
        "gate_id": "DATA_QUALITY_GATE",
        "outcome": "REVIEW",
        "reason_codes": ["OPEN_CONFLICT", "STALE_LINEUP"],
        "evidence": [{"key": "snapshot", "reference": "snapshot:1"}],
        "evaluated_at": "2026-09-20T17:55:00+00:00",
        "decision_cutoff_at": "2026-09-20T18:00:00+00:00",
    }
    assert GateResult.from_dict(payload) == result
    assert GateResult.from_json(result.to_json()) == result


def test_non_qualified_gate_requires_reason_code() -> None:
    with pytest.raises(ContractError) as excinfo:
        gate(outcome=DecisionState.NO_BET)
    assert excinfo.value.code == "REASON_CODE_REQUIRED"


@pytest.mark.parametrize("bad", ["lower_case", "WITH SPACE", "1LEADING_DIGIT", "", "DASH-ED"])
def test_reason_codes_and_gate_ids_must_be_deterministic_identifiers(bad: str) -> None:
    with pytest.raises(ContractError) as excinfo:
        gate(outcome=DecisionState.NO_BET, reason_codes=(bad,))
    assert excinfo.value.code == "INVALID_REASON_CODE"
    with pytest.raises(ContractError):
        gate(gate_id=bad)


def test_gate_contract_has_no_score_or_threshold_fields() -> None:
    names = {field.name for field in dataclasses.fields(GateResult)}
    assert not {name for name in names if "score" in name or "threshold" in name}
