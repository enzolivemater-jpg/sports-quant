"""F4 canonical record invariants: identities, scores, Phase 1 markets, missingness values."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

import pytest

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.data_state import QualityState
from sports_quant.contracts.entity import CanonicalEntityId, EntityKind, ProviderEntityRef, Sport
from sports_quant.contracts.market import MarketFamily
from sports_quant.data.canonical.football import (
    BookmakerRef,
    EventStatus,
    FixtureRecord,
    MatchResultRecord,
    OddsObservationRecord,
    OutcomeKey,
    phase_1_market,
)
from sports_quant.data.canonical.values import (
    IntValue,
    ValueState,
    missing_instant,
    missing_int,
    observed_decimal,
    observed_int,
    quality_state,
)
from sports_quant.data.entity_resolution.football_epl import (
    competition_id,
    league_event_id,
    season_id,
    team_id,
)

SEASON = season_id("ENGLAND_PREMIER_LEAGUE:2024-25")
HOME, AWAY = team_id("ARSENAL"), team_id("FULHAM")
EVENT = league_event_id(SEASON, HOME, AWAY)
KICKOFF = datetime(2024, 8, 17, 14, 0, tzinfo=UTC)


def fixture(**changes: object) -> FixtureRecord:
    base = FixtureRecord(
        event_id=EVENT,
        competition_id=competition_id("ENGLAND_PREMIER_LEAGUE"),
        season_id=SEASON,
        home_team_id=HOME,
        away_team_id=AWAY,
        event_time=KICKOFF,
        matchday=observed_int(1),
        provider_event_ref=ProviderEntityRef(
            provider_id="openfootball", kind=EntityKind.EVENT, external_id="x"
        ),
    )
    return replace(base, **changes)  # type: ignore[arg-type]


def result(**changes: object) -> MatchResultRecord:
    base = MatchResultRecord(
        event_id=EVENT,
        status=EventStatus.COMPLETED,
        home_goals=observed_int(2),
        away_goals=observed_int(2),
        home_ht_goals=observed_int(1),
        away_ht_goals=missing_int(ValueState.NOT_PROVIDED_BY_SOURCE),
        source_published_at=missing_instant(ValueState.UNSUPPORTED_BY_SOURCE),
    )
    return replace(base, **changes)  # type: ignore[arg-type]


def test_valid_records_construct() -> None:
    assert fixture().home_team_id == HOME
    assert result().outcome_1x2() is OutcomeKey.DRAW
    assert result().total_goals() == 4


def test_fixture_identity_kinds_are_enforced() -> None:
    with pytest.raises(ContractError, match="ENTITY_KIND_MISMATCH"):
        fixture(home_team_id=SEASON)
    with pytest.raises(ContractError, match="SAME_TEAM_FIXTURE"):
        fixture(away_team_id=HOME)
    with pytest.raises(ContractError, match="ENTITY_KIND_MISMATCH"):
        fixture(
            provider_event_ref=ProviderEntityRef(
                provider_id="openfootball", kind=EntityKind.TEAM, external_id="x"
            )
        )


def test_fixture_time_must_be_timezone_aware() -> None:
    with pytest.raises(ContractError, match="NAIVE_DATETIME"):
        fixture(event_time=datetime(2024, 8, 17, 15, 0))


@pytest.mark.parametrize(
    ("changes", "code"),
    [
        ({"home_goals": observed_int(-1)}, "IMPOSSIBLE_SCORE"),
        ({"home_ht_goals": observed_int(3)}, "IMPOSSIBLE_SCORE"),
        ({"away_goals": missing_int(ValueState.NOT_YET_PUBLISHED)}, "PARTIAL_SCORE"),
        ({"status": EventStatus.SCHEDULED}, "STATUS_SCORE_MISMATCH"),
    ],
)
def test_result_invariants(changes: dict[str, object], code: str) -> None:
    with pytest.raises(ContractError, match=code):
        result(**changes)


def test_scheduled_result_carries_no_label() -> None:
    pending = missing_int(ValueState.NOT_YET_PUBLISHED)
    scheduled = result(
        status=EventStatus.SCHEDULED,
        home_goals=pending,
        away_goals=pending,
        home_ht_goals=pending,
        away_ht_goals=pending,
    )
    assert (scheduled.outcome_1x2(), scheduled.total_goals()) == (None, None)
    assert result(home_goals=observed_int(0), home_ht_goals=observed_int(0)).outcome_1x2() is (
        OutcomeKey.AWAY
    )


def test_value_present_exactly_when_observed() -> None:
    with pytest.raises(ContractError, match="VALUE_STATE_MISMATCH"):
        IntValue(state=ValueState.OBSERVED, value=None)
    with pytest.raises(ContractError, match="VALUE_STATE_MISMATCH"):
        IntValue(state=ValueState.NOT_PROVIDED_BY_SOURCE, value=0)
    assert observed_int(0).value == 0  # a verified zero is a value, not an absence


@pytest.mark.parametrize(
    ("states", "quality"),
    [
        ((ValueState.OBSERVED, ValueState.UNSUPPORTED_BY_SOURCE), QualityState.VALID),
        ((ValueState.OBSERVED, ValueState.NOT_PROVIDED_BY_SOURCE), QualityState.PARTIAL),
        ((ValueState.NOT_YET_PUBLISHED, ValueState.ENDPOINT_UNAVAILABLE), QualityState.UNAVAILABLE),
        ((ValueState.OBSERVED, ValueState.PARSE_ERROR), QualityState.ERROR),
    ],
)
def test_quality_state_from_value_states(
    states: tuple[ValueState, ...], quality: QualityState
) -> None:
    assert quality_state(states) is quality


def test_phase_1_market_descriptors() -> None:
    one_x_two = phase_1_market(MarketFamily.FOOTBALL_1X2, None)
    assert (one_x_two.market_type, one_x_two.market_instance) == ("1X2_FULL_TIME", "FULL_TIME")
    assert phase_1_market(MarketFamily.FOOTBALL_TOTAL_GOALS_MAIN, 2.25).market_instance == (
        "LINE_2.25"
    )
    for family, line, code in (
        (MarketFamily.FOOTBALL_1X2, 2.5, "UNEXPECTED_LINE"),
        (MarketFamily.FOOTBALL_TOTAL_GOALS_MAIN, None, "INVALID_LINE"),
        (MarketFamily.FOOTBALL_TOTAL_GOALS_MAIN, 2.3, "INVALID_LINE"),
        (MarketFamily.FOOTBALL_TOTAL_GOALS_MAIN, 0.0, "INVALID_LINE"),
        (MarketFamily.FOOTBALL_ASIAN_HANDICAP, None, "NOT_PHASE_1_MARKET"),
        (MarketFamily.FOOTBALL_TEAM_TOTALS, 1.5, "NOT_PHASE_1_MARKET"),
    ):
        with pytest.raises(ContractError, match=code):
            phase_1_market(family, line)


def odds(**changes: object) -> OddsObservationRecord:
    base = OddsObservationRecord(
        event_id=EVENT,
        bookmaker=BookmakerRef(
            provider_id="the_odds_api", external_key="bookie_a", canonical_bookmaker_id="BOOKIE_A"
        ),
        market=phase_1_market(MarketFamily.FOOTBALL_1X2, None),
        outcome=OutcomeKey.HOME,
        line=None,
        decimal_odds=observed_decimal(1.8),
        provider_snapshot_at=KICKOFF,
        requested_snapshot_at=KICKOFF,
        market_last_update_at=missing_instant(ValueState.NOT_PROVIDED_BY_SOURCE),
        bookmaker_last_update_at=missing_instant(ValueState.NOT_PROVIDED_BY_SOURCE),
        provider_outcome_label="Arsenal",
    )
    return replace(base, **changes)  # type: ignore[arg-type]


def test_odds_observation_invariants() -> None:
    with pytest.raises(ContractError, match="OUTCOME_MISMATCH"):
        odds(outcome=OutcomeKey.OVER)
    with pytest.raises(ContractError, match="UNEXPECTED_LINE"):
        odds(line=2.5)
    with pytest.raises(ContractError, match="MARKET_MISMATCH"):
        odds(
            market=phase_1_market(MarketFamily.FOOTBALL_TOTAL_GOALS_MAIN, 2.5),
            outcome=OutcomeKey.OVER,
            line=3.5,
        )
    with pytest.raises(ContractError, match="ENTITY_KIND_MISMATCH"):
        odds(event_id=HOME)


def test_odds_logical_key_is_instant_based() -> None:
    from datetime import timedelta, timezone

    paris = KICKOFF.astimezone(timezone(timedelta(hours=2)))
    assert odds(provider_snapshot_at=paris).logical_key() == odds().logical_key()
    assert (
        odds()
        .logical_key()
        .startswith(
            "FOOTBALL_ODDS:ENGLAND_PREMIER_LEAGUE:2024-25:ARSENAL:FULHAM:BOOKIE_A:FOOTBALL_1X2"
        )
    )


def test_canonical_ids_never_carry_provider_ids() -> None:
    assert (
        CanonicalEntityId(
            sport=Sport.FOOTBALL,
            kind=EntityKind.EVENT,
            value="ENGLAND_PREMIER_LEAGUE:2024-25:ARSENAL:FULHAM",
        )
        == EVENT
    )
