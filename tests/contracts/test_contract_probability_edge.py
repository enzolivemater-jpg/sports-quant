"""Probability bounds, P_safe <= P_calibrated, direct-assignment ban and edge formulas."""

from __future__ import annotations

import dataclasses
import math

import pytest
from contract_builders import probability

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.edge import EdgeAssessment
from sports_quant.contracts.probability import ProbabilityEstimate, ProbabilityProducer


@pytest.mark.parametrize("field", ["p_raw", "p_calibrated", "p_safe"])
@pytest.mark.parametrize("value", [-0.0001, 1.0001, -1.0, 2.0])
def test_probabilities_outside_unit_interval_are_rejected(field: str, value: float) -> None:
    with pytest.raises(ContractError) as excinfo:
        probability(**{field: value})
    assert excinfo.value.code in {"PROBABILITY_OUT_OF_BOUNDS", "P_SAFE_EXCEEDS_CALIBRATED"}


@pytest.mark.parametrize("field", ["p_raw", "p_calibrated", "p_safe"])
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_probabilities_are_rejected(field: str, value: float) -> None:
    with pytest.raises(ContractError) as excinfo:
        probability(**{field: value})
    assert excinfo.value.code == "NON_FINITE_NUMBER"


def test_bounds_are_inclusive() -> None:
    probability(p_raw=0.0, p_calibrated=0.0, p_safe=0.0)
    probability(p_raw=1.0, p_calibrated=1.0, p_safe=1.0)


def test_p_safe_may_equal_but_not_exceed_p_calibrated() -> None:
    assert probability(p_calibrated=0.5, p_safe=0.5).p_safe == 0.5
    with pytest.raises(ContractError) as excinfo:
        probability(p_calibrated=0.5, p_safe=0.5000001)
    assert excinfo.value.code == "P_SAFE_EXCEEDS_CALIBRATED"


def test_p_raw_is_not_ordered_against_calibrated_or_safe() -> None:
    estimate = probability(p_raw=0.1, p_calibrated=0.6, p_safe=0.55)
    assert estimate.p_raw < estimate.p_safe


def test_three_probabilities_remain_distinct_fields() -> None:
    names = {field.name for field in dataclasses.fields(ProbabilityEstimate)}
    assert {"p_raw", "p_calibrated", "p_safe"} <= names


@pytest.mark.parametrize("producer", [ProbabilityProducer.HUMAN, ProbabilityProducer.LLM])
def test_human_or_llm_cannot_assign_final_p_safe(producer: ProbabilityProducer) -> None:
    with pytest.raises(ContractError) as excinfo:
        probability(p_safe_producer=producer)
    assert excinfo.value.code == "P_SAFE_DIRECT_ASSIGNMENT_PROHIBITED"


def test_human_or_llm_p_safe_is_rejected_on_deserialization() -> None:
    payload = probability().to_dict()
    payload["p_safe_producer"] = "LLM"
    with pytest.raises(ContractError):
        ProbabilityEstimate.from_dict(payload)


def test_probability_estimate_is_immutable() -> None:
    estimate = probability()
    with pytest.raises(dataclasses.FrozenInstanceError):
        estimate.p_safe = 0.9  # type: ignore[misc]


def test_edge_formulas() -> None:
    estimate = probability(p_calibrated=0.55, p_safe=0.52)
    edge = EdgeAssessment.from_probabilities(estimate, 0.5)
    assert edge.edge_calibrated == 0.55 - 0.5
    assert edge.edge_safe == 0.52 - 0.5
    assert edge.edge_safe <= edge.edge_calibrated


def test_edge_safe_can_be_negative_while_edge_calibrated_is_positive() -> None:
    edge = EdgeAssessment.from_probabilities(probability(p_calibrated=0.55, p_safe=0.48), 0.5)
    assert edge.edge_calibrated > 0 > edge.edge_safe


@pytest.mark.parametrize("field", ["edge_calibrated", "edge_safe"])
def test_edges_inconsistent_with_formula_are_rejected(field: str) -> None:
    edge = EdgeAssessment.from_probabilities(probability(), 0.5)
    with pytest.raises(ContractError) as excinfo:
        dataclasses.replace(edge, **{field: getattr(edge, field) + 0.01})
    assert excinfo.value.code == "EDGE_FORMULA_MISMATCH"


def test_edge_formula_is_rechecked_on_deserialization() -> None:
    payload = EdgeAssessment.from_probabilities(probability(), 0.5).to_dict()
    payload["edge_safe"] = 0.25
    with pytest.raises(ContractError):
        EdgeAssessment.from_dict(payload)


@pytest.mark.parametrize("value", [-0.01, 1.01])
def test_market_no_vig_probability_must_be_bounded(value: float) -> None:
    with pytest.raises(ContractError):
        EdgeAssessment.from_probabilities(probability(), value)
