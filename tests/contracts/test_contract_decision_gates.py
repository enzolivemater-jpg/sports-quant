"""Decision precedence, the negative-edge invariant and the gate contract surface.

F2 defines no qualification engine: no gate sets, no gate aggregation, no
critical-gate policy and no thresholds.
"""

from __future__ import annotations

import dataclasses
import importlib.util
import itertools

import pytest
from contract_builders import gate, probability

from sports_quant.contracts import gates
from sports_quant.contracts.common import ContractError
from sports_quant.contracts.decision import (
    DecisionState,
    combine_decision_states,
    require_edge_permits_state,
)
from sports_quant.contracts.edge import EdgeAssessment
from sports_quant.contracts.gates import GateResult

ORDER = [
    DecisionState.BLOCKED,
    DecisionState.REVIEW,
    DecisionState.WAIT,
    DecisionState.NO_BET,
    DecisionState.QUALIFIED,
]


def _edge(p_safe: float, p_market_no_vig: float = 0.5) -> EdgeAssessment:
    return EdgeAssessment.from_probabilities(
        probability(p_calibrated=max(p_safe, 0.55), p_safe=p_safe), p_market_no_vig
    )


def test_precedence_order_is_canonical() -> None:
    assert sorted(DecisionState, key=lambda state: state.precedence, reverse=True) == ORDER


@pytest.mark.parametrize(("higher", "lower"), list(itertools.combinations(ORDER, 2)))
def test_higher_precedence_state_always_wins(higher: DecisionState, lower: DecisionState) -> None:
    assert combine_decision_states([lower, higher]) is higher
    assert combine_decision_states([higher, lower]) is higher


def test_combining_is_order_independent_over_all_permutations() -> None:
    for permutation in itertools.permutations(DecisionState):
        assert combine_decision_states(permutation) is DecisionState.BLOCKED


def test_precedence_of_no_states_is_undefined() -> None:
    with pytest.raises(ContractError) as excinfo:
        combine_decision_states([])
    assert excinfo.value.code == "NO_STATES"


def test_negative_edge_safe_cannot_be_qualified() -> None:
    negative = _edge(p_safe=0.49)
    assert negative.edge_safe < 0
    with pytest.raises(ContractError) as excinfo:
        require_edge_permits_state(DecisionState.QUALIFIED, negative)
    assert excinfo.value.code == "NEGATIVE_EDGE_SAFE_CANNOT_QUALIFY"


def test_negative_edge_safe_cannot_qualify_even_when_edge_calibrated_is_positive() -> None:
    edge = _edge(p_safe=0.48)
    assert edge.edge_calibrated > 0 > edge.edge_safe
    with pytest.raises(ContractError):
        require_edge_permits_state(DecisionState.QUALIFIED, edge)


@pytest.mark.parametrize("state", ORDER[:-1])
def test_negative_edge_safe_permits_every_non_qualified_state(state: DecisionState) -> None:
    require_edge_permits_state(state, _edge(p_safe=0.49))


def test_zero_edge_safe_is_not_blocked_by_contract() -> None:
    # A stricter positive minimum (OD-06) is deliberately not invented.
    zero = _edge(p_safe=0.5)
    assert zero.edge_safe == 0
    require_edge_permits_state(DecisionState.QUALIFIED, zero)


def test_positive_edge_safe_does_not_force_qualified() -> None:
    # edge_safe >= 0 is necessary, not sufficient: every state stays representable.
    for state in DecisionState:
        require_edge_permits_state(state, _edge(p_safe=0.54))


def test_no_decision_evaluation_engine_exists_in_f2() -> None:
    assert importlib.util.find_spec("sports_quant.contracts.evaluation") is None


def test_gates_module_defines_no_aggregation_or_gate_policy() -> None:
    public = {name.lower() for name in dir(gates) if not name.startswith("_")}
    for forbidden in ("combine", "aggregate", "mandatory", "critical", "threshold", "score"):
        assert not {name for name in public if forbidden in name}, forbidden


def test_gate_contract_has_no_score_threshold_or_criticality_fields() -> None:
    names = {field.name for field in dataclasses.fields(GateResult)}
    assert names == {
        "gate_id",
        "outcome",
        "reason_codes",
        "evidence",
        "evaluated_at",
        "decision_cutoff_at",
    }


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


def test_gate_result_without_cutoff_round_trips() -> None:
    result = dataclasses.replace(gate(), decision_cutoff_at=None)
    assert GateResult.from_json(result.to_json()) == result


@pytest.mark.parametrize("outcome", list(DecisionState))
def test_gate_outcome_uses_canonical_decision_states(outcome: DecisionState) -> None:
    reasons = () if outcome is DecisionState.QUALIFIED else ("REASON",)
    assert GateResult.from_json(gate(outcome=outcome, reason_codes=reasons).to_json()).outcome is (
        outcome
    )
    payload = gate().to_dict()
    payload["outcome"] = "PASS"
    with pytest.raises(ContractError):
        GateResult.from_dict(payload)


def test_non_qualified_gate_requires_reason_code() -> None:
    with pytest.raises(ContractError) as excinfo:
        gate(outcome=DecisionState.NO_BET)
    assert excinfo.value.code == "REASON_CODE_REQUIRED"


@pytest.mark.parametrize("bad", ["lower_case", "WITH SPACE", "1LEADING_DIGIT", "", "DASH-ED"])
def test_reason_codes_and_gate_ids_must_be_deterministic_identifiers(bad: str) -> None:
    with pytest.raises(ContractError) as excinfo:
        gate(outcome=DecisionState.NO_BET, reason_codes=(bad,))
    assert excinfo.value.code == "INVALID_IDENTIFIER"
    with pytest.raises(ContractError):
        gate(gate_id=bad)


def test_duplicate_reason_codes_are_rejected() -> None:
    with pytest.raises(ContractError):
        gate(outcome=DecisionState.NO_BET, reason_codes=("A", "A"))
