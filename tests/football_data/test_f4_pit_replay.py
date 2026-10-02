"""F4 through F3: corrections as versions, PIT replay, deterministic rebuild."""

from __future__ import annotations

import random
from datetime import timedelta
from pathlib import Path

import pytest
from football_builders import (
    CODE,
    DATASET,
    MATCHDAY_1,
    SNAPSHOT_AT,
    T1,
    T2,
    bookmaker,
    build,
    context,
    h2h,
    odds_capture,
    odds_event,
    odds_payload,
    of_capture,
    season_text,
    totals,
)

from sports_quant.contracts.common import ContractError
from sports_quant.data.canonical.values import observed_int
from sports_quant.data.ingestion.dataset import (
    FootballPitDataset,
    build_manifest,
    materialize_football,
)
from sports_quant.data.ingestion.football import CaptureMode, FootballBuild, build_football
from sports_quant.data.point_in_time.manifest import verify_replay
from sports_quant.data.point_in_time.selection import RecordDisposition
from sports_quant.data.snapshots.store import RawSnapshotStore

MUFC_FULHAM = "ENGLAND_PREMIER_LEAGUE:2024-25:MANCHESTER_UNITED:FULHAM"
ORIGINAL = season_text()
CORRECTED = season_text(MATCHDAY_1.replace("1-0 (0-0)", "2-1 (0-0)"))


def at(b: FootballBuild, cutoff) -> FootballPitDataset:  # type: ignore[no-untyped-def]
    return materialize_football(
        b, decision_cutoff_at=cutoff, code_version=CODE, dataset_ref=DATASET, created_at=T2
    )


def mufc(dataset: FootballPitDataset):  # type: ignore[no-untyped-def]
    (result,) = [r for r in dataset.results if r.event_id.value == MUFC_FULHAM]
    return result


def test_correction_creates_a_new_version_and_keeps_the_old_one() -> None:
    b = build(of_capture(ORIGINAL, received_at=T1), of_capture(CORRECTED, received_at=T2))
    versions = [
        o for o in b.observations if o.result is not None and o.result.event_id.value == MUFC_FULHAM
    ]
    assert len(versions) == 2
    assert len({o.pit_record.revision_id for o in versions}) == 2
    assert {o.result.home_goals.value for o in versions if o.result} == {1, 2}
    assert not b.conflicts  # different revisions of one source are corrections


def test_f3_excludes_a_revision_first_known_after_the_cutoff() -> None:
    b = build(of_capture(ORIGINAL, received_at=T1), of_capture(CORRECTED, received_at=T2))
    before_correction = at(b, T2 - timedelta(seconds=1))
    after_correction = at(b, T2)
    assert mufc(before_correction).home_goals == observed_int(1)
    assert mufc(after_correction).home_goals == observed_int(2)
    later = [
        d
        for d in before_correction.manifest.body.record_decisions
        if d.known_at == T2 and d.logical_key.endswith(MUFC_FULHAM)
    ]
    assert later and all(d.disposition is RecordDisposition.REJECTED for d in later)


def test_later_revision_does_not_change_an_earlier_replay() -> None:
    original_only = build(of_capture(ORIGINAL, received_at=T1))
    with_correction = build(
        of_capture(ORIGINAL, received_at=T1), of_capture(CORRECTED, received_at=T2)
    )
    cutoff = T2 - timedelta(seconds=1)
    before, after = at(original_only, cutoff), at(with_correction, cutoff)
    assert (before.fixtures, before.results, before.odds) == (
        after.fixtures,
        after.results,
        after.odds,
    )
    selected = lambda d: {  # noqa: E731
        (o.logical_key, o.selected_record_digest) for o in d.manifest.body.key_outcomes
    }
    assert selected(before) == selected(after)
    verify_replay(before.manifest, original_only.pit_records())


def test_nothing_is_usable_before_receipt_fail_closed() -> None:
    b = build(of_capture(ORIGINAL, received_at=T1))
    dataset = at(b, T1 - timedelta(microseconds=1))
    assert (dataset.fixtures, dataset.results, dataset.odds) == ((), (), ())
    assert len(dataset.no_eligible_keys) == len(b.observations)
    assert at(b, T1).results  # usable from the receipt instant on


def test_historical_cutoff_never_sees_retrospectively_captured_data() -> None:
    """A 2024 cutoff cannot use data SPORTS QUANT received in 2026 (no guessed known_at)."""

    b = build(of_capture(ORIGINAL, received_at=T1), odds_capture(received_at=T2))
    dataset = at(b, SNAPSHOT_AT + timedelta(minutes=1))
    assert (dataset.fixtures, dataset.results, dataset.odds) == ((), (), ())


def test_odds_snapshots_are_separate_logical_records_in_replay() -> None:
    later = SNAPSHOT_AT + timedelta(minutes=5)
    b = build(
        of_capture(ORIGINAL, received_at=T1),
        odds_capture(received_at=T2),
        odds_capture(
            odds_payload(
                odds_event(bookmaker("bookie_a", h2h(home=1.45), totals())), snapshot_at=later
            ),
            requested_at=later,
            received_at=T2 + timedelta(hours=1),
        ),
    )
    first_only = at(b, T2 + timedelta(minutes=30))
    both = at(b, T2 + timedelta(hours=1))
    assert {o.provider_snapshot_at for o in first_only.odds} == {SNAPSHOT_AT}
    assert {o.provider_snapshot_at for o in both.odds} == {SNAPSHOT_AT, later}


def test_conflicting_version_is_unresolved_in_f3_not_arbitrated() -> None:
    corrected_prices = odds_payload(odds_event(bookmaker("bookie_a", h2h(home=1.55), totals())))
    b = build(
        of_capture(ORIGINAL, received_at=T1),
        odds_capture(received_at=T2),
        odds_capture(corrected_prices, received_at=T2 + timedelta(hours=1)),
    )
    dataset = at(b, T2 + timedelta(hours=2))
    (conflict,) = b.conflicts  # only the HOME price differs between the two captures
    assert conflict.logical_key in dataset.unresolved_keys
    assert "HOME" not in {o.outcome.value for o in dataset.odds}  # neither price is chosen
    assert {o.outcome.value for o in dataset.odds} == {"DRAW", "AWAY", "OVER", "UNDER"}


def test_record_dropped_by_a_later_revision_is_reported_not_applied() -> None:
    everton = "           Everton FC              v Brighton & Hove Albion FC  0-3\n"
    dropped = season_text(MATCHDAY_1.replace(everton, ""))
    b = build(of_capture(ORIGINAL, received_at=T1), of_capture(dropped, received_at=T2))
    absent = {i.subject for i in b.issues if i.code == "RECORD_ABSENT_IN_LATER_REVISION"}
    key = "ENGLAND_PREMIER_LEAGUE:2024-25:EVERTON:BRIGHTON_AND_HOVE_ALBION"
    assert absent == {f"FOOTBALL_FIXTURE:{key}", f"FOOTBALL_RESULT:{key}"}
    # F3 has no deletion semantics: the last known version stays selected, visibly flagged.
    assert any(f.event_id.value == key for f in at(b, T2).fixtures)
    reversed_order = build(
        of_capture(dropped, received_at=T1), of_capture(ORIGINAL, received_at=T2)
    )
    assert not [i for i in reversed_order.issues if i.code == "RECORD_ABSENT_IN_LATER_REVISION"]


def test_materialization_rejects_empty_build() -> None:
    with pytest.raises(ContractError, match="EMPTY_BUILD"):
        at(build(), T2)


# -- deterministic rebuild -------------------------------------------------------------


def _inputs() -> list:  # type: ignore[type-arg]
    return [
        of_capture(ORIGINAL, received_at=T1),
        of_capture(CORRECTED, received_at=T2),
        odds_capture(received_at=T2),
    ]


def _manifest_hash(captures: list, run_id: str) -> str:  # type: ignore[type-arg]
    ctx = context()
    b = build_football(captures, ctx)
    datasets = [at(b, cutoff) for cutoff in (T1, T2 + timedelta(hours=1))]
    manifest = build_manifest(
        b,
        raw_captures=(raw for raw, _payload in captures),
        mappings=ctx.mappings,
        capture_mode=CaptureMode.RETROSPECTIVE_ARCHIVE,
        openfootball_timezone=ctx.openfootball_timezone,
        code_version=CODE,
        datasets=datasets,
        extraction_run_id=run_id,
        extraction_started_at=T2,
        extraction_completed_at=T2 + timedelta(seconds=len(run_id)),
    )
    return manifest.content_hash


def test_rebuild_is_deterministic_across_order_and_run_identity() -> None:
    reference = _manifest_hash(_inputs(), "run-a")
    for seed in range(5):
        shuffled = _inputs()
        random.Random(seed).shuffle(shuffled)
        assert _manifest_hash(shuffled, f"run-{seed}-longer") == reference


def test_rebuild_from_store_matches_in_memory_build(tmp_path: Path) -> None:
    store = RawSnapshotStore(tmp_path)
    for raw, payload in _inputs():
        store.put(raw, payload)
    assert build_football(store.load(), context()) == build_football(_inputs(), context())
    assert _manifest_hash(list(store.load()), "x") == _manifest_hash(_inputs(), "y")


def test_manifest_changes_when_inputs_change() -> None:
    reference = _manifest_hash(_inputs(), "run")
    assert _manifest_hash(_inputs()[:1], "run") != reference


def test_manifest_records_lineage_and_counts() -> None:
    ctx = context()
    captures = _inputs()
    b = build_football(captures, ctx)
    manifest = build_manifest(
        b,
        raw_captures=(raw for raw, _ in captures),
        mappings=ctx.mappings,
        capture_mode=CaptureMode.RETROSPECTIVE_ARCHIVE,
        openfootball_timezone="Europe/London",
        code_version=CODE,
        datasets=[at(b, T2)],
        extraction_run_id="run-1",
        extraction_started_at=T2,
        extraction_completed_at=T2,
    )
    body = manifest.body
    assert [c.capture_id for c in body.raw_captures] == list(b.capture_ids)
    assert {(c.name, c.count) for c in body.record_counts} == {
        ("FIXTURE", 8),  # same fixture content, two source revisions
        ("RESULT", 8),
        ("ODDS", 5),
    }
    assert {v.name for v in body.parser_versions} == {"openfootball", "the_odds_api"}
    (evidence,) = body.pit_evidence
    assert evidence.selected_keys == 4 + 4 + 5
    assert body.code_version == CODE and body.canonical_schema_version
    with pytest.raises(ContractError, match="CAPTURE_SET_MISMATCH"):
        build_manifest(
            b,
            raw_captures=(raw for raw, _ in captures[:1]),
            mappings=ctx.mappings,
            capture_mode=CaptureMode.RETROSPECTIVE_ARCHIVE,
            openfootball_timezone="Europe/London",
            code_version=CODE,
            datasets=[],
            extraction_run_id="run-1",
            extraction_started_at=T2,
            extraction_completed_at=T2,
        )
