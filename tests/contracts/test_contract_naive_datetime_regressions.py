"""Regression (F3 review P1-01): ``instant`` must fail closed on naive datetimes.

``instant`` used ``value.astimezone(UTC)``, which reads a naive datetime in the host's
local timezone. Called directly, ``require_critical_known_at`` then accepted a naive
``decision_cutoff_at`` and its result depended on the machine's timezone.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone, tzinfo
from zoneinfo import ZoneInfo

import pytest
from contract_builders import temporal

from sports_quant.contracts.common import ContractError, instant
from sports_quant.contracts.time import require_critical_known_at

NAIVE = datetime(2024, 8, 16, 12, 0)
KNOWN = datetime(2024, 8, 16, 10, 0, tzinfo=UTC)


class _NoOffset(tzinfo):
    """A tzinfo whose ``utcoffset`` is None: the datetime is naive for Python."""

    def utcoffset(self, dt: datetime | None) -> timedelta | None:
        return None

    def dst(self, dt: datetime | None) -> timedelta | None:
        return None


@pytest.mark.parametrize("value", [NAIVE, NAIVE.replace(tzinfo=_NoOffset())])
def test_instant_rejects_naive_datetimes(value: datetime) -> None:
    with pytest.raises(ContractError) as excinfo:
        instant(value)
    assert excinfo.value.code == "NAIVE_DATETIME"


def test_instant_rejects_non_datetimes() -> None:
    with pytest.raises(ContractError) as excinfo:
        instant("2024-08-16T12:00:00+00:00")  # type: ignore[arg-type]
    assert excinfo.value.code == "INVALID_TYPE"


@pytest.mark.parametrize(
    "value",
    [
        datetime(2024, 8, 16, 14, 0, tzinfo=timezone(timedelta(hours=2))),
        datetime(2024, 8, 16, 13, 0, tzinfo=ZoneInfo("Europe/London")),
        datetime(2024, 8, 16, 8, 0, tzinfo=ZoneInfo("America/New_York")),
    ],
)
def test_instant_converts_aware_non_utc_datetimes(value: datetime) -> None:
    converted = instant(value)
    assert converted == datetime(2024, 8, 16, 12, 0, tzinfo=UTC)
    assert converted.tzinfo is UTC


def test_require_critical_known_at_rejects_naive_cutoff() -> None:
    record = temporal(received_at=KNOWN, known_at=KNOWN)
    with pytest.raises(ContractError) as excinfo:
        require_critical_known_at(record, NAIVE)
    assert excinfo.value.code == "NAIVE_DATETIME"


def test_naive_cutoff_is_rejected_before_missing_known_at() -> None:
    record = temporal(received_at=KNOWN, known_at=None, known_at_basis=None)
    with pytest.raises(ContractError) as excinfo:
        require_critical_known_at(record, NAIVE)
    assert excinfo.value.code == "NAIVE_DATETIME"


def test_require_critical_known_at_accepts_aware_non_utc_cutoff() -> None:
    record = temporal(received_at=KNOWN, known_at=KNOWN)
    require_critical_known_at(record, datetime(2024, 8, 16, 20, 0, tzinfo=ZoneInfo("Asia/Tokyo")))
    with pytest.raises(ContractError) as excinfo:
        # 11:00 in UTC+02:00 is 09:00Z, before known_at.
        require_critical_known_at(
            record, datetime(2024, 8, 16, 11, 0, tzinfo=timezone(timedelta(hours=2)))
        )
    assert excinfo.value.code == "KNOWN_AT_AFTER_CUTOFF"
