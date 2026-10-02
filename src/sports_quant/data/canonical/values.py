"""Explicit missingness for canonical field values.

A canonical value is either ``OBSERVED`` (with its value, which may legitimately be
zero) or carries the reason it is absent. Absence is never encoded as zero, an empty
string or an implicit default.

The F2 ``DataState`` axes are not redefined: ``quality_state`` only derives the F2
``QualityState`` of a record from the states of its values.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import CanonicalEnum, Contract, ContractError
from sports_quant.contracts.data_state import QualityState


class ValueState(CanonicalEnum):
    OBSERVED = "OBSERVED"
    NOT_PROVIDED_BY_SOURCE = "NOT_PROVIDED_BY_SOURCE"
    ENDPOINT_UNAVAILABLE = "ENDPOINT_UNAVAILABLE"
    UNSUPPORTED_BY_SOURCE = "UNSUPPORTED_BY_SOURCE"
    NOT_YET_PUBLISHED = "NOT_YET_PUBLISHED"
    PARSE_ERROR = "PARSE_ERROR"


def _require_value_iff_observed(state: ValueState, value: object) -> None:
    if (state is ValueState.OBSERVED) != (value is not None):
        raise ContractError(
            "VALUE_STATE_MISMATCH", "a value is present exactly when its state is OBSERVED"
        )


@dataclass(frozen=True, kw_only=True)
class IntValue(Contract):
    state: ValueState
    value: int | None

    def _validate(self) -> None:
        _require_value_iff_observed(self.state, self.value)


@dataclass(frozen=True, kw_only=True)
class DecimalValue(Contract):
    state: ValueState
    value: float | None

    def _validate(self) -> None:
        _require_value_iff_observed(self.state, self.value)


@dataclass(frozen=True, kw_only=True)
class InstantValue(Contract):
    state: ValueState
    value: datetime | None

    def _validate(self) -> None:
        _require_value_iff_observed(self.state, self.value)


def observed_int(value: int) -> IntValue:
    return IntValue(state=ValueState.OBSERVED, value=value)


def missing_int(state: ValueState) -> IntValue:
    return IntValue(state=state, value=None)


def observed_decimal(value: float) -> DecimalValue:
    return DecimalValue(state=ValueState.OBSERVED, value=value)


def missing_decimal(state: ValueState) -> DecimalValue:
    return DecimalValue(state=state, value=None)


def observed_instant(value: datetime) -> InstantValue:
    return InstantValue(state=ValueState.OBSERVED, value=value)


def missing_instant(state: ValueState) -> InstantValue:
    return InstantValue(state=state, value=None)


def quality_state(states: Iterable[ValueState]) -> QualityState:
    """F2 ``QualityState`` of a record from the states of the values it should carry.

    ``UNSUPPORTED_BY_SOURCE`` values are ignored: a source that never supplies a field
    does not degrade every record it produces. Any ``PARSE_ERROR`` is ``ERROR``; all
    remaining values observed is ``VALID``, none observed ``UNAVAILABLE``, otherwise
    ``PARTIAL``.
    """

    relevant = [state for state in states if state is not ValueState.UNSUPPORTED_BY_SOURCE]
    if ValueState.PARSE_ERROR in relevant:
        return QualityState.ERROR
    observed = sum(1 for state in relevant if state is ValueState.OBSERVED)
    if observed == len(relevant):
        return QualityState.VALID
    if observed == 0:
        return QualityState.UNAVAILABLE
    return QualityState.PARTIAL
