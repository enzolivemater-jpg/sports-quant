from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType

SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "research" / "validate_stage_a_fixtures.py"
)
ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "data" / "manifests" / "football_odds_stage_a_epl_2024_25_fixtures.json"
CUTOFFS = ROOT / "data" / "manifests" / "football_odds_stage_a_epl_2024_25.json"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_stage_a_fixtures", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fixture_manifest_is_complete_and_matches_cutoff_groups() -> None:
    module = _load_module()
    fixture_data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    cutoff_data = json.loads(CUTOFFS.read_text(encoding="utf-8"))

    assert module.validate_fixture_manifest(fixture_data, cutoff_data) == []
    assert fixture_data["fixture_count"] == 40
    assert len(fixture_data["official_team_labels"]) == 21
    assert len(fixture_data["source_identity_team_keys"]) == 20
    assert fixture_data["source_label_aliases"] == {"Newcastle": "Newcastle United"}


def test_ten_fixtures_per_matchweek() -> None:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))

    counts: dict[str, int] = {}
    for fixture in data["fixtures"]:
        matchweek = fixture["matchweek"]
        counts[matchweek] = counts.get(matchweek, 0) + 1

    assert counts == {"MW1": 10, "MW2": 10, "MW3": 10, "MW4": 10}


def test_source_alias_does_not_become_canonical_identity() -> None:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))

    newcastle_fixture = next(
        fixture for fixture in data["fixtures"] if fixture["official_home_name"] == "Newcastle"
    )
    assert newcastle_fixture["source_identity_home_key"] == "Newcastle United"
    assert newcastle_fixture["canonical_event_id"] is None


def test_fixture_identity_starts_unresolved() -> None:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))

    assert all(fixture["canonical_event_id"] is None for fixture in data["fixtures"])
    assert all(fixture["provider_event_ids"] == {} for fixture in data["fixtures"])


def test_first_and_last_fixture_regression() -> None:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))

    first = data["fixtures"][0]
    assert first["official_home_name"] == "Man Utd"
    assert first["official_away_name"] == "Fulham"
    assert first["kickoff_utc"] == "2024-08-16T19:00:00Z"
    assert first["kickoff_group_id"] == "MW1_G01"

    last = data["fixtures"][-1]
    assert last["official_home_name"] == "Wolves"
    assert last["official_away_name"] == "Newcastle United"
    assert last["kickoff_utc"] == "2024-09-15T15:30:00Z"
    assert last["kickoff_group_id"] == "MW4_G23"
