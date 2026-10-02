"""Regression: temporal comparisons must be instant-based inside a DST fall-back hour.

Defect found during F3: Python compares aware datetimes sharing one ``tzinfo`` object
by wall time and ignores ``fold``. On 2024-10-27 Europe/London repeats 01:00-02:00,
so ``01:15 (fold=1, GMT) > 01:45 (fold=0, BST)`` evaluated False although it is 30
minutes later, and F2 accepted a record known after the cutoff.
"""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest
from contract_builders import assessment, temporal

from sports_quant.contracts.common import ContractError, instant
from sports_quant.contracts.predictability import EvaluationPeriod, require_successor
from sports_quant.contracts.time import (
    CriticalInformationUse,
    require_critical_known_at,
)

LONDON = ZoneInfo("Europe/London")
# Second 01:15 (GMT) = 01:15Z; first 01:45 (BST) = 00:45Z.
LATE_GMT = datetime(2024, 10, 27, 1, 15, fold=1, tzinfo=LONDON)
EARLY_BST = datetime(2024, 10, 27, 1, 45, fold=0, tzinfo=LONDON)
# Same wall time, one hour apart.
FIRST_0130 = datetime(2024, 10, 27, 1, 30, fold=0, tzinfo=LONDON)
SECOND_0130 = datetime(2024, 10, 27, 1, 30, fold=1, tzinfo=LONDON)


def test_fixture_really_exercises_the_wall_time_comparison_trap() -> None:
    assert instant(LATE_GMT) > instant(EARLY_BST)
    assert not LATE_GMT > EARLY_BST  # Python's same-tzinfo comparison is wrong here
    assert FIRST_0130 == SECOND_0130  # and here
    assert instant(FIRST_0130) != instant(SECOND_0130)


def test_known_after_cutoff_inside_fold_is_rejected() -> None:
    record = temporal(received_at=LATE_GMT, known_at=LATE_GMT)
    with pytest.raises(ContractError) as excinfo:
        CriticalInformationUse(temporal=record, decision_cutoff_at=EARLY_BST)
    assert excinfo.value.code == "KNOWN_AT_AFTER_CUTOFF"
    with pytest.raises(ContractError):
        require_critical_known_at(record, EARLY_BST)


def test_known_before_cutoff_inside_fold_is_accepted() -> None:
    record = temporal(received_at=EARLY_BST, known_at=EARLY_BST)
    CriticalInformationUse(temporal=record, decision_cutoff_at=LATE_GMT)


def test_system_receipt_equality_is_instant_based_inside_fold() -> None:
    with pytest.raises(ContractError) as excinfo:
        temporal(received_at=FIRST_0130, known_at=SECOND_0130)
    assert excinfo.value.code == "KNOWN_AT_RECEIPT_MISMATCH"
    temporal(received_at=FIRST_0130, known_at=FIRST_0130.astimezone(UTC))


def test_validity_window_order_is_instant_based_inside_fold() -> None:
    with pytest.raises(ContractError) as excinfo:
        temporal(valid_from=LATE_GMT, valid_to=EARLY_BST)
    assert excinfo.value.code == "INVALID_VALIDITY_WINDOW"
    temporal(valid_from=EARLY_BST, valid_to=LATE_GMT)


def test_evaluation_period_order_is_instant_based_inside_fold() -> None:
    with pytest.raises(ContractError):
        EvaluationPeriod(start=LATE_GMT, end=EARLY_BST)


def test_assessment_known_at_before_period_end_inside_fold_is_rejected() -> None:
    with pytest.raises(ContractError) as excinfo:
        assessment(
            evaluation_period=EvaluationPeriod(
                start=datetime(2024, 1, 1, tzinfo=UTC), end=LATE_GMT
            ),
            known_at=EARLY_BST,
        )
    assert excinfo.value.code == "KNOWN_AT_BEFORE_EVALUATION_END"


def test_successor_known_at_regression_inside_fold_is_rejected() -> None:
    period = EvaluationPeriod(start=datetime(2024, 1, 1, tzinfo=UTC), end=EARLY_BST)
    previous = assessment(evaluation_period=period, known_at=LATE_GMT)
    successor = dataclasses.replace(previous, assessment_version=2, known_at=EARLY_BST)
    with pytest.raises(ContractError) as excinfo:
        require_successor(previous, successor)
    assert excinfo.value.code == "ASSESSMENT_KNOWN_AT_REGRESSION"
