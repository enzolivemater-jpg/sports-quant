"""F4 raw -> normalized -> canonical build: mapping, lineage, missingness, odds, conflicts."""

from __future__ import annotations

from datetime import timedelta

import pytest
from football_builders import (
    MATCHDAY_1,
    MUFC_FULHAM_KICKOFF,
    SNAPSHOT_AT,
    T1,
    T2,
    bookmaker,
    build,
    h2h,
    odds_capture,
    odds_event,
    odds_payload,
    odds_test_mappings,
    of_capture,
    season_text,
    totals,
)

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.data_state import ConflictState, FreshnessState, QualityState
from sports_quant.contracts.entity import EntityKind
from sports_quant.contracts.market import MarketFamily
from sports_quant.contracts.time import KnownAtBasis
from sports_quant.data.canonical.football import (
    EventStatus,
    MatchResultRecord,
    OddsObservationRecord,
    OutcomeKey,
    phase_1_market,
)
from sports_quant.data.canonical.values import ValueState, missing_int, observed_int
from sports_quant.data.ingestion.football import (
    CanonicalObservation,
    FootballBuild,
    RecordKind,
    detect_conflicts,
)

MUFC_FULHAM = "ENGLAND_PREMIER_LEAGUE:2024-25:MANCHESTER_UNITED:FULHAM"


def results(b: FootballBuild) -> dict[str, MatchResultRecord]:
    return {o.result.event_id.value: o.result for o in b.observations if o.result is not None}


def odds(b: FootballBuild) -> list[OddsObservationRecord]:
    return [o.odds for o in b.observations if o.odds is not None]


def issue_codes(b: FootballBuild) -> set[str]:
    return {issue.code for issue in b.issues}


# -- normalized -> canonical ------------------------------------------------------


def test_openfootball_maps_to_canonical_fixtures_and_results() -> None:
    b = build(of_capture(season_text()))
    kinds = [o.kind for o in b.observations]
    assert kinds.count(RecordKind.FIXTURE) == kinds.count(RecordKind.RESULT) == 4
    fixture = next(o.fixture for o in b.observations if o.fixture is not None)
    assert fixture.competition_id.value == "ENGLAND_PREMIER_LEAGUE"
    assert fixture.season_id.value == "ENGLAND_PREMIER_LEAGUE:2024-25"
    assert fixture.home_team_id.kind is EntityKind.TEAM
    result = results(b)[MUFC_FULHAM]
    assert result.status is EventStatus.COMPLETED
    assert (result.outcome_1x2(), result.total_goals()) == (OutcomeKey.HOME, 1)
    assert not b.issues and not b.unresolved and not b.conflicts


def test_provider_external_ids_are_preserved() -> None:
    b = build(of_capture(season_text()))
    fixture = next(
        o.fixture for o in b.observations if o.fixture and o.fixture.event_id.value == MUFC_FULHAM
    )
    assert fixture.provider_event_ref.provider_id == "openfootball"
    assert fixture.provider_event_ref.external_id == (
        "English Premier League 2024/25|Manchester United FC|Fulham FC"
    )
    pit = next(o.pit_record for o in b.observations if o.fixture is fixture)
    assert pit.provenance.external_id == fixture.provider_event_ref.external_id
    odds_build = build(of_capture(season_text()), odds_capture())
    observation = odds(odds_build)[0]
    assert observation.bookmaker.external_key == "bookie_a"
    assert observation.provider_outcome_label in {"Manchester United", "Draw", "Fulham"}


def test_raw_lineage_is_preserved_on_every_record() -> None:
    raw, payload = of_capture(season_text())
    b = build((raw, payload))
    assert b.capture_ids == (raw.capture_id,)
    for observation in b.observations:
        pit = observation.pit_record
        assert observation.capture_id == raw.capture_id
        assert pit.raw_snapshot == raw.snapshot_ref()
        assert pit.revision_id == raw.source_revision
        assert pit.provenance.source.source_version == raw.source_revision
        assert pit.payload_sha256 == observation.payload().content_digest()


def test_known_at_is_system_receipt_only_and_records_are_critical() -> None:
    b = build(of_capture(season_text(), received_at=T1), odds_capture(received_at=T2))
    for observation in b.observations:
        temporal = observation.pit_record.provenance.temporal
        assert temporal.known_at_basis is KnownAtBasis.SYSTEM_RECEIPT
        assert temporal.known_at == temporal.received_at
        assert temporal.published_at is None
        assert observation.pit_record.provenance.critical
    # Provider snapshot time is data, never known_at.
    observation = next(o for o in b.observations if o.odds is not None)
    assert observation.odds is not None
    assert observation.pit_record.provenance.temporal.known_at == T2 != SNAPSHOT_AT


def test_data_state_axes_are_explicit_and_conflicts_are_not_collapsed_into_them() -> None:
    b = build(of_capture(season_text()))
    states = {o.pit_record.provenance.data_state for o in b.observations}
    assert {s.freshness for s in states} == {FreshnessState.DELAYED}
    assert {s.conflict for s in states} == {ConflictState.NONE}


# -- entity resolution -------------------------------------------------------------


def test_entity_mapping_is_deterministic_and_order_independent() -> None:
    a = build(of_capture(season_text(), received_at=T1), of_capture(season_text(), received_at=T2))
    b = build(of_capture(season_text(), received_at=T2), of_capture(season_text(), received_at=T1))
    assert a == b
    events = {o.fixture.event_id for o in a.observations if o.fixture is not None}
    assert len(events) == 4  # two captures of one file: versions, not new fixtures


def test_unmapped_team_is_reported_not_guessed() -> None:
    body = MATCHDAY_1 + "  Sat Aug 24\n    15:00  Leeds United FC  v Fulham FC  1-1\n"
    b = build(of_capture(season_text(body)))
    assert "UNMAPPED_TEAM" in issue_codes(b) and "FIXTURE_NOT_CANONICALIZED" in issue_codes(b)
    assert [r.external_id for r in b.unresolved] == ["Leeds United FC"]
    assert len(results(b)) == 4  # the other fixtures are unaffected


def test_name_variants_are_not_fuzzy_matched() -> None:
    body = MATCHDAY_1 + "  Sat Aug 24\n    15:00  Arsenal  v Fulham FC  1-1\n"
    b = build(of_capture(season_text(body)))
    assert [r.external_id for r in b.unresolved] == ["Arsenal"]


def test_ambiguous_mapping_blocks_the_record() -> None:
    from sports_quant.data.entity_resolution.mapping import (
        EntityMapping,
        MappingMethod,
        ResolutionStatus,
        ReviewState,
    )

    clash = EntityMapping(
        provider_id="openfootball",
        namespace="TEAM",
        external_id="Fulham FC",
        canonical_value="FULHAM_WOMEN",
        method=MappingMethod.CURATED_ALIAS,
        review_state=ReviewState.CURATED_PENDING_REVIEW,
        evidence="synthetic collision",
    )
    b = build(of_capture(season_text()), mappings=odds_test_mappings(clash))
    (ambiguous,) = b.unresolved
    assert ambiguous.status is ResolutionStatus.AMBIGUOUS
    assert ambiguous.candidates == ("FULHAM", "FULHAM_WOMEN")
    assert MUFC_FULHAM not in results(b)
    assert "AMBIGUOUS_TEAM" in issue_codes(b)


def test_unmapped_season_blocks_the_whole_file() -> None:
    text = season_text().replace(b"2024/25", b"2025/26")
    b = build(of_capture(text))
    assert not b.observations
    assert "UNMAPPED_SEASON" in issue_codes(b)


# -- missingness ---------------------------------------------------------------------


def test_missing_half_time_score_is_not_zero() -> None:
    b = build(of_capture(season_text()))
    everton = results(b)["ENGLAND_PREMIER_LEAGUE:2024-25:EVERTON:BRIGHTON_AND_HOVE_ALBION"]
    assert everton.home_ht_goals == missing_int(ValueState.NOT_PROVIDED_BY_SOURCE)
    assert everton.home_ht_goals.value is None
    pit = next(o.pit_record for o in b.observations if o.result is everton)
    assert pit.provenance.data_state.quality is QualityState.PARTIAL


def test_verified_zero_remains_zero() -> None:
    b = build(of_capture(season_text()))
    mufc = results(b)[MUFC_FULHAM]
    assert mufc.away_goals == observed_int(0)
    assert mufc.home_ht_goals == observed_int(0)
    pit = next(o.pit_record for o in b.observations if o.result is mufc)
    assert pit.provenance.data_state.quality is QualityState.VALID


def test_unplayed_fixture_result_is_not_yet_published() -> None:
    body = MATCHDAY_1 + "  Sat Aug 24\n    15:00  Fulham FC  v Liverpool FC\n"
    b = build(of_capture(season_text(body)))
    pending = results(b)["ENGLAND_PREMIER_LEAGUE:2024-25:FULHAM:LIVERPOOL"]
    assert pending.status is EventStatus.SCHEDULED
    assert pending.home_goals == missing_int(ValueState.NOT_YET_PUBLISHED)
    assert (pending.outcome_1x2(), pending.total_goals()) == (None, None)
    pit = next(o.pit_record for o in b.observations if o.result is pending)
    assert pit.provenance.data_state.quality is QualityState.UNAVAILABLE


def test_unsupported_field_is_explicit() -> None:
    b = build(of_capture(season_text()))
    for result in results(b).values():
        assert result.source_published_at.state is ValueState.UNSUPPORTED_BY_SOURCE
        assert result.source_published_at.value is None


def test_endpoint_unavailable_is_a_visible_gap() -> None:
    raw, payload = odds_capture(b'{"message": "quota exceeded"}', http_status=429)
    b = build(of_capture(season_text()), (raw, payload))
    (gap,) = b.gaps
    assert (gap.state, gap.http_status, gap.capture_id) == (
        ValueState.ENDPOINT_UNAVAILABLE,
        429,
        raw.capture_id,
    )
    assert not odds(b)


def test_impossible_score_is_rejected() -> None:
    with pytest.raises(ContractError, match="IMPOSSIBLE_SCORE"):
        MatchResultRecord(
            event_id=results(build(of_capture(season_text())))[MUFC_FULHAM].event_id,
            status=EventStatus.COMPLETED,
            home_goals=observed_int(1),
            away_goals=observed_int(0),
            home_ht_goals=observed_int(2),
            away_ht_goals=observed_int(0),
            source_published_at=results(build(of_capture(season_text())))[
                MUFC_FULHAM
            ].source_published_at,
        )


# -- odds plumbing (synthetic payloads; live leg blocked) -------------------------------


def test_odds_map_to_phase_1_markets_by_label_not_array_order() -> None:
    reordered = h2h()
    reordered["outcomes"] = list(reversed(reordered["outcomes"]))
    b = build(
        of_capture(season_text()),
        odds_capture(odds_payload(odds_event(bookmaker("bookie_a", reordered, totals())))),
    )
    by_outcome = {o.outcome: o for o in odds(b)}
    assert set(by_outcome) == {
        OutcomeKey.HOME,
        OutcomeKey.DRAW,
        OutcomeKey.AWAY,
        OutcomeKey.OVER,
        OutcomeKey.UNDER,
    }
    assert by_outcome[OutcomeKey.HOME].decimal_odds.value == 1.5
    assert by_outcome[OutcomeKey.AWAY].provider_outcome_label == "Fulham"
    assert by_outcome[OutcomeKey.OVER].market.market_instance == "LINE_2.5"
    assert {o.event_id.value for o in odds(b)} == {MUFC_FULHAM}


def test_odds_keep_bookmaker_and_snapshot_granularity() -> None:
    later = SNAPSHOT_AT + timedelta(minutes=5)
    first = odds_capture(odds_payload(odds_event(bookmaker("bookie_a"), bookmaker("bookie_b"))))
    second = odds_capture(
        odds_payload(odds_event(bookmaker("bookie_a", h2h(home=1.45))), snapshot_at=later),
        requested_at=later,
    )
    b = build(of_capture(season_text()), first, second)
    home = [o for o in odds(b) if o.outcome is OutcomeKey.HOME]
    keys = {(o.bookmaker.canonical_bookmaker_id, o.provider_snapshot_at) for o in home}
    assert keys == {("BOOKIE_A", SNAPSHOT_AT), ("BOOKIE_B", SNAPSHOT_AT), ("BOOKIE_A", later)}
    assert {o.decimal_odds.value for o in home if o.provider_snapshot_at == later} == {1.45}
    assert len({o.logical_key() for o in home}) == 3


def test_market_and_bookmaker_update_times_are_kept_separately() -> None:
    b = build(of_capture(season_text()), odds_capture())
    observation = odds(b)[0]
    assert observation.market_last_update_at.state is ValueState.OBSERVED
    assert observation.bookmaker_last_update_at.state is ValueState.OBSERVED
    assert observation.market_last_update_at != observation.bookmaker_last_update_at
    assert observation.requested_snapshot_at > observation.provider_snapshot_at


def test_next_snapshot_navigation_never_enters_canonical_records() -> None:
    b = build(of_capture(season_text()), odds_capture())
    next_at = (SNAPSHOT_AT + timedelta(minutes=5)).isoformat()
    for observation in b.observations:
        assert next_at not in observation.payload().to_json()
        assert next_at not in observation.pit_record.to_json()
    assert "next" not in " ".join(OddsObservationRecord.__dataclass_fields__)


def test_phase_2_and_unknown_markets_are_not_mapped() -> None:
    spreads = {"key": "spreads", "outcomes": [{"name": "Fulham", "price": 1.9, "point": 1.5}]}
    b = build(
        of_capture(season_text()),
        odds_capture(odds_payload(odds_event(bookmaker("bookie_a", spreads)))),
    )
    assert not odds(b) and "NOT_PHASE_1_MARKET" in issue_codes(b)
    with pytest.raises(ContractError, match="NOT_PHASE_1_MARKET"):
        phase_1_market(MarketFamily.FOOTBALL_BTTS, None)


def test_multiple_totals_lines_are_never_merged_into_main() -> None:
    two_lines = totals()
    two_lines["outcomes"] += [
        {"name": "Over", "price": 2.5, "point": 3.5},
        {"name": "Under", "price": 1.5, "point": 3.5},
    ]
    b = build(
        of_capture(season_text()),
        odds_capture(odds_payload(odds_event(bookmaker("bookie_a", two_lines)))),
    )
    assert not odds(b)
    assert "MAIN_LINE_UNRESOLVED" in issue_codes(b)
    assert "DUPLICATE_OUTCOME" not in issue_codes(b)


def test_totals_without_line_are_not_mapped() -> None:
    no_point = totals()
    for outcome in no_point["outcomes"]:
        del outcome["point"]
    b = build(
        of_capture(season_text()),
        odds_capture(odds_payload(odds_event(bookmaker("bookie_a", no_point)))),
    )
    assert not odds(b) and "MAIN_LINE_UNRESOLVED" in issue_codes(b)


def test_duplicate_and_unrecognized_outcomes_are_reported() -> None:
    duplicated = h2h()
    duplicated["outcomes"].append({"name": "Draw", "price": 4.0})
    extra = h2h()
    extra["outcomes"].append({"name": "Fulham or Draw", "price": 1.2})
    b = build(
        of_capture(season_text()),
        odds_capture(odds_payload(odds_event(bookmaker("bookie_a", duplicated)))),
        odds_capture(
            odds_payload(odds_event(bookmaker("bookie_b", extra))), received_at=T2 + timedelta(1)
        ),
    )
    assert {"DUPLICATE_OUTCOME", "UNRECOGNIZED_OUTCOME"} <= issue_codes(b)
    assert "INCOMPLETE_1X2" not in issue_codes(b)  # bookie_b's 1X2 set is complete
    assert {o.bookmaker.canonical_bookmaker_id for o in odds(b)} == {"BOOKIE_B"}


def test_incomplete_1x2_is_flagged() -> None:
    partial = h2h()
    partial["outcomes"] = partial["outcomes"][:2]
    b = build(
        of_capture(season_text()),
        odds_capture(odds_payload(odds_event(bookmaker("bookie_a", partial)))),
    )
    assert "INCOMPLETE_1X2" in issue_codes(b)
    assert {o.outcome for o in odds(b)} == {OutcomeKey.HOME, OutcomeKey.DRAW}


def test_unparseable_and_impossible_prices_are_kept_as_errors_not_zero() -> None:
    market = h2h(home="abc", away=0.95)
    b = build(
        of_capture(season_text()),
        odds_capture(odds_payload(odds_event(bookmaker("bookie_a", market)))),
    )
    by_outcome = {o.odds.outcome: o for o in b.observations if o.odds is not None}
    home = by_outcome[OutcomeKey.HOME]
    assert home.odds is not None and home.odds.decimal_odds.state is ValueState.PARSE_ERROR
    assert home.pit_record.provenance.data_state.quality is QualityState.ERROR
    away = by_outcome[OutcomeKey.AWAY]
    assert away.pit_record.provenance.data_state.quality is QualityState.ERROR
    assert {"ODDS_PRICE_PARSE_ERROR", "ODDS_NOT_ABOVE_ONE"} <= issue_codes(b)


def test_odds_event_needs_an_exactly_matching_fixture() -> None:
    moved = odds_capture(
        odds_payload(odds_event(bookmaker(), commence=MUFC_FULHAM_KICKOFF + timedelta(hours=1)))
    )
    b = build(of_capture(season_text()), moved)
    assert not odds(b) and "EVENT_FIXTURE_UNMATCHED" in issue_codes(b)
    no_fixtures = build(odds_capture())
    assert not odds(no_fixtures) and "EVENT_FIXTURE_UNMATCHED" in issue_codes(no_fixtures)


def test_unmapped_bookmaker_is_reported() -> None:
    b = build(
        of_capture(season_text()),
        odds_capture(odds_payload(odds_event(bookmaker("bookie_zz")))),
    )
    assert not odds(b) and "UNMAPPED_BOOKMAKER" in issue_codes(b)


def test_odds_capture_without_requested_date_fails_visibly() -> None:
    raw, payload = odds_capture()
    data = raw.to_dict()
    data["request_parameters"] = [p for p in data["request_parameters"] if p["name"] != "date"]
    stripped = type(raw).from_dict(data)
    with pytest.raises(ContractError, match="MISSING_REQUESTED_DATE"):
        build(of_capture(season_text()), (stripped, payload))


# -- duplicates and conflicts ------------------------------------------------------------


def test_duplicate_capture_and_duplicate_observations_collapse() -> None:
    capture_ = of_capture(season_text())
    once = build(capture_)
    twice = build(capture_, capture_)
    assert once == twice


def test_conflicting_observations_of_one_version_are_all_retained() -> None:
    a = odds_capture(received_at=T2)
    corrected_prices = odds_payload(odds_event(bookmaker("bookie_a", h2h(home=1.55), totals())))
    b_ = odds_capture(corrected_prices, received_at=T2 + timedelta(hours=1))
    b = build(of_capture(season_text()), a, b_)
    conflict_keys = {c.logical_key for c in b.conflicts}
    home = [o for o in odds(b) if o.outcome is OutcomeKey.HOME]
    assert {o.decimal_odds.value for o in home} == {1.5, 1.55}  # both retained
    assert {o.logical_key() for o in home} <= conflict_keys
    conflict = next(c for c in b.conflicts if c.logical_key == home[0].logical_key())
    assert {m.capture_id for m in conflict.observations} == {a[0].capture_id, b_[0].capture_id}


def test_cross_source_disagreement_is_a_conflict_and_agreement_is_not() -> None:
    observation = next(o for o in build(of_capture(season_text())).observations if o.result)
    agreeing = _from_other_source(observation)
    assert detect_conflicts([observation, agreeing]) == ()
    disagreeing = _with_home_goals(agreeing, 9)
    (conflict,) = detect_conflicts([observation, disagreeing])
    assert conflict.logical_key == observation.pit_record.logical_key
    assert {m.source_id for m in conflict.observations} == {"openfootball", "the_odds_api"}
    assert len({m.payload_sha256 for m in conflict.observations}) == 2


def _from_other_source(observation: CanonicalObservation) -> CanonicalObservation:
    data = observation.to_dict()
    data["capture_id"] = "other-capture"
    data["pit_record"]["provenance"]["source"]["source_id"] = "the_odds_api"
    data["pit_record"]["raw_snapshot"]["source_id"] = "the_odds_api"
    return CanonicalObservation.from_dict(data)


def _with_home_goals(observation: CanonicalObservation, goals: int) -> CanonicalObservation:
    data = observation.to_dict()
    data["result"]["home_goals"] = {"state": "OBSERVED", "value": goals}
    data["pit_record"]["payload_sha256"] = MatchResultRecord.from_dict(
        data["result"]
    ).content_digest()
    return CanonicalObservation.from_dict(data)
