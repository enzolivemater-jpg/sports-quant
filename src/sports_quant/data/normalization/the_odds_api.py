"""The Odds API historical odds payload -> typed normalized records.

EXPERIMENTAL adapter for a CANDIDATE historical-odds provider (OD-24 OPEN, not
approved). It parses already-captured bytes only: the repository contains no code
that calls the provider, and live historical ingestion is explicitly blocked
(``docs/research/FOOTBALL_F4_HISTORICAL_ODDS_BLOCK.md``).

Shape follows the documented v4 historical endpoint
(``docs/research/FOOTBALL_ODDS_SNAPSHOT_SCHEMA_MAPPING_v0.1.md``)::

    {"timestamp", "previous_timestamp", "next_timestamp", "data": [event, ...]}

All provider timestamps are kept separately and verbatim; none becomes ``known_at``
here. ``next_timestamp`` is audit metadata only and is not carried into canonical
records. Structural problems fail visibly; a price that is not a number becomes a
``PARSE_ERROR`` value, an absent one ``NOT_PROVIDED_BY_SOURCE`` -- never zero.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sports_quant.contracts.common import Contract, ContractError, instant, require_non_empty
from sports_quant.data.canonical.values import (
    DecimalValue,
    InstantValue,
    ValueState,
    missing_decimal,
    missing_instant,
    observed_decimal,
    observed_instant,
)

PARSER_VERSION = "the-odds-api-historical-v4-1"


@dataclass(frozen=True, kw_only=True)
class OddsApiOutcome(Contract):
    name: str
    price: DecimalValue
    point: float | None


@dataclass(frozen=True, kw_only=True)
class OddsApiMarket(Contract):
    key: str
    last_update: InstantValue
    outcomes: tuple[OddsApiOutcome, ...]


@dataclass(frozen=True, kw_only=True)
class OddsApiBookmaker(Contract):
    key: str
    title: str | None
    last_update: InstantValue
    markets: tuple[OddsApiMarket, ...]


@dataclass(frozen=True, kw_only=True)
class OddsApiEvent(Contract):
    event_id: str
    sport_key: str
    commence_time: datetime
    home_team: str
    away_team: str
    bookmakers: tuple[OddsApiBookmaker, ...]

    def _validate(self) -> None:
        require_non_empty(self.event_id, "event_id")
        if self.home_team == self.away_team:
            raise ContractError("SAME_TEAM_FIXTURE", f"{self.home_team!r} plays itself")


@dataclass(frozen=True, kw_only=True)
class OddsApiHistoricalSnapshot(Contract):
    """One historical response. ``requested_snapshot_at`` comes from the request."""

    requested_snapshot_at: datetime
    provider_snapshot_at: datetime
    previous_snapshot_at: datetime | None
    next_snapshot_at: datetime | None
    events: tuple[OddsApiEvent, ...]

    def _validate(self) -> None:
        # Documented: the closest snapshot at or before the requested date is returned.
        if instant(self.provider_snapshot_at) > instant(self.requested_snapshot_at):
            raise ContractError(
                "SNAPSHOT_AFTER_REQUEST", "provider snapshot is later than the requested date"
            )


def parse_utc(value: object, path: str) -> datetime:
    """Parse a provider ``...Z`` timestamp; anything else is malformed."""

    if not isinstance(value, str) or not value.endswith("Z"):
        raise ContractError("MALFORMED_PAYLOAD", f"{path} must be a UTC '...Z' timestamp")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        raise ContractError("MALFORMED_PAYLOAD", f"{path} is not ISO-8601") from None


def parse_historical_odds(
    payload: bytes, *, requested_snapshot_at: datetime
) -> OddsApiHistoricalSnapshot:
    try:
        document = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError("MALFORMED_PAYLOAD", "payload is not JSON") from exc
    root = _object(document, "$")
    data = root.get("data")
    if not isinstance(data, list):
        raise ContractError("MALFORMED_PAYLOAD", "$.data must be a list")
    return OddsApiHistoricalSnapshot(
        requested_snapshot_at=requested_snapshot_at,
        provider_snapshot_at=parse_utc(root.get("timestamp"), "$.timestamp"),
        previous_snapshot_at=_optional_utc(root.get("previous_timestamp"), "$.previous_timestamp"),
        next_snapshot_at=_optional_utc(root.get("next_timestamp"), "$.next_timestamp"),
        events=tuple(_event(item, f"$.data[{i}]") for i, item in enumerate(data)),
    )


def _event(value: object, path: str) -> OddsApiEvent:
    event = _object(value, path)
    bookmakers = _list(event.get("bookmakers", []), f"{path}.bookmakers")
    return OddsApiEvent(
        event_id=_string(event.get("id"), f"{path}.id"),
        sport_key=_string(event.get("sport_key"), f"{path}.sport_key"),
        commence_time=parse_utc(event.get("commence_time"), f"{path}.commence_time"),
        home_team=_string(event.get("home_team"), f"{path}.home_team"),
        away_team=_string(event.get("away_team"), f"{path}.away_team"),
        bookmakers=tuple(
            _bookmaker(item, f"{path}.bookmakers[{i}]") for i, item in enumerate(bookmakers)
        ),
    )


def _bookmaker(value: object, path: str) -> OddsApiBookmaker:
    bookmaker = _object(value, path)
    title = bookmaker.get("title")
    markets = _list(bookmaker.get("markets", []), f"{path}.markets")
    return OddsApiBookmaker(
        key=_string(bookmaker.get("key"), f"{path}.key"),
        title=_string(title, f"{path}.title") if title is not None else None,
        last_update=_instant_value(bookmaker.get("last_update"), f"{path}.last_update"),
        markets=tuple(_market(item, f"{path}.markets[{i}]") for i, item in enumerate(markets)),
    )


def _market(value: object, path: str) -> OddsApiMarket:
    market = _object(value, path)
    outcomes = _list(market.get("outcomes", []), f"{path}.outcomes")
    return OddsApiMarket(
        key=_string(market.get("key"), f"{path}.key"),
        last_update=_instant_value(market.get("last_update"), f"{path}.last_update"),
        outcomes=tuple(_outcome(item, f"{path}.outcomes[{i}]") for i, item in enumerate(outcomes)),
    )


def _outcome(value: object, path: str) -> OddsApiOutcome:
    outcome = _object(value, path)
    point = outcome.get("point")
    if point is not None and not _is_number(point):
        raise ContractError("MALFORMED_PAYLOAD", f"{path}.point must be a number")
    return OddsApiOutcome(
        name=_string(outcome.get("name"), f"{path}.name"),
        price=_price(outcome.get("price", None)),
        point=float(point) if point is not None else None,
    )


def _price(value: object) -> DecimalValue:
    if value is None:
        return missing_decimal(ValueState.NOT_PROVIDED_BY_SOURCE)
    if _is_number(value):
        return observed_decimal(float(value))  # type: ignore[arg-type]
    return missing_decimal(ValueState.PARSE_ERROR)


def _instant_value(value: object, path: str) -> InstantValue:
    if value is None:
        return missing_instant(ValueState.NOT_PROVIDED_BY_SOURCE)
    try:
        return observed_instant(parse_utc(value, path))
    except ContractError:
        return missing_instant(ValueState.PARSE_ERROR)


def _optional_utc(value: object, path: str) -> datetime | None:
    return None if value is None else parse_utc(value, path)


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _object(value: object, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError("MALFORMED_PAYLOAD", f"{path} must be an object")
    return value


def _list(value: object, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContractError("MALFORMED_PAYLOAD", f"{path} must be a list")
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError("MALFORMED_PAYLOAD", f"{path} must be a non-empty string")
    return value
