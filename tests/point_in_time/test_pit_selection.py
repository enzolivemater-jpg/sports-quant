"""As-of version selection for one logical record."""

from __future__ import annotations

import itertools
from datetime import datetime, timedelta, timezone

import pytest
from pit_builders import CUTOFF, at, data_state, version

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.data_state import ConflictState, DataState, QualityState
from sports_quant.contracts.time import KnownAtBasis
from sports_quant.data.point_in_time.eligibility import PitRejectionReason
from sports_quant.data.point_in_time.records import PitRecord, SourceVersionRef
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
    assert _dispositions(later) == {"v1": D.ELIGIBLE_NOT_LATEST, "v2": D.SELECTED}


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


# P1-02 regressions: knowing a newer version that is not valid at the cutoff does not
# supersede an older version that is. There is no supersession field in F2/F3.


def test_newer_version_not_yet_valid_does_not_displace_older_valid_version() -> None:
    v1 = version(at(9), revision_id="v1")
    v2 = version(at(11), revision_id="v2", valid_from=at(13))
    selection = select_as_of([v1, v2], CUTOFF)
    assert selection.status is SelectionStatus.SELECTED
    assert selection.selected == v1
    assert _dispositions(selection) == {"v1": D.SELECTED, "v2": D.REJECTED}
    decision = next(d for d in selection.decisions if d.revision_id == "v2")
    assert decision.reasons == (PitRejectionReason.NOT_YET_VALID_AT_CUTOFF,)
    assert select_as_of([v1, v2], at(13)).selected == v2


@pytest.mark.parametrize(
    "bound", [{"expires_at": at(11.5)}, {"expires_at": CUTOFF}, {"valid_to": at(11.5)}]
)
def test_newer_version_expired_at_cutoff_does_not_displace_older_valid_version(
    bound: dict[str, datetime],
) -> None:
    v1 = version(at(9), revision_id="v1")
    v2 = version(at(11), revision_id="v2", **bound)  # type: ignore[arg-type]
    selection = select_as_of([v1, v2], CUTOFF)
    assert selection.status is SelectionStatus.SELECTED
    assert selection.selected == v1
    assert _dispositions(selection) == {"v1": D.SELECTED, "v2": D.REJECTED}
    assert select_as_of([v1, v2], at(11.25)).selected == v2


def test_older_version_expired_at_cutoff_is_not_selected() -> None:
    v1 = version(at(9), revision_id="v1", expires_at=at(10))
    v2 = version(at(11), revision_id="v2", valid_from=at(13))
    selection = select_as_of([v1, v2], CUTOFF)
    assert selection.status is SelectionStatus.NO_ELIGIBLE_VERSION
    assert _dispositions(selection) == {"v1": D.REJECTED, "v2": D.REJECTED}


def test_older_version_rejected_on_its_own_does_not_block_current() -> None:
    v1 = version(at(9), revision_id="v1", expires_at=at(10))
    v2 = version(at(11), revision_id="v2")
    assert select_as_of([v1, v2], CUTOFF).selected == v2


def test_same_latest_known_at_only_the_valid_candidate_is_selected() -> None:
    a = version(at(11), revision_id="a", payload="A")
    b = version(at(11), revision_id="b", payload="B", expires_at=at(11.5))
    older = version(at(9), revision_id="old")
    selection = select_as_of([older, a, b], CUTOFF)
    assert selection.status is SelectionStatus.SELECTED
    assert selection.selected == a
    assert _dispositions(selection) == {
        "a": D.SELECTED,
        "b": D.REJECTED,
        "old": D.ELIGIBLE_NOT_LATEST,
    }


def test_same_latest_known_at_with_source_content_conflict_stays_unresolved() -> None:
    a = version(at(11), revision_id="a", payload="A")
    a_rewritten = version(at(11), revision_id="a", payload="A'", expires_at=at(11.5))
    selection = select_as_of([a, a_rewritten], CUTOFF)
    assert selection.status is SelectionStatus.UNRESOLVED
    assert selection.selected is None


def test_invalid_revision_known_after_cutoff_cannot_affect_earlier_replay() -> None:
    v1 = version(at(9), revision_id="v1")
    later = [
        version(at(14), revision_id="v2"),
        version(at(14), revision_id="v1", payload="v1 rewritten"),
        version(at(15), revision_id=None),
        version(at(15), revision_id="v3", valid_from=at(10)),
    ]
    replay = select_as_of([v1, *later], CUTOFF)
    assert replay.status is SelectionStatus.SELECTED
    assert replay.selected == v1
    assert {
        d.disposition for d in replay.decisions if d.revision_id != "v1" or d.known_at != at(9)
    } == {D.REJECTED}


def test_older_version_observed_again_after_newer_one_is_unresolved() -> None:
    # Without supersession semantics the order of v1 and v2 at 12:00 is ambiguous.
    v1 = version(at(9), revision_id="v1", payload="A")
    v2 = version(at(10), revision_id="v2", payload="B")
    v1_again = version(at(11), revision_id="v1", payload="A")
    selection = select_as_of([v1, v2, v1_again], CUTOFF)
    assert selection.status is SelectionStatus.UNRESOLVED
    assert select_as_of([v1, v2, v1_again], at(10.5)).selected == v2


# P1-03 regressions: source-version identity is (source_id, revision_id) with content
# payload_sha256; DataState, receipt and raw lineage belong to the observation.


def test_same_source_version_with_different_data_state_is_not_unresolved() -> None:
    first = version(at(10), revision_id="v1", payload="A")
    restated = version(
        at(10),
        revision_id="v1",
        payload="A",
        state=data_state(quality=QualityState.PARTIAL, conflict=ConflictState.OPEN),
    )
    assert first.content_digest() != restated.content_digest()
    selection = select_as_of([first, restated], CUTOFF)
    assert selection.status is SelectionStatus.SELECTED
    assert selection.selected is not None
    assert selection.selected.source_version() == first.source_version()
    assert sorted(d.disposition for d in selection.decisions) == sorted(
        [D.SELECTED, D.DUPLICATE_OBSERVATION]
    )


def test_same_source_version_with_different_receipt_and_raw_lineage_is_not_unresolved() -> None:
    first = version(at(10), revision_id="v1", payload="A", raw=True)
    refetched = version(at(11), revision_id="v1", payload="A", raw=True)
    verified = version(
        at(10),
        revision_id="v1",
        payload="A",
        basis=KnownAtBasis.VERIFIED_SOURCE_AVAILABILITY,
        received_at=at(11.5),
    )
    assert first.raw_snapshot != refetched.raw_snapshot
    selection = select_as_of([refetched, verified, first], CUTOFF)
    assert selection.status is SelectionStatus.SELECTED
    # The earliest eligible observation is selected; ties break on the record digest.
    assert selection.selected == min(first, verified, key=lambda r: r.content_digest())
    assert sorted(d.disposition for d in selection.decisions) == sorted(
        [D.SELECTED, D.DUPLICATE_OBSERVATION, D.DUPLICATE_OBSERVATION]
    )


def test_same_source_version_with_different_payload_is_unresolved() -> None:
    first = version(at(10), revision_id="v1", payload="A")
    conflicting = version(at(10), revision_id="v1", payload="B")
    selection = select_as_of([first, conflicting], CUTOFF)
    assert selection.status is SelectionStatus.UNRESOLVED
    assert {d.disposition for d in selection.decisions} == {D.UNRESOLVED}


def test_revision_ids_are_scoped_by_source() -> None:
    a = version(at(9), revision_id="1", payload="A", source_id="provider-a")
    b = version(at(10), revision_id="1", payload="B", source_id="provider-b")
    assert a.source_version() != b.source_version()
    selection = select_as_of([a, b], CUTOFF)
    assert selection.status is SelectionStatus.SELECTED
    assert selection.selected == b
    assert selection.selected.source_version() == SourceVersionRef(
        source_id="provider-b", revision_id="1"
    )


def test_same_revision_label_from_two_sources_at_the_same_instant_is_a_tie() -> None:
    a = version(at(10), revision_id="1", payload="A", source_id="provider-a")
    b = version(at(10), revision_id="1", payload="A", source_id="provider-b")
    assert select_as_of([a, b], CUTOFF).status is SelectionStatus.UNRESOLVED


def test_observation_identity_results_are_independent_of_input_order() -> None:
    records = [
        version(at(9), revision_id="v1", payload="A", raw=True),
        version(at(10), revision_id="v2", payload="B"),
        version(at(10.5), revision_id="v2", payload="B", raw=True),
        version(at(10), revision_id="v2", payload="B", state=data_state(QualityState.ERROR)),
        version(at(10), revision_id="1", payload="X", source_id="provider-b", expires_at=at(11)),
        version(at(13), revision_id="v3", payload="C"),
    ]
    results = {select_as_of(p, CUTOFF).to_json() for p in itertools.permutations(records)}
    assert len(results) == 1
    selection = select_as_of(records, CUTOFF)
    assert selection.selected is not None
    assert selection.selected.source_version() == SourceVersionRef(
        source_id="provider-a", revision_id="v2"
    )


def test_changing_only_data_state_keeps_status_and_selected_source_version() -> None:
    def history(state: DataState) -> list[PitRecord]:
        return [
            version(at(9), revision_id="v1", state=state),
            version(at(10), revision_id="v2", state=state),
            version(at(10.5), revision_id="v2", payload="value@" + at(10).isoformat()),
        ]

    good = select_as_of(history(data_state()), CUTOFF)
    bad = select_as_of(
        history(data_state(QualityState.UNAVAILABLE, conflict=ConflictState.OPEN)), CUTOFF
    )
    assert good.status is bad.status is SelectionStatus.SELECTED
    assert good.selected is not None and bad.selected is not None
    assert good.selected.source_version() == bad.selected.source_version()
    assert good.selected.payload_sha256 == bad.selected.payload_sha256
    assert good.selected.provenance.data_state != bad.selected.provenance.data_state


def test_selected_version_identity_and_lineage_are_preserved() -> None:
    v1 = version(at(10), revision_id="v1", source_id="provider-b", raw=True)
    selection = select_as_of([v1], CUTOFF)
    assert selection.selected == v1
    (decision,) = selection.decisions
    assert decision.revision_id == "v1"
    assert decision.source_id == "provider-b"
    assert decision.payload_sha256 == v1.payload_sha256
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
    payload["decisions"][0]["disposition"] = "ELIGIBLE_NOT_LATEST"
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
