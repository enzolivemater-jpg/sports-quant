"""Explicit conversion of provider-local wall times to UTC instants.

F2 contracts only accept timezone-aware datetimes. Providers that publish local wall
times must be converted here, naming the IANA zone explicitly. Wall times that are
ambiguous (DST fall-back) or nonexistent (DST spring-forward) are rejected rather
than guessed.
"""

from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sports_quant.contracts.common import ContractError


def localize_provider_time(local_wall_time: datetime, zone: str) -> datetime:
    """Return the UTC instant of a naive provider-local wall time in IANA ``zone``."""

    if local_wall_time.tzinfo is not None:
        raise ContractError(
            "INVALID_TIMEZONE", "expected a naive provider-local wall time and an explicit zone"
        )
    try:
        tz = ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ContractError("INVALID_TIMEZONE", f"unknown IANA zone {zone!r}") from exc
    earlier = local_wall_time.replace(tzinfo=tz, fold=0)
    later = local_wall_time.replace(tzinfo=tz, fold=1)
    if earlier.utcoffset() != later.utcoffset():
        raise ContractError(
            "INVALID_TIMEZONE",
            f"{local_wall_time.isoformat()} is ambiguous or nonexistent in {zone}",
        )
    return earlier.astimezone(UTC)
