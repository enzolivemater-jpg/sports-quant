from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "research" / "render_probe_evidence.py"
)


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("render_probe_evidence", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _metadata() -> dict[str, object]:
    return {
        "research_only": True,
        "provider": "example-provider",
        "probe_name": "fixtures",
        "requested_at": "2026-09-22T16:00:00+00:00",
        "received_at": "2026-09-22T16:00:01+00:00",
        "request_url_redacted": (
            "https://provider.example/fixtures?api_key=%2A%2A%2AREDACTED%2A%2A%2A"
        ),
        "http_status": 200,
        "selected_response_headers": {"X-RateLimit-Remaining": "99"},
        "payload_sha256": "a" * 64,
        "payload_bytes": 1234,
        "payload_file": "capture.json",
        "error": None,
        "canonical_known_at_assigned": False,
    }


def test_render_preserves_safe_capture_facts_and_unknowns() -> None:
    module = _load_module()

    rendered = module.render_evidence(_metadata())

    assert "example-provider" in rendered
    assert "2026-09-22T16:00:01+00:00" in rendered
    assert "Canonical known_at assigned: NO" in rendered
    assert "Payload SHA-256: " + ("a" * 64) in rendered
    assert "UNKNOWN" in rendered
    assert "OD-24" in rendered


def test_renderer_rejects_metadata_that_assigns_known_at() -> None:
    module = _load_module()
    metadata = _metadata()
    metadata["canonical_known_at_assigned"] = True

    with pytest.raises(ValueError, match="canonical_known_at_assigned=false"):
        module.render_evidence(metadata)


def test_renderer_rejects_missing_required_capture_field() -> None:
    module = _load_module()
    metadata = _metadata()
    del metadata["payload_sha256"]

    with pytest.raises(ValueError, match="payload_sha256"):
        module.render_evidence(metadata)


def test_main_writes_only_inside_research_probe_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    root = (tmp_path / "research-probes").resolve()
    monkeypatch.setattr(module, "OUTPUT_ROOT", root)

    metadata_path = root / "provider" / "probe" / "capture.metadata.json"
    metadata_path.parent.mkdir(parents=True)
    metadata_path.write_text(json.dumps(_metadata()), encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT),
            "--research-only",
            "--metadata",
            str(metadata_path),
        ],
    )

    assert module.main() == 0
    expected = metadata_path.with_suffix(".evidence.md")
    assert expected.is_file()


def test_main_rejects_output_outside_probe_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    root = (tmp_path / "research-probes").resolve()
    monkeypatch.setattr(module, "OUTPUT_ROOT", root)

    metadata_path = root / "provider" / "probe" / "capture.metadata.json"
    metadata_path.parent.mkdir(parents=True)
    metadata_path.write_text(json.dumps(_metadata()), encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT),
            "--research-only",
            "--metadata",
            str(metadata_path),
            "--output",
            str(tmp_path / "outside.md"),
        ],
    )

    assert module.main() == 1
