"""F4 data CLIs: pinned local capture and deterministic rebuild from a raw store."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest
from football_builders import season_text

from sports_quant.data.ingestion.football import git_blob_sha
from sports_quant.data.snapshots.store import RawSnapshotStore

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "data"
COMMIT = "00a01efad79294692263e841510ab78514da51da"


def _load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_capture_refuses_a_file_that_is_not_the_pinned_blob(tmp_path: Path) -> None:
    capture = _load("capture_openfootball_season")
    source = tmp_path / "season.txt"
    source.write_bytes(season_text())
    code = capture.main(
        [
            "--input",
            str(source),
            "--season-path",
            "2024-25/1-premierleague.txt",
            "--store",
            str(tmp_path / "s"),
        ]
    )
    assert code == 1
    assert RawSnapshotStore(tmp_path / "s").captures() == ()


def test_capture_refuses_an_unpinned_path(tmp_path: Path) -> None:
    capture = _load("capture_openfootball_season")
    source = tmp_path / "season.txt"
    source.write_bytes(season_text())
    code = capture.main(
        ["--input", str(source), "--season-path", "2099-00/x.txt", "--store", str(tmp_path)]
    )
    assert code == 2


def test_capture_accepts_the_pinned_blob(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    capture = _load("capture_openfootball_season")
    payload = season_text()
    monkeypatch.setattr(capture, "pinned_blob_sha", lambda _path: git_blob_sha(payload))
    source = tmp_path / "season.txt"
    source.write_bytes(payload)
    store = tmp_path / "store"
    assert (
        capture.main(
            [
                "--input",
                str(source),
                "--season-path",
                "2024-25/1-premierleague.txt",
                "--store",
                str(store),
            ]
        )
        == 0
    )
    (raw,) = RawSnapshotStore(store).captures()
    assert raw.source_revision == f"git-blob:{git_blob_sha(payload)}"


def test_rebuild_prints_the_same_hash_twice(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    capture = _load("capture_openfootball_season")
    rebuild = _load("rebuild_football_dataset")
    payload = season_text()
    monkeypatch.setattr(capture, "pinned_blob_sha", lambda _path: git_blob_sha(payload))
    source = tmp_path / "season.txt"
    source.write_bytes(payload)
    store = tmp_path / "store"
    capture.main(
        [
            "--input",
            str(source),
            "--season-path",
            "2024-25/1-premierleague.txt",
            "--store",
            str(store),
        ]
    )
    capsys.readouterr()
    args = [
        "--store",
        str(store),
        "--code-version",
        COMMIT,
        "--dataset-version",
        "test",
        "--cutoff",
        "2030-01-01T00:00:00+00:00",
        "--output",
        str(tmp_path / "manifest.json"),
    ]
    assert rebuild.main(args) == 0
    first = capsys.readouterr().out
    assert rebuild.main(args) == 0
    second = capsys.readouterr().out
    assert first == second
    assert "records FIXTURE 4" in first and "selected=8" in first
    assert (tmp_path / "manifest.json").is_file()


def test_rebuild_rejects_naive_cutoff(tmp_path: Path) -> None:
    rebuild = _load("rebuild_football_dataset")
    code = rebuild.main(
        [
            "--store",
            str(tmp_path),
            "--code-version",
            COMMIT,
            "--dataset-version",
            "t",
            "--cutoff",
            "2030-01-01T00:00:00",
        ]
    )
    assert code == 1
