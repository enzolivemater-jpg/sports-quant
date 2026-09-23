"""PIT materialization, manifest completeness and deterministic replay."""

from __future__ import annotations

import dataclasses
import random
import subprocess
import sys
from pathlib import Path

import pytest
from pit_builders import CODE, CUTOFF, DATASET, at, data_state, version

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.data_state import ConflictState, QualityState
from sports_quant.contracts.reproducibility import ArtifactKind, ArtifactRef, CodeVersion
from sports_quant.data.point_in_time.eligibility import PitRejectionReason
from sports_quant.data.point_in_time.manifest import (
    PitManifest,
    PitManifestBody,
    PitMaterialization,
    materialize,
    verify_replay,
)
from sports_quant.data.point_in_time.records import PitRecord
from sports_quant.data.point_in_time.selection import RecordDisposition, SelectionStatus


def _batch() -> list[PitRecord]:
    return [
        # lineup: V1 before cutoff, correction after cutoff
        version(at(10), key="lineup", revision_id="v1", payload="A", raw=True),
        version(at(14), key="lineup", revision_id="v2", payload="B", raw=True),
        # odds: three snapshots, latest before cutoff wins
        version(at(9), key="odds", revision_id="o1"),
        version(at(10), key="odds", revision_id="o2"),
        version(at(11), key="odds", revision_id="o3"),
        # injury: only a current-state snapshot fetched later
        version(at(20), key="injury", revision_id="i-now"),
        # weather: tie at the latest known_at
        version(at(11), key="weather", revision_id="w1", payload="sun"),
        version(at(11), key="weather", revision_id="w2", payload="rain"),
        # referee: undated
        version(None, key="referee", revision_id="r1"),
    ]


def _materialize(records: list[PitRecord], **overrides: object) -> PitMaterialization:
    kwargs: dict[str, object] = {
        "decision_cutoff_at": CUTOFF,
        "code_version": CODE,
        "dataset_ref": DATASET,
        "created_at": at(30),
    }
    kwargs.update(overrides)
    return materialize(records, **kwargs)  # type: ignore[arg-type]


def test_manifest_records_outcome_of_every_key() -> None:
    result = _materialize(_batch())
    outcomes = {o.logical_key: o.status for o in result.manifest.body.key_outcomes}
    assert outcomes == {
        "injury": SelectionStatus.NO_ELIGIBLE_VERSION,
        "lineup": SelectionStatus.SELECTED,
        "odds": SelectionStatus.SELECTED,
        "referee": SelectionStatus.NO_ELIGIBLE_VERSION,
        "weather": SelectionStatus.UNRESOLVED,
    }
    assert [(r.logical_key, r.revision_id) for r in result.selected] == [
        ("lineup", "v1"),
        ("odds", "o3"),
    ]


def test_manifest_is_complete() -> None:
    body = _materialize(_batch()).manifest.body
    assert body.decision_cutoff_at == CUTOFF
    assert body.code_version == CODE
    assert body.dataset_ref == DATASET
    assert body.input_record_count == 9
    assert len(body.record_decisions) == 9
    counts = {c.disposition: c.count for c in body.disposition_counts}
    assert counts == {
        RecordDisposition.SELECTED: 2,
        RecordDisposition.SUPERSEDED: 2,
        RecordDisposition.REJECTED: 3,
        RecordDisposition.UNRESOLVED: 2,
    }
    reasons = {c.reason: c.count for c in body.reason_counts}
    assert reasons == {
        PitRejectionReason.MISSING_KNOWN_AT: 1,
        PitRejectionReason.KNOWN_AFTER_CUTOFF: 2,
        PitRejectionReason.NOT_YET_VALID_AT_CUTOFF: 0,
        PitRejectionReason.EXPIRED_AT_CUTOFF: 0,
        PitRejectionReason.SOURCE_VERSION_UNRESOLVED: 0,
    }
    lineage = {d.revision_id: d.raw_payload_sha256 for d in body.record_decisions}
    assert lineage["v1"] is not None and lineage["o1"] is None


def test_replay_is_deterministic_regardless_of_order_and_run_time() -> None:
    reference = _materialize(_batch())
    rng = random.Random(20240816)
    for run in range(20):
        shuffled = _batch()
        rng.shuffle(shuffled)
        replay = _materialize(shuffled, created_at=at(40 + run))
        assert replay.manifest.body == reference.manifest.body
        assert replay.manifest.content_hash == reference.manifest.content_hash
        assert replay.selected == reference.selected
        assert replay.manifest.created_at != reference.manifest.created_at


def test_verify_replay() -> None:
    manifest = _materialize(_batch()).manifest
    verify_replay(manifest, reversed(_batch()))
    tampered = _batch()[:-1]
    with pytest.raises(ContractError) as excinfo:
        verify_replay(manifest, tampered)
    assert excinfo.value.code == "REPLAY_MISMATCH"


@pytest.mark.parametrize(
    "overrides",
    [
        {"decision_cutoff_at": at(12.5)},
        {"code_version": CodeVersion(commit="0" * 40)},
        {
            "dataset_ref": ArtifactRef(
                kind=ArtifactKind.SNAPSHOT, identifier="pit-test", version="2"
            )
        },
    ],
    ids=["cutoff", "code", "dataset"],
)
def test_hash_depends_on_cutoff_code_and_dataset(overrides: dict[str, object]) -> None:
    assert (
        _materialize(_batch(), **overrides).manifest.content_hash
        != _materialize(_batch()).manifest.content_hash
    )


def test_hash_binds_record_content_including_data_state_lineage() -> None:
    changed = _batch()
    changed[0] = version(
        at(10),
        key="lineup",
        revision_id="v1",
        payload="A",
        raw=True,
        state=data_state(quality=QualityState.PARTIAL, conflict=ConflictState.OPEN),
    )
    reference = _materialize(_batch())
    replay = _materialize(changed)
    assert replay.manifest.content_hash != reference.manifest.content_hash
    # ...while eligibility and selection are unaffected by the data state.
    assert [o.status for o in replay.manifest.body.key_outcomes] == [
        o.status for o in reference.manifest.body.key_outcomes
    ]
    assert replay.selected[0].provenance.data_state.conflict is ConflictState.OPEN


def test_hash_is_stable_across_processes() -> None:
    script = (
        "import sys; sys.path.insert(0, 'tests/point_in_time');"
        "from test_pit_manifest import _batch, _materialize;"
        "print(_materialize(_batch()).manifest.content_hash)"
    )
    hashes = {
        subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            check=True,
            env={"PYTHONHASHSEED": seed, "PATH": ""},
            cwd=Path(__file__).resolve().parents[2],
        ).stdout.strip()
        for seed in ("0", "1", "4242")
    }
    assert hashes == {_materialize(_batch()).manifest.content_hash}


def test_empty_input_produces_an_empty_deterministic_manifest() -> None:
    first = _materialize([])
    second = _materialize([], created_at=at(50))
    assert first.selected == ()
    assert first.manifest.body.input_record_count == 0
    assert first.manifest.body.key_outcomes == ()
    assert first.manifest.content_hash == second.manifest.content_hash


def test_duplicates_are_counted_as_inputs_but_decided_once() -> None:
    v1 = version(at(10), revision_id="v1")
    result = _materialize([v1, v1])
    assert result.manifest.body.input_record_count == 2
    assert len(result.manifest.body.record_decisions) == 1


def test_manifest_round_trips_and_self_verifies() -> None:
    manifest = _materialize(_batch()).manifest
    assert PitManifest.from_json(manifest.to_json()) == manifest
    payload = manifest.to_dict()
    payload["content_hash"] = "0" * 64
    with pytest.raises(ContractError) as excinfo:
        PitManifest.from_dict(payload)
    assert excinfo.value.code == "CONTENT_HASH_MISMATCH"


def test_manifest_body_rejects_inconsistent_counts() -> None:
    payload = _materialize(_batch()).manifest.body.to_dict()
    payload["disposition_counts"][0]["count"] += 1
    with pytest.raises(ContractError) as excinfo:
        PitManifestBody.from_dict(payload)
    assert excinfo.value.code == "COUNT_MISMATCH"


def test_manifest_body_rejects_non_canonical_order() -> None:
    body = _materialize(_batch()).manifest.body
    with pytest.raises(ContractError) as excinfo:
        dataclasses.replace(body, key_outcomes=tuple(reversed(body.key_outcomes)))
    assert excinfo.value.code == "NON_CANONICAL_MANIFEST"


def test_materialization_rejects_selected_records_not_in_manifest() -> None:
    result = _materialize(_batch())
    with pytest.raises(ContractError):
        dataclasses.replace(result, selected=result.selected[:1])


def test_dataset_ref_must_be_dataset_or_snapshot() -> None:
    with pytest.raises(ContractError):
        _materialize(
            _batch(),
            dataset_ref=ArtifactRef(kind=ArtifactKind.MODEL, identifier="m", version="1"),
        )


def test_naive_cutoff_and_created_at_are_rejected() -> None:
    with pytest.raises(ContractError):
        _materialize(_batch(), decision_cutoff_at=CUTOFF.replace(tzinfo=None))
    with pytest.raises(ContractError):
        _materialize(_batch(), created_at=at(30).replace(tzinfo=None))
