"""Explicit provider-local time conversion; DST ambiguity is never guessed."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from sports_quant.contracts.common import ContractError
from sports_quant.data.point_in_time.timezones import localize_provider_time


@pytest.mark.parametrize(
    ("wall", "zone", "expected"),
    [
        (datetime(2024, 8, 16, 20, 0), "Europe/London", datetime(2024, 8, 16, 19, 0, tzinfo=UTC)),
        (datetime(2024, 12, 16, 20, 0), "Europe/London", datetime(2024, 12, 16, 20, 0, tzinfo=UTC)),
        (datetime(2024, 8, 16, 20, 0), "Europe/Paris", datetime(2024, 8, 16, 18, 0, tzinfo=UTC)),
        (datetime(2024, 8, 16, 20, 0), "America/New_York", datetime(2024, 8, 17, 0, 0, tzinfo=UTC)),
        (datetime(2024, 8, 16, 20, 0), "UTC", datetime(2024, 8, 16, 20, 0, tzinfo=UTC)),
    ],
)
def test_unambiguous_local_times_convert_to_utc(
    wall: datetime, zone: str, expected: datetime
) -> None:
    result = localize_provider_time(wall, zone)
    assert result == expected
    assert result.tzinfo is UTC


@pytest.mark.parametrize(
    ("wall", "zone"),
    [
        (datetime(2024, 10, 27, 1, 30), "Europe/London"),  # fall-back: occurs twice
        (datetime(2024, 3, 31, 1, 30), "Europe/London"),  # spring-forward: never occurs
        (datetime(2024, 11, 3, 1, 30), "America/New_York"),
        (datetime(2024, 3, 10, 2, 30), "America/New_York"),
    ],
)
def test_ambiguous_or_nonexistent_local_times_are_rejected(wall: datetime, zone: str) -> None:
    with pytest.raises(ContractError) as excinfo:
        localize_provider_time(wall, zone)
    assert excinfo.value.code == "INVALID_TIMEZONE"


@pytest.mark.parametrize("zone", ["Not/AZone", "", "../etc/passwd"])
def test_unknown_zone_is_rejected(zone: str) -> None:
    with pytest.raises(ContractError) as excinfo:
        localize_provider_time(datetime(2024, 8, 16, 20, 0), zone)
    assert excinfo.value.code == "INVALID_TIMEZONE"


def test_aware_input_is_rejected_rather_than_reinterpreted() -> None:
    with pytest.raises(ContractError) as excinfo:
        localize_provider_time(datetime(2024, 8, 16, 20, 0, tzinfo=UTC), "Europe/London")
    assert excinfo.value.code == "INVALID_TIMEZONE"
