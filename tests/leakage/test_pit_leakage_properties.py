"""Seeded property tests: no information known after the cutoff reaches a replay."""

from __future__ import annotations

import dataclasses
import random
import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "point_in_time"))

from pit_builders import at, data_state, version  # noqa: E402

from sports_quant.contracts.common import instant  # noqa: E402
from sports_quant.contracts.data_state import (  # noqa: E402
    ConflictState,
    FreshnessState,
    QualityState,
    VerificationState,
)
from sports_quant.data.point_in_time.eligibility import rejection_reasons  # noqa: E402
from sports_quant.data.point_in_time.records import PitRecord  # noqa: E402
from sports_quant.data.point_in_time.selection import (  # noqa: E402
    AsOfSelection,
    SelectionStatus,
    select_as_of,
)

SEEDS = range(300)


def _random_version(rng: random.Random, *, known_at: datetime | None) -> PitRecord:
    optional = [None, None, None, at(rng.randrange(0, 48) / 2)]
    return version(
        known_at,
        revision_id=rng.choice(["r1", "r2", "r3", "r4", "r5", None]),
        payload=rng.choice(["A", "B", "C"]),
        valid_from=rng.choice(optional),
        expires_at=rng.choice(optional),
        state=data_state(
            rng.choice(list(QualityState)),
            rng.choice(list(FreshnessState)),
            rng.choice(list(VerificationState)),
            rng.choice(list(ConflictState)),
        ),
    )


def _history(rng: random.Random, cutoff: datetime) -> list[PitRecord]:
    records: list[PitRecord] = []
    for _ in range(rng.randrange(1, 7)):
        hours = rng.randrange(0, 48) / 2
        records.append(_random_version(rng, known_at=at(hours)))
    return [r for r in records if _valid_window(r)]


def _valid_window(record: PitRecord) -> bool:
    temporal = record.provenance.temporal
    return not (
        temporal.valid_from is not None
        and temporal.expires_at is not None
        and temporal.valid_from > temporal.expires_at
    )


def _outcome(selection: AsOfSelection) -> tuple[SelectionStatus, str | None]:
    selected = selection.selected.content_digest() if selection.selected else None
    return selection.status, selected


def _cutoff(rng: random.Random) -> datetime:
    return at(rng.randrange(0, 48) / 2 + 0.25 * rng.randrange(0, 2))


@pytest.mark.parametrize("seed", SEEDS)
def test_versions_known_later_or_undated_never_change_the_outcome(seed: int) -> None:
    rng = random.Random(seed)
    cutoff = _cutoff(rng)
    history = _history(rng, cutoff) or [_random_version(rng, known_at=at(0))]
    future = [
        _random_version(rng, known_at=cutoff + (at(rng.randrange(1, 20)) - at(0)))
        for _ in range(rng.randrange(1, 4))
    ] + [_random_version(rng, known_at=None) for _ in range(rng.randrange(0, 2))]
    base = select_as_of(history, cutoff)
    with_future = select_as_of(history + future, cutoff)
    assert _outcome(with_future) == _outcome(base)


@pytest.mark.parametrize("seed", SEEDS)
def test_a_selected_version_was_known_by_the_cutoff_and_is_fully_eligible(seed: int) -> None:
    rng = random.Random(seed)
    cutoff = _cutoff(rng)
    history = _history(rng, cutoff) or [_random_version(rng, known_at=at(0))]
    selection = select_as_of(history, cutoff)
    if selection.selected is not None:
        known_at = selection.selected.provenance.temporal.known_at
        assert known_at is not None and instant(known_at) <= instant(cutoff)
        assert rejection_reasons(selection.selected, cutoff) == ()
        later_known = [
            r
            for r in history
            if r.provenance.temporal.known_at is not None
            and known_at < r.provenance.temporal.known_at <= cutoff
        ]
        assert later_known == []


@pytest.mark.parametrize("seed", SEEDS)
def test_outcome_is_independent_of_input_order(seed: int) -> None:
    rng = random.Random(seed)
    cutoff = _cutoff(rng)
    history = _history(rng, cutoff) or [_random_version(rng, known_at=at(0))]
    reference = select_as_of(history, cutoff)
    for _ in range(5):
        rng.shuffle(history)
        assert select_as_of(history, cutoff) == reference


@pytest.mark.parametrize("seed", SEEDS)
def test_data_state_never_changes_status_or_selected_revision(seed: int) -> None:
    rng = random.Random(seed)
    cutoff = _cutoff(rng)
    history = _history(rng, cutoff) or [_random_version(rng, known_at=at(0))]
    restated = [
        dataclasses.replace(
            r,
            provenance=dataclasses.replace(
                r.provenance,
                data_state=data_state(
                    QualityState.ERROR,
                    FreshnessState.STALE,
                    VerificationState.UNVERIFIED,
                    ConflictState.OPEN,
                ),
            ),
        )
        for r in history
    ]

    def summary(selection: AsOfSelection) -> tuple[SelectionStatus, str | None]:
        chosen = selection.selected
        return selection.status, None if chosen is None else chosen.payload_sha256

    # Restating the data state can merge versions that differed only in data state,
    # so compare only when the distinct-version structure is unchanged.
    if len({r.content_digest() for r in restated}) == len({r.content_digest() for r in history}):
        assert summary(select_as_of(restated, cutoff)) == summary(select_as_of(history, cutoff))


@pytest.mark.parametrize("seed", SEEDS)
def test_clean_histories_select_the_latest_version_known_by_the_cutoff(seed: int) -> None:
    rng = random.Random(seed)
    cutoff = _cutoff(rng)
    hours = rng.sample(range(0, 48), rng.randrange(1, 8))
    history = [version(at(h / 2), revision_id=f"r{h}") for h in hours]
    selection = select_as_of(history, cutoff)
    known = [r for r in history if r.provenance.temporal.known_at <= cutoff]  # type: ignore[operator]
    if not known:
        assert selection.status is SelectionStatus.NO_ELIGIBLE_VERSION
    else:
        expected = max(known, key=lambda r: r.provenance.temporal.known_at)  # type: ignore[arg-type,return-value]
        assert selection.selected == expected
