"""P1-06 regressions: raw snapshot lineage is bound to the record's provenance."""

from __future__ import annotations

import dataclasses
from datetime import timedelta, timezone

import pytest
from pit_builders import at, sha, version

from sports_quant.contracts.common import ContractError
from sports_quant.data.point_in_time.records import PitRecord, RawSnapshotRef


def _raw_record() -> PitRecord:
    record = version(at(10), revision_id="v1", source_id="provider-a", raw=True)
    assert record.raw_snapshot is not None
    return record


def _with_raw(record: PitRecord, **changes: object) -> PitRecord:
    assert record.raw_snapshot is not None
    raw = dataclasses.replace(record.raw_snapshot, **changes)  # type: ignore[arg-type]
    return dataclasses.replace(record, raw_snapshot=raw)


def test_raw_snapshot_from_another_source_is_rejected() -> None:
    with pytest.raises(ContractError) as excinfo:
        _with_raw(_raw_record(), source_id="provider-b")
    assert excinfo.value.code == "RAW_SNAPSHOT_SOURCE_MISMATCH"


@pytest.mark.parametrize("delta", [timedelta(seconds=1), -timedelta(hours=1)])
def test_raw_snapshot_received_at_another_instant_is_rejected(delta: timedelta) -> None:
    with pytest.raises(ContractError) as excinfo:
        _with_raw(_raw_record(), received_at=at(10) + delta)
    assert excinfo.value.code == "RAW_SNAPSHOT_RECEIVED_AT_MISMATCH"


def test_raw_snapshot_received_at_same_instant_other_offset_is_accepted() -> None:
    shifted = at(10).astimezone(timezone(timedelta(hours=-5, minutes=-30)))
    record = _with_raw(_raw_record(), received_at=shifted)
    assert record.raw_snapshot is not None
    assert record.raw_snapshot.received_at.utcoffset() != timedelta(0)


def test_raw_payload_digest_is_not_the_normalized_payload_digest() -> None:
    record = _with_raw(_raw_record(), payload_sha256=sha("a different raw response"))
    assert record.raw_snapshot is not None
    assert record.raw_snapshot.payload_sha256 != record.payload_sha256


def test_valid_raw_lineage_round_trips() -> None:
    record = _raw_record()
    assert PitRecord.from_json(record.to_json()) == record
    assert isinstance(record.raw_snapshot, RawSnapshotRef)


def test_mismatched_raw_lineage_is_rejected_on_deserialization() -> None:
    payload = _raw_record().to_dict()
    payload["raw_snapshot"]["source_id"] = "provider-b"
    with pytest.raises(ContractError) as excinfo:
        PitRecord.from_dict(payload)
    assert excinfo.value.code == "RAW_SNAPSHOT_SOURCE_MISMATCH"
    payload = _raw_record().to_dict()
    payload["raw_snapshot"]["received_at"] = at(11).isoformat()
    with pytest.raises(ContractError) as excinfo:
        PitRecord.from_dict(payload)
    assert excinfo.value.code == "RAW_SNAPSHOT_RECEIVED_AT_MISMATCH"
