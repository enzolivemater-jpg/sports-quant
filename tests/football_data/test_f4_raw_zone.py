"""F4 raw zone: immutable captures, write-once store, secret redaction."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
from football_builders import T1, odds_capture, of_capture, season_text

from sports_quant.contracts.common import ContractError
from sports_quant.data.snapshots.raw import (
    REDACTED,
    RawCapture,
    RequestParameter,
    capture,
    sha256_hex,
)
from sports_quant.data.snapshots.store import RawSnapshotStore

SECRET = "synthetic-secret-api-key"


def test_capture_records_hash_size_lineage_and_provider_timestamps() -> None:
    raw, payload = of_capture(season_text())
    assert raw.payload_sha256 == sha256_hex(payload)
    assert raw.payload_size == len(payload)
    assert raw.received_at == T1
    assert raw.source_revision is not None and raw.source_revision.startswith("git-blob:")
    ref = raw.snapshot_ref()
    assert (ref.source_id, ref.payload_sha256, ref.received_at) == (
        "openfootball",
        raw.payload_sha256,
        T1,
    )
    assert ref.request_identity == "openfootball/england/2024-25/1-premierleague.txt"


def test_secret_parameters_are_redacted_everywhere() -> None:
    raw, _payload = odds_capture(api_key=SECRET)
    assert raw.parameter("apiKey") == REDACTED
    for text in (raw.to_json(), raw.request_identity(), raw.snapshot_ref().to_json()):
        assert SECRET not in text
    assert raw.parameter("date") is not None  # non-secret parameters are kept verbatim


def test_unredacted_secret_cannot_be_constructed() -> None:
    with pytest.raises(ContractError, match="UNREDACTED_SECRET"):
        RequestParameter(name="api_key", value=SECRET)
    raw, _payload = odds_capture()
    data = raw.to_dict()
    data["request_parameters"][0]["value"] = SECRET
    with pytest.raises(ContractError, match="UNREDACTED_SECRET"):
        RawCapture.from_dict(data)


@pytest.mark.parametrize(
    "resource",
    [
        "https://api.example.com/odds?apiKey=leak",
        "https://user:pass@api.example.com/odds",
    ],
)
def test_resource_cannot_smuggle_query_or_credentials(resource: str) -> None:
    with pytest.raises(ContractError, match="RESOURCE_HAS_QUERY|CREDENTIALS_IN_RESOURCE"):
        capture(
            b"{}",
            source_id="the_odds_api",
            resource=resource,
            request_parameters={},
            received_at=T1,
            provider_timestamps={},
            source_revision=None,
            media_type="application/json",
            http_status=200,
            ingestion_version="v",
        )


def test_capture_and_store_never_log_secrets(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    raw, payload = odds_capture(api_key=SECRET)
    RawSnapshotStore(tmp_path).put(raw, payload)
    assert SECRET not in caplog.text
    assert all(SECRET not in p.read_text() for p in (tmp_path / "captures").iterdir())


def test_store_round_trips_and_is_idempotent(tmp_path: Path) -> None:
    store = RawSnapshotStore(tmp_path)
    raw, payload = of_capture(season_text())
    store.put(raw, payload)
    store.put(raw, payload)  # identical re-ingestion is a no-op
    assert store.load() == ((raw, payload),)


def test_store_never_overwrites_a_capture(tmp_path: Path) -> None:
    store = RawSnapshotStore(tmp_path)
    raw, payload = of_capture(season_text())
    store.put(raw, payload)
    path = tmp_path / "captures" / f"{raw.capture_id}.json"
    path.chmod(0o644)
    path.write_text(path.read_text().replace("openfootball/", "tampered/"))
    with pytest.raises(ContractError, match="RAW_STORE_OVERWRITE"):
        store.put(raw, payload)


def test_store_detects_corrupted_payload(tmp_path: Path) -> None:
    store = RawSnapshotStore(tmp_path)
    raw, payload = of_capture(season_text())
    store.put(raw, payload)
    path = tmp_path / "payloads" / raw.payload_sha256
    path.chmod(0o644)
    path.write_bytes(payload + b"\n")
    with pytest.raises(ContractError, match="RAW_STORE_INTEGRITY"):
        store.load()


def test_store_rejects_payload_not_matching_capture(tmp_path: Path) -> None:
    raw, payload = of_capture(season_text())
    with pytest.raises(ContractError, match="PAYLOAD_MISMATCH"):
        RawSnapshotStore(tmp_path).put(raw, payload + b"x")


def test_stored_files_are_read_only(tmp_path: Path) -> None:
    raw, payload = of_capture(season_text())
    RawSnapshotStore(tmp_path).put(raw, payload)
    mode = (tmp_path / "payloads" / raw.payload_sha256).stat().st_mode & 0o777
    assert mode == 0o444


def test_a_correction_is_a_new_capture_beside_the_old_one(tmp_path: Path) -> None:
    store = RawSnapshotStore(tmp_path)
    first = of_capture(season_text(), received_at=T1)
    corrected = of_capture(season_text().replace(b"1-0 (0-0)", b"2-0 (0-0)"))
    store.put(*first)
    store.put(*corrected)
    assert {raw.capture_id for raw, _ in store.load()} == {
        first[0].capture_id,
        corrected[0].capture_id,
    }
