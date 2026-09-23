"""The four data-state axes stay independent."""

from __future__ import annotations

import dataclasses
import itertools

import pytest
from contract_builders import data_state

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.data_state import (
    ConflictState,
    DataState,
    FreshnessState,
    QualityState,
    VerificationState,
)


def test_data_state_has_exactly_four_separate_axes() -> None:
    assert [field.name for field in dataclasses.fields(DataState)] == [
        "quality",
        "freshness",
        "verification",
        "conflict",
    ]


def test_every_combination_of_axes_is_representable() -> None:
    combinations = list(
        itertools.product(QualityState, FreshnessState, VerificationState, ConflictState)
    )
    assert len(combinations) == 4 * 5 * 4 * 3
    for quality, freshness, verification, conflict in combinations:
        state = DataState(
            quality=quality, freshness=freshness, verification=verification, conflict=conflict
        )
        assert DataState.from_json(state.to_json()) == state


def test_changing_one_axis_never_changes_another() -> None:
    base = data_state()
    changed = dataclasses.replace(base, conflict=ConflictState.OPEN)
    assert (changed.quality, changed.freshness, changed.verification) == (
        base.quality,
        base.freshness,
        base.verification,
    )


def test_axis_value_sets_are_disjoint() -> None:
    axes = [QualityState, FreshnessState, VerificationState, ConflictState]
    values = [value for axis in axes for value in (member.value for member in axis)]
    assert len(values) == len(set(values))


@pytest.mark.parametrize(
    ("field", "wrong"),
    [
        ("quality", FreshnessState.LIVE),
        ("freshness", VerificationState.UNVERIFIED),
        ("freshness", ConflictState.OPEN),
        ("verification", QualityState.VALID),
        ("conflict", "OPEN"),
    ],
)
def test_an_axis_rejects_values_of_another_axis(field: str, wrong: object) -> None:
    with pytest.raises(ContractError) as excinfo:
        data_state(**{field: wrong})
    assert excinfo.value.code == "INVALID_TYPE"


def test_conflict_and_unverified_are_not_freshness_states() -> None:
    freshness_values = {member.value for member in FreshnessState}
    assert "CONFLICT" not in freshness_values
    assert "UNVERIFIED" not in freshness_values
