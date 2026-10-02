"""F4 provider normalization: OpenFootball and (synthetic) The Odds API payloads."""

from __future__ import annotations

import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType

import pytest
from football_builders import (
    HEADER,
    MATCHDAY_1,
    REQUESTED_AT,
    SNAPSHOT_AT,
    bookmaker,
    h2h,
    odds_event,
    odds_payload,
    season_text,
)

from sports_quant.contracts.common import ContractError
from sports_quant.data.canonical.values import ValueState
from sports_quant.data.normalization.openfootball import (
    LINE_FORMAT_LEGACY,
    LINE_FORMAT_MODERN,
    parse_season_file,
)
from sports_quant.data.normalization.the_odds_api import parse_historical_odds

LONDON = "Europe/London"


def parse(payload: bytes, zone: str = LONDON):  # type: ignore[no-untyped-def]
    return parse_season_file(payload, timezone_name=zone)


# -- OpenFootball -----------------------------------------------------------------


def test_openfootball_parse_keeps_source_labels_and_scores() -> None:
    season = parse(season_text())
    assert (season.title, season.season_label) == ("English Premier League 2024/25", "2024/25")
    first = season.matches[0]
    assert (first.home_label, first.away_label) == ("Manchester United FC", "Fulham FC")
    assert (first.home_goals, first.away_goals, first.home_ht_goals) == (1, 0, 0)
    assert first.line_format == LINE_FORMAT_MODERN
    assert len(season.matches) == 4


def test_openfootball_kickoff_is_inherited_within_a_date_only() -> None:
    season = parse(season_text())
    everton = season.matches[3]
    assert everton.kickoff_local == "15:00"
    bad = season_text(
        MATCHDAY_1 + "  Sun Aug 18\n           Chelsea FC  v Manchester City FC  0-2\n"
    )
    with pytest.raises(ContractError, match="MISSING_KICKOFF_TIME"):
        parse(bad)


def test_event_times_are_timezone_aware_utc_instants() -> None:
    season = parse(season_text())
    first = season.matches[0]
    assert first.event_time == datetime(2024, 8, 16, 19, 0, tzinfo=UTC)  # 20:00 BST
    assert first.event_time.utcoffset() is not None
    assert first.date_local == "2024-08-16" and first.timezone_name == LONDON


def test_ambiguous_dst_kickoff_is_rejected_not_guessed() -> None:
    body = "\n▪ Matchday 1\n  Sun Oct 27 2024\n    01:30  Arsenal FC  v Fulham FC  1-0\n"
    with pytest.raises(ContractError, match="INVALID_TIMEZONE"):
        parse(season_text(body))


def test_unknown_timezone_is_rejected() -> None:
    with pytest.raises(ContractError, match="INVALID_TIMEZONE"):
        parse(season_text(), zone="Mars/Olympus")


def test_unplayed_fixture_has_no_score() -> None:
    body = MATCHDAY_1 + "  Sat Aug 24\n    15:00  Fulham FC  v Leicester City FC\n"
    fixture = parse(season_text(body)).matches[-1]
    assert (fixture.home_goals, fixture.away_goals, fixture.home_ht_goals) == (None, None, None)


def test_legacy_line_format_is_supported() -> None:
    text = (
        "= English Premier League 2000/01\n\n"
        "# Date       Sat Aug 19 2000 - Sat May 19 2001 (273d)\n\n"
        "▪ Matchday 1\nSat Aug 19\n  15:00  Charlton Athletic   4-0 (2-0)  Manchester City\n"
    )
    match = parse(text.encode()).matches[0]
    assert (match.home_label, match.away_label, match.line_format) == (
        "Charlton Athletic",
        "Manchester City",
        LINE_FORMAT_LEGACY,
    )
    assert match.date_local == "2000-08-19"


@pytest.mark.parametrize(
    ("payload", "code"),
    [
        (b"", "MISSING_TITLE"),
        (b"\xff\xfe", "PAYLOAD_NOT_UTF8"),
        (season_text(MATCHDAY_1 + "    this is not a fixture line\n"), "MALFORMED_LINE"),
        (season_text(MATCHDAY_1 + "  Sat Aug 18\n"), "WEEKDAY_MISMATCH"),
        (season_text(MATCHDAY_1 + "  Fri Feb 30\n"), "INVALID_DATE"),
        (
            season_text(
                MATCHDAY_1
                + "  Sat Aug 24\n    15:00  Arsenal FC  v Wolverhampton Wanderers FC  1-1\n"
            ),
            "DUPLICATE_FIXTURE",
        ),
        (
            season_text(MATCHDAY_1 + "  Sat Aug 24\n    15:00  Fulham FC  v Fulham FC  1-1\n"),
            "SAME_TEAM_FIXTURE",
        ),
        (
            season_text("\n  Fri Aug 16 2024\n    20:00  Arsenal FC  v Fulham FC  1-0\n"),
            "MATCH_BEFORE_MATCHDAY",
        ),
        (season_text(MATCHDAY_1, header=HEADER), "MATCH_COUNT_MISMATCH"),
        (
            season_text(MATCHDAY_1 + "    25:00  Chelsea FC  v Manchester City FC  0-2\n"),
            "INVALID_TIME",
        ),
    ],
)
def test_malformed_openfootball_payload_fails_visibly(payload: bytes, code: str) -> None:
    with pytest.raises(ContractError, match=code):
        parse(payload)


RESEARCH_PARSER = (
    Path(__file__).resolve().parents[2] / "scripts" / "research" / "parse_openfootball_results.py"
)


def _research_parser() -> ModuleType:
    spec = importlib.util.spec_from_file_location("parse_openfootball_results", RESEARCH_PARSER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_production_parser_agrees_with_research_parser() -> None:
    payload = season_text()
    research = _research_parser().parse_openfootball(payload.decode(), timezone_name=LONDON)
    production = parse(payload).matches
    assert [
        (
            r["event_time_utc"],
            r["home_team"],
            r["away_team"],
            r["home_goals"],
            r["away_goals"],
            r["home_ht_goals"],
            r["away_ht_goals"],
            r["matchday"],
            r["source_line_number"],
        )
        for r in research
    ] == [
        (
            m.event_time.isoformat().replace("+00:00", "Z"),
            m.home_label,
            m.away_label,
            m.home_goals,
            m.away_goals,
            m.home_ht_goals,
            m.away_ht_goals,
            m.matchday,
            m.line_number,
        )
        for m in production
    ]


# -- The Odds API (synthetic payloads) ------------------------------------------


def test_odds_api_parse_keeps_every_provider_timestamp_separately() -> None:
    snapshot = parse_historical_odds(odds_payload(), requested_snapshot_at=REQUESTED_AT)
    assert snapshot.provider_snapshot_at == SNAPSHOT_AT
    assert snapshot.requested_snapshot_at == REQUESTED_AT
    assert snapshot.next_snapshot_at is not None and snapshot.previous_snapshot_at is not None
    event = snapshot.events[0]
    assert event.event_id == "synthetic-event-0001"
    market = event.bookmakers[0].markets[0]
    assert market.last_update.state is ValueState.OBSERVED
    assert [o.price.value for o in market.outcomes] == [1.5, 4.2, 6.5]


def test_odds_price_missing_or_unparseable_is_never_zero() -> None:
    payload = odds_payload(odds_event(bookmaker("bookie_a", h2h(home=None, draw="4,2"))))
    outcomes = parse_historical_odds(payload, requested_snapshot_at=REQUESTED_AT).events[0]
    prices = [o.price for o in outcomes.bookmakers[0].markets[0].outcomes]
    assert [p.state for p in prices] == [
        ValueState.NOT_PROVIDED_BY_SOURCE,
        ValueState.PARSE_ERROR,
        ValueState.OBSERVED,
    ]
    assert prices[0].value is None and prices[1].value is None


def test_snapshot_later_than_requested_is_rejected() -> None:
    with pytest.raises(ContractError, match="SNAPSHOT_AFTER_REQUEST"):
        parse_historical_odds(odds_payload(), requested_snapshot_at=SNAPSHOT_AT.replace(minute=0))


@pytest.mark.parametrize(
    "document",
    [
        "not json",
        "[]",
        '{"timestamp": "2024-08-16T17:57:00Z"}',
        '{"timestamp": "2024-08-16T17:57:00+01:00", "data": []}',
        '{"timestamp": "2024-08-16T17:57:00Z", "data": [{"id": "e"}]}',
        '{"timestamp": "2024-08-16T17:57:00Z", "data": [{"id": "e", "sport_key": "s",'
        ' "commence_time": "2024-08-16T19:00:00Z", "home_team": "A", "away_team": "B",'
        ' "bookmakers": [{"key": "k", "markets": [{"key": "h2h", "outcomes":'
        ' [{"name": "A", "price": 2, "point": "x"}]}]}]}]}',
    ],
)
def test_malformed_odds_payload_fails_visibly(document: str) -> None:
    with pytest.raises(ContractError, match="MALFORMED_PAYLOAD"):
        parse_historical_odds(document.encode(), requested_snapshot_at=REQUESTED_AT)


def test_odds_payload_is_valid_json_shape() -> None:
    document = json.loads(odds_payload())
    assert set(document) == {"timestamp", "previous_timestamp", "next_timestamp", "data"}
