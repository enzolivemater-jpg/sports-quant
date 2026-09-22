from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "research" / "reconcile_odds_stage_a.py"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("reconcile_odds_stage_a", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _fixture_manifest() -> dict[str, object]:
    return {
        "fixtures": [
            {
                "fixture_index": 1,
                "official_home_name": "Man Utd",
                "official_away_name": "Fulham",
                "source_identity_home_key": "Man Utd",
                "source_identity_away_key": "Fulham",
                "kickoff_utc": "2024-08-16T19:00:00Z",
                "kickoff_group_id": "MW1_G01",
            },
            {
                "fixture_index": 2,
                "official_home_name": "Arsenal",
                "official_away_name": "Wolves",
                "source_identity_home_key": "Arsenal",
                "source_identity_away_key": "Wolves",
                "kickoff_utc": "2024-08-17T14:00:00Z",
                "kickoff_group_id": "MW1_G03",
            },
            {
                "fixture_index": 3,
                "official_home_name": "Everton",
                "official_away_name": "Brighton",
                "source_identity_home_key": "Everton",
                "source_identity_away_key": "Brighton",
                "kickoff_utc": "2024-08-17T14:00:00Z",
                "kickoff_group_id": "MW1_G03",
            },
        ]
    }


def _provider_payload() -> dict[str, object]:
    return {
        "timestamp": "2024-08-16T18:00:00Z",
        "data": [
            {
                "id": "provider-1",
                "commence_time": "2024-08-16T19:00:00Z",
                "home_team": "Manchester United",
                "away_team": "Fulham",
            },
            {
                "id": "provider-2",
                "commence_time": "2024-08-17T14:00:00Z",
                "home_team": "Arsenal",
                "away_team": "Wolverhampton Wanderers",
            },
            {
                "id": "provider-3",
                "commence_time": "2024-08-17T14:00:00Z",
                "home_team": "Everton",
                "away_team": "Brighton and Hove Albion",
            },
            {
                "id": "other-event",
                "commence_time": "2024-08-18T20:00:00Z",
                "home_team": "Other A",
                "away_team": "Other B",
            },
        ],
    }


def test_without_alias_map_every_fixture_remains_unresolved() -> None:
    module = _load_module()

    report = module.reconcile(_fixture_manifest(), _provider_payload(), {})

    assert report["resolved_fixture_count"] == 0
    assert report["unresolved_fixture_count"] == 3
    assert report["fuzzy_matching_used"] is False
    assert report["canonical_ids_assigned"] is False


def test_explicit_alias_map_resolves_exact_home_away_pairs() -> None:
    module = _load_module()
    aliases = {
        "Manchester United": "Man Utd",
        "Fulham": "Fulham",
        "Arsenal": "Arsenal",
        "Wolverhampton Wanderers": "Wolves",
        "Everton": "Everton",
        "Brighton and Hove Albion": "Brighton",
    }

    report = module.reconcile(_fixture_manifest(), _provider_payload(), aliases)

    assert report["resolved_fixture_count"] == 3
    assert report["unresolved_fixture_count"] == 0
    assert {item["provider_event_id"] for item in report["resolved_pairs"]} == {
        "provider-1",
        "provider-2",
        "provider-3",
    }


def test_provider_event_outside_official_kickoffs_is_reported() -> None:
    module = _load_module()

    report = module.reconcile(_fixture_manifest(), _provider_payload(), {})

    outside = report["provider_events_outside_manifest"]
    assert len(outside) == 1
    assert outside[0]["provider_event_id"] == "other-event"


def test_same_kickoff_group_does_not_force_match_without_alias_evidence() -> None:
    module = _load_module()
    aliases = {
        "Arsenal": "Arsenal",
        "Wolverhampton Wanderers": "Wolves",
    }

    report = module.reconcile(_fixture_manifest(), _provider_payload(), aliases)

    resolved = {item["provider_event_id"] for item in report["resolved_pairs"]}
    assert resolved == {"provider-2"}
    assert report["unresolved_fixture_count"] == 2
