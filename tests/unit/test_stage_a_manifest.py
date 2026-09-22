from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "research" / "validate_stage_a_manifest.py"
)
MANIFEST = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "manifests"
    / "football_odds_stage_a_epl_2024_25.json"
)


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_stage_a_manifest", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stage_a_manifest_is_complete_and_temporally_valid() -> None:
    module = _load_module()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert module.validate_manifest(data) == []
    assert data["kickoff_group_count"] == 23
    assert data["planned_query_count"] == 69
    assert len(data["query_plan"]) == 69


def test_stage_a_manifest_bst_to_utc_conversion_regression() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    first = data["kickoff_groups"][0]
    assert first["kickoff_local_europe_london"] == "2024-08-16T20:00:00+01:00"
    assert first["kickoff_utc"] == "2024-08-16T19:00:00Z"
    assert first["cutoffs"]["T-24h"] == "2024-08-15T19:00:00Z"
    assert first["cutoffs"]["T-1h"] == "2024-08-16T18:00:00Z"
    assert first["cutoffs"]["T-15m"] == "2024-08-16T18:45:00Z"


def test_stage_a_manifest_last_group_regression() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    last = data["kickoff_groups"][-1]
    assert last["kickoff_local_europe_london"] == "2024-09-15T16:30:00+01:00"
    assert last["kickoff_utc"] == "2024-09-15T15:30:00Z"
    assert last["cutoffs"]["T-24h"] == "2024-09-14T15:30:00Z"
    assert last["cutoffs"]["T-1h"] == "2024-09-15T14:30:00Z"
    assert last["cutoffs"]["T-15m"] == "2024-09-15T15:15:00Z"
