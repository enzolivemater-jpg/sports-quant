"""As-of version selection for one logical record."""

from __future__ import annotations

import itertools
from datetime import datetime, timedelta, timezone

import pytest
from pit_builders import CUTOFF, at, data_state, version

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.data_state import ConflictState, QualityState
from sports_quant.contracts.time import KnownAtBasis
from sports_quant.data.point_in_time.eligibility import PitRejectionReason
from sports_quant.data.point_in_time.selection import (
    AsOfSelection,
    RecordDisposition,
    SelectionStatus,
    select_as_of,
)

D = RecordDisposition


def _dispositions(selection: AsOfSelection) -> dict[str | None, RecordDisposition]:
    return {decision.revision_id: decision.disposition for decision in selection.decisions}


def test_correction_after_cutoff_never_leaks_backward() -> None:
    v1 = version(at(10), revision_id="v1", payload="lineup A")
    v2 = version(at(14), revision_id="v2", payload="lineup B (correction)")
    replay = select_as_of([v1, v2], CUTOFF)
    assert replay.status is SelectionStatus.SELECTED
    assert replay.selected == v1
    assert _dispositions(replay) == {"v1": D.SELECTED, "v2": D.REJECTED}
    later = select_as_of([v1, v2], at(15))
    assert later.selected == v2
    assert _dispositions(later) == {"v1": D.SUPERSEDED, "v2": D.SELECTED}


def test_only_the_late_correction_exists_so_nothing_is_fabricated() -> None:
    v2 = version(at(14), revision_id="v2")
    replay = select_as_of([v2], CUTOFF)
    assert replay.status is SelectionStatus.NO_ELIGIBLE_VERSION
    assert replay.selected is None


@pytest.mark.parametrize(
    ("cutoff", "expected"),
    [
        (at(8), None),
        (at(9), "v1"),
        (at(9.5), "v1"),
        (at(10), "v2"),
        (at(12), "v3"),
        (at(13), "v4"),
        (at(20), "v4"),
    ],
)
def test_as_of_selection_among_four_revisions(cutoff: datetime, expected: str | None) -> None:
    revisions = [
        version(at(9), revision_id="v1"),
        version(at(10), revision_id="v2"),
        version(at(11), revision_id="v3"),
        version(at(13), revision_id="v4"),
    ]
    selection = select_as_of(revisions, cutoff)
    selected = selection.selected.revision_id if selection.selected else None
    assert selected == expected
    for decision in selection.decisions:
        assert decision.known_at is not None
        if decision.disposition is D.SELECTED:
            assert decision.known_at <= cutoff


def test_selection_is_independent_of_input_order() -> None:
    revisions = [
        version(at(9), revision_id="v1"),
        version(at(10), revision_id="v2"),
        version(at(11), revision_id="v3"),
        version(at(13), revision_id="v4"),
    ]
    results = {select_as_of(p, CUTOFF).to_json() for p in itertools.permutations(revisions)}
    assert len(results) == 1


def test_singletons() -> None:
    assert select_as_of([version(at(10))], CUTOFF).status is SelectionStatus.SELECTED
    assert select_as_of([version(at(13))], CUTOFF).status is SelectionStatus.NO_ELIGIBLE_VERSION


def test_empty_input_is_rejected() -> None:
    with pytest.raises(ContractError) as excinfo:
        select_as_of([], CUTOFF)
    assert excinfo.value.code == "NO_RECORDS"


def test_mixed_logical_keys_are_rejected() -> None:
    with pytest.raises(ContractError) as excinfo:
        select_as_of([version(at(9)), version(at(10), key="other")], CUTOFF)
    assert excinfo.value.code == "MIXED_LOGICAL_KEYS"


def test_exact_duplicates_collapse_to_one_version() -> None:
    v1 = version(at(10), revision_id="v1")
    assert select_as_of([v1, v1, v1], CUTOFF) == select_as_of([v1], CUTOFF)


def test_tie_at_latest_known_at_is_unresolved_not_guessed() -> None:
    a = version(at(10), revision_id="a", payload="A")
    b = version(at(10), revision_id="b", payload="B")
    older = version(at(9), revision_id="old")
    selection = select_as_of([older, a, b], CUTOFF)
    assert selection.status is SelectionStatus.UNRESOLVED
    assert selection.selected is None
    assert set(_dispositions(selection).values()) == {D.UNRESOLVED}


def test_tie_detection_is_instant_based_across_offsets() -> None:
    a = version(at(10), revision_id="a", payload="A")
    b = version(at(10).astimezone(timezone(timedelta(hours=5))), revision_id="b", payload="B")
    assert select_as_of([a, b], CUTOFF).status is SelectionStatus.UNRESOLVED


def test_same_revision_with_different_content_is_unresolved() -> None:
    first = version(at(9), revision_id="v1", payload="lineup A")
    conflicting = version(at(10), revision_id="v1", payload="lineup B")
    selection = select_as_of([first, conflicting], CUTOFF)
    assert selection.status is SelectionStatus.UNRESOLVED
    assert selection.selected is None


def test_revision_conflict_known_after_cutoff_does_not_leak_backward() -> None:
    # Regression (found during F3): a rewrite of v2 first known at 15:00 made the 12:00
    # replay UNRESOLVED, i.e. post-cutoff information changed a historical outcome.
    v1 = version(at(9), revision_id="v1", payload="A")
    v2 = version(at(10), revision_id="v2", payload="B")
    v2_rewritten = version(at(15), revision_id="v2", payload="B'")
    assert select_as_of([v1, v2, v2_rewritten], CUTOFF).selected == v2
    assert select_as_of([v1, v2, v2_rewritten], at(16)).status is SelectionStatus.UNRESOLVED


def test_undated_revision_conflict_does_not_influence_selection() -> None:
    v1 = version(at(9), revision_id="v1", payload="A")
    undated_rewrite = version(None, revision_id="v1", payload="A'")
    assert select_as_of([v1, undated_rewrite], CUTOFF).selected == v1


def test_unidentified_version_known_after_latest_eligible_makes_key_unresolved() -> None:
    v1 = version(at(9), revision_id="v1")
    unidentified = version(at(11), revision_id=None)
    selection = select_as_of([v1, unidentified], CUTOFF)
    assert selection.status is SelectionStatus.UNRESOLVED
    assert _dispositions(selection) == {"v1": D.UNRESOLVED, None: D.REJECTED}


def test_unidentified_version_older_than_selected_does_not_block() -> None:
    unidentified = version(at(8), revision_id=None)
    v1 = version(at(9), revision_id="v1")
    assert select_as_of([unidentified, v1], CUTOFF).selected == v1


def test_unidentified_version_known_after_cutoff_does_not_block() -> None:
    v1 = version(at(9), revision_id="v1")
    unidentified = version(at(14), revision_id=None)
    assert select_as_of([v1, unidentified], CUTOFF).selected == v1


def test_undated_version_is_rejected_and_does_not_block() -> None:
    v1 = version(at(9), revision_id="v1")
    undated = version(None, revision_id="v?")
    selection = select_as_of([v1, undated], CUTOFF)
    assert selection.selected == v1
    assert _dispositions(selection)["v?"] is D.REJECTED


def test_current_version_not_yet_valid_does_not_fall_back_to_superseded() -> None:
    v1 = version(at(9), revision_id="v1")
    v2 = version(at(11), revision_id="v2", valid_from=at(13))
    selection = select_as_of([v1, v2], CUTOFF)
    assert selection.status is SelectionStatus.NO_ELIGIBLE_VERSION
    assert selection.selected is None
    assert _dispositions(selection) == {"v1": D.SUPERSEDED, "v2": D.REJECTED}
    decision = next(d for d in selection.decisions if d.revision_id == "v2")
    assert decision.reasons == (PitRejectionReason.NOT_YET_VALID_AT_CUTOFF,)
    assert select_as_of([v1, v2], at(13)).selected == v2


def test_expired_current_version_does_not_fall_back_to_superseded() -> None:
    v1 = version(at(9), revision_id="v1")
    v2 = version(at(11), revision_id="v2", expires_at=at(11.5))
    selection = select_as_of([v1, v2], CUTOFF)
    assert selection.status is SelectionStatus.NO_ELIGIBLE_VERSION
    assert _dispositions(selection) == {"v1": D.SUPERSEDED, "v2": D.REJECTED}
    assert select_as_of([v1, v2], at(11.25)).selected == v2


def test_older_version_rejected_on_its_own_does_not_block_current() -> None:
    v1 = version(at(9), revision_id="v1", expires_at=at(10))
    v2 = version(at(11), revision_id="v2")
    assert select_as_of([v1, v2], CUTOFF).selected == v2


def test_tie_including_an_invalid_version_is_still_unresolved() -> None:
    a = version(at(11), revision_id="a", payload="A")
    b = version(at(11), revision_id="b", payload="B", expires_at=at(11.5))
    assert select_as_of([a, b], CUTOFF).status is SelectionStatus.UNRESOLVED


def test_selected_version_identity_and_lineage_are_preserved() -> None:
    v1 = version(at(10), revision_id="v1", source_id="provider-b", raw=True)
    selection = select_as_of([v1], CUTOFF)
    assert selection.selected == v1
    (decision,) = selection.decisions
    assert decision.revision_id == "v1"
    assert decision.source_id == "provider-b"
    assert decision.record_digest == v1.content_digest()
    assert v1.raw_snapshot is not None
    assert decision.raw_payload_sha256 == v1.raw_snapshot.payload_sha256


def test_data_state_is_passed_through_unchanged() -> None:
    state = data_state(quality=QualityState.ERROR, conflict=ConflictState.OPEN)
    v1 = version(at(10), revision_id="v1", state=state)
    selection = select_as_of([v1], CUTOFF)
    assert selection.status is SelectionStatus.SELECTED
    assert selection.selected is not None
    assert selection.selected.provenance.data_state == state


def test_data_state_does_not_influence_which_version_is_selected() -> None:
    bad_latest = version(
        at(11),
        revision_id="v2",
        state=data_state(quality=QualityState.UNAVAILABLE, conflict=ConflictState.OPEN),
    )
    good_older = version(at(10), revision_id="v1")
    assert select_as_of([good_older, bad_latest], CUTOFF).selected == bad_latest


def test_selection_round_trips() -> None:
    selection = select_as_of(
        [version(at(9), revision_id="v1"), version(at(13), revision_id="v2")], CUTOFF
    )
    assert AsOfSelection.from_json(selection.to_json()) == selection


def test_selection_contract_rejects_inconsistent_payloads() -> None:
    payload = select_as_of([version(at(9), revision_id="v1")], CUTOFF).to_dict()
    payload["status"] = "NO_ELIGIBLE_VERSION"
    with pytest.raises(ContractError):
        AsOfSelection.from_dict(payload)
    payload = select_as_of([version(at(9), revision_id="v1")], CUTOFF).to_dict()
    payload["decisions"][0]["disposition"] = "SUPERSEDED"
    with pytest.raises(ContractError):
        AsOfSelection.from_dict(payload)


def test_verified_source_availability_basis_uses_its_known_at() -> None:
    record = version(
        at(9),
        revision_id="v1",
        basis=KnownAtBasis.VERIFIED_SOURCE_AVAILABILITY,
        received_at=at(20),
    )
    assert select_as_of([record], CUTOFF).selected == record
