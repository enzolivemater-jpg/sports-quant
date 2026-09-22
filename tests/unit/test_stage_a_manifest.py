from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType

SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "research" / "validate_stage_a_manifest.py"
)
PLAN_MANIFEST = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "manifests"
    / "football_odds_stage_a_epl_2024_25.json"
)
FIXTURE_MANIFEST = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "manifests"
    / "football_odds_stage_a_epl_2024_25_fixtures.json"
)


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_stage_a_manifest", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_plan() -> dict:
    return json.loads(PLAN_MANIFEST.read_text(encoding="utf-8"))


def _load_fixtures() -> dict:
    return json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))


def test_committed_stage_a_manifests_are_valid() -> None:
    module = _load_module()
    plan = _load_plan()
    fixtures = _load_fixtures()

    assert module.validate_plan_manifest(plan) == []
    assert module.validate_fixture_manifest(fixtures, plan) == []


def test_query_timestamp_must_equal_declared_cutoff() -> None:
    module = _load_module()
    plan = _load_plan()
    plan["query_plan"][0]["requested_snapshot_at_utc"] = "2024-08-15T18:59:00Z"

    errors = module.validate_plan_manifest(plan)

    assert "Query timestamps do not exactly match every declared group cutoff" in errors


def test_cutoff_delta_must_be_exact() -> None:
    module = _load_module()
    plan = _load_plan()
    plan["kickoff_groups"][0]["cutoffs"]["T-1h"] = "2024-08-16T17:59:00Z"

    errors = module.validate_plan_manifest(plan)

    assert any("T-1h delta mismatch" in error for error in errors)


def test_fixture_kickoff_must_match_referenced_group() -> None:
    module = _load_module()
    plan = _load_plan()
    fixtures = _load_fixtures()
    fixtures["fixtures"][0]["kickoff_utc"] = "2024-08-16T18:59:00Z"

    errors = module.validate_fixture_manifest(fixtures, plan)

    assert any("kickoff does not match group" in error for error in errors)


def test_research_fixture_cannot_preassign_canonical_or_provider_ids() -> None:
    module = _load_module()
    plan = _load_plan()
    fixtures = _load_fixtures()
    fixtures["fixtures"][0]["canonical_event_id"] = "forbidden"
    fixtures["fixtures"][1]["provider_event_ids"] = {"book": "123"}

    errors = module.validate_fixture_manifest(fixtures, plan)

    assert any("canonical_event_id must remain null" in error for error in errors)
    assert any("provider_event_ids must remain an empty object" in error for error in errors)


def test_alias_target_must_resolve_to_declared_identity_key() -> None:
    module = _load_module()
    plan = _load_plan()
    fixtures = _load_fixtures()
    fixtures["source_label_aliases"]["Fake Label"] = "Missing Team"

    errors = module.validate_fixture_manifest(fixtures, plan)

    assert any("Alias target is not a declared identity key" in error for error in errors)


def test_each_matchweek_requires_ten_fixtures() -> None:
    module = _load_module()
    plan = _load_plan()
    fixtures = _load_fixtures()
    broken = copy.deepcopy(fixtures)
    broken["fixtures"][0]["matchweek"] = "MW2"

    errors = module.validate_fixture_manifest(broken, plan)

    assert any("MW1: expected 10 fixtures" in error for error in errors)
    assert any("MW2: expected 10 fixtures" in error for error in errors)
