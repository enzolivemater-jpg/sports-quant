#!/usr/bin/env python3
"""Validate the EPL 2024/25 Stage A fixture identity manifest."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_MANIFEST = ROOT / "data" / "manifests" / "football_odds_stage_a_epl_2024_25_fixtures.json"
CUTOFF_MANIFEST = ROOT / "data" / "manifests" / "football_odds_stage_a_epl_2024_25.json"

EXPECTED_FIXTURES = 40
EXPECTED_MATCHWEEKS = {"MW1", "MW2", "MW3", "MW4"}
EXPECTED_FIXTURES_PER_MATCHWEEK = 10


def _parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError(f"Expected UTC Z timestamp, got {value!r}")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_fixture_manifest(
    fixture_data: dict[str, Any],
    cutoff_data: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    fixtures = fixture_data.get("fixtures")
    groups = cutoff_data.get("kickoff_groups")

    if not isinstance(fixtures, list) or len(fixtures) != EXPECTED_FIXTURES:
        return [f"Expected {EXPECTED_FIXTURES} fixtures"]
    if not isinstance(groups, list):
        return ["Missing cutoff kickoff_groups"]

    group_map = {
        group["group_id"]: group["kickoff_utc"]
        for group in groups
        if isinstance(group, dict)
        and isinstance(group.get("group_id"), str)
        and isinstance(group.get("kickoff_utc"), str)
    }

    matchweek_counts: Counter[str] = Counter()
    team_week_counts: Counter[tuple[str, str]] = Counter()
    fixture_keys: set[tuple[str, str, str]] = set()

    for fixture in fixtures:
        matchweek = fixture.get("matchweek")
        home = fixture.get("official_home_name")
        away = fixture.get("official_away_name")
        home_key = fixture.get("source_identity_home_key")
        away_key = fixture.get("source_identity_away_key")
        kickoff_utc = fixture.get("kickoff_utc")
        group_id = fixture.get("kickoff_group_id")

        if (
            not isinstance(matchweek, str)
            or not isinstance(home, str)
            or not isinstance(away, str)
            or not isinstance(home_key, str)
            or not isinstance(away_key, str)
            or not isinstance(kickoff_utc, str)
            or not isinstance(group_id, str)
        ):
            errors.append("Fixture has missing/invalid identity fields")
            continue

        if matchweek not in EXPECTED_MATCHWEEKS:
            errors.append(f"Unexpected matchweek: {matchweek}")
        if home == away:
            errors.append(f"Self-match detected: {home}")
        if group_id not in group_map:
            errors.append(f"Unknown kickoff_group_id: {group_id}")
        elif group_map[group_id] != kickoff_utc:
            errors.append(f"{home} v {away}: kickoff does not match {group_id}")

        _parse_utc(kickoff_utc)
        matchweek_counts[matchweek] += 1
        team_week_counts[(matchweek, home_key)] += 1
        team_week_counts[(matchweek, away_key)] += 1

        key = (home, away, kickoff_utc)
        if key in fixture_keys:
            errors.append(f"Duplicate fixture identity: {key}")
        fixture_keys.add(key)

        if fixture.get("canonical_event_id") is not None:
            errors.append(f"{home} v {away}: canonical_event_id must remain null before F4")
        provider_ids = fixture.get("provider_event_ids")
        if provider_ids != {}:
            errors.append(f"{home} v {away}: provider_event_ids must start empty")

    for matchweek in EXPECTED_MATCHWEEKS:
        if matchweek_counts[matchweek] != EXPECTED_FIXTURES_PER_MATCHWEEK:
            errors.append(
                f"{matchweek}: expected {EXPECTED_FIXTURES_PER_MATCHWEEK} fixtures, "
                f"got {matchweek_counts[matchweek]}"
            )

    duplicates = [
        f"{matchweek}/{team}" for (matchweek, team), count in team_week_counts.items() if count != 1
    ]
    if duplicates:
        errors.append(
            "Each team must appear exactly once per matchweek; violations: "
            + ", ".join(sorted(duplicates))
        )

    if len(team_week_counts) != 80:
        errors.append("Expected 20 source-identity teams across each of 4 matchweeks")

    source_identity_team_keys = fixture_data.get("source_identity_team_keys")
    if not isinstance(source_identity_team_keys, list) or len(source_identity_team_keys) != 20:
        errors.append("Expected 20 source_identity_team_keys")

    aliases = fixture_data.get("source_label_aliases")
    if aliases != {"Newcastle": "Newcastle United"}:
        errors.append("Unexpected source label alias map")

    if fixture_data.get("fixture_count") != EXPECTED_FIXTURES:
        errors.append("fixture_count metadata mismatch")

    return errors


def main() -> int:
    fixture_data = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))
    cutoff_data = json.loads(CUTOFF_MANIFEST.read_text(encoding="utf-8"))
    errors = validate_fixture_manifest(fixture_data, cutoff_data)

    if errors:
        for error in errors:
            print(f"Fixture manifest error: {error}")
        return 1

    print("Stage A fixture identity manifest: PASS (40 fixtures, MW1-MW4)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
