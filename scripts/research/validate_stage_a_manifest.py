#!/usr/bin/env python3
"""Validate committed EPL 2024/25 historical-odds Stage A research manifests."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PLAN_MANIFEST = ROOT / "data" / "manifests" / "football_odds_stage_a_epl_2024_25.json"
FIXTURE_MANIFEST = ROOT / "data" / "manifests" / "football_odds_stage_a_epl_2024_25_fixtures.json"

EXPECTED_GROUPS = 23
EXPECTED_FIXTURES = 40
EXPECTED_TEAMS = 20
EXPECTED_MATCHWEEKS = ("MW1", "MW2", "MW3", "MW4")
EXPECTED_CUTOFFS = ("T-24h", "T-1h", "T-15m")
EXPECTED_QUERY_COUNT = EXPECTED_GROUPS * len(EXPECTED_CUTOFFS)
EXPECTED_DELTAS = {
    "T-24h": timedelta(hours=24),
    "T-1h": timedelta(hours=1),
    "T-15m": timedelta(minutes=15),
}


def _parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError(f"Expected UTC Z timestamp, got {value!r}")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError(f"Naive timestamp not allowed: {value!r}")
    return parsed


def _plan_groups(
    data: dict[str, Any], errors: list[str]
) -> tuple[dict[str, dict[str, Any]], set[tuple[str, str, str]]]:
    groups = data.get("kickoff_groups")
    if not isinstance(groups, list) or len(groups) != EXPECTED_GROUPS:
        errors.append(f"Expected {EXPECTED_GROUPS} kickoff groups")
        return {}, set()

    by_id: dict[str, dict[str, Any]] = {}
    expected_queries: set[tuple[str, str, str]] = set()

    for group in groups:
        if not isinstance(group, dict):
            errors.append("Kickoff group must be an object")
            continue

        group_id = group.get("group_id")
        kickoff_utc = group.get("kickoff_utc")
        cutoffs = group.get("cutoffs")

        if not isinstance(group_id, str) or not group_id:
            errors.append("Missing group_id")
            continue
        if group_id in by_id:
            errors.append(f"Duplicate group_id: {group_id}")
            continue
        by_id[group_id] = group

        if not isinstance(kickoff_utc, str):
            errors.append(f"{group_id}: missing kickoff_utc")
            continue
        if not isinstance(cutoffs, dict):
            errors.append(f"{group_id}: missing cutoffs")
            continue

        kickoff = _parse_utc(kickoff_utc)

        for cutoff_name in EXPECTED_CUTOFFS:
            value = cutoffs.get(cutoff_name)
            if not isinstance(value, str):
                errors.append(f"{group_id}: missing {cutoff_name}")
                continue

            cutoff = _parse_utc(value)
            expected_delta = EXPECTED_DELTAS[cutoff_name]
            actual_delta = kickoff - cutoff
            if actual_delta != expected_delta:
                errors.append(
                    f"{group_id}: {cutoff_name} delta mismatch "
                    f"(expected {expected_delta}, got {actual_delta})"
                )
            expected_queries.add((group_id, cutoff_name, value))

    return by_id, expected_queries


def validate_plan_manifest(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if data.get("kickoff_group_count") != EXPECTED_GROUPS:
        errors.append("kickoff_group_count mismatch")
    if tuple(data.get("cutoffs_per_group", ())) != EXPECTED_CUTOFFS:
        errors.append("Unexpected cutoff set/order")
    if data.get("planned_query_count") != EXPECTED_QUERY_COUNT:
        errors.append("planned_query_count mismatch")

    groups, expected_queries = _plan_groups(data, errors)

    queries = data.get("query_plan")
    if not isinstance(queries, list) or len(queries) != EXPECTED_QUERY_COUNT:
        errors.append(f"Expected {EXPECTED_QUERY_COUNT} query records")
        return errors

    actual_queries: set[tuple[str, str, str]] = set()
    pairs: set[tuple[str, str]] = set()

    for query in queries:
        if not isinstance(query, dict):
            errors.append("Query record must be an object")
            continue

        group_id = query.get("group_id")
        cutoff = query.get("cutoff")
        timestamp = query.get("requested_snapshot_at_utc")

        if not isinstance(group_id, str) or not isinstance(cutoff, str):
            errors.append("Query missing group_id/cutoff")
            continue
        if group_id not in groups:
            errors.append(f"Query references unknown group_id: {group_id}")
        if cutoff not in EXPECTED_CUTOFFS:
            errors.append(f"{group_id}: unexpected cutoff {cutoff!r}")
        if not isinstance(timestamp, str):
            errors.append(f"{group_id}/{cutoff}: missing requested timestamp")
            continue

        _parse_utc(timestamp)
        actual_queries.add((group_id, cutoff, timestamp))
        pairs.add((group_id, cutoff))

    if actual_queries != expected_queries:
        errors.append("Query timestamps do not exactly match every declared group cutoff")
    if len(pairs) != len(queries):
        errors.append("Duplicate group/cutoff query pair detected")

    return errors


def validate_fixture_manifest(data: dict[str, Any], plan_data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    plan_errors: list[str] = []
    groups, _ = _plan_groups(plan_data, plan_errors)
    if plan_errors:
        return ["Cannot validate fixtures against invalid plan manifest", *plan_errors]

    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != EXPECTED_FIXTURES:
        errors.append(f"Expected {EXPECTED_FIXTURES} fixture records")
        return errors
    if data.get("fixture_count") != EXPECTED_FIXTURES:
        errors.append("fixture_count mismatch")
    if tuple(data.get("matchweeks", ())) != EXPECTED_MATCHWEEKS:
        errors.append("Unexpected matchweek set/order")

    indices: set[int] = set()
    identities: set[tuple[str, str, str]] = set()
    week_counts: Counter[str] = Counter()
    observed_identity_keys: set[str] = set()

    for fixture in fixtures:
        if not isinstance(fixture, dict):
            errors.append("Fixture record must be an object")
            continue

        index = fixture.get("fixture_index")
        matchweek = fixture.get("matchweek")
        group_id = fixture.get("kickoff_group_id")
        kickoff_utc = fixture.get("kickoff_utc")
        home_key = fixture.get("source_identity_home_key")
        away_key = fixture.get("source_identity_away_key")

        if not isinstance(index, int):
            errors.append("Fixture missing integer fixture_index")
        elif index in indices:
            errors.append(f"Duplicate fixture_index: {index}")
        else:
            indices.add(index)

        if not isinstance(matchweek, str) or matchweek not in EXPECTED_MATCHWEEKS:
            errors.append(f"Fixture {index}: invalid matchweek")
        else:
            week_counts[matchweek] += 1

        if not isinstance(group_id, str) or group_id not in groups:
            errors.append(f"Fixture {index}: unknown kickoff_group_id")
        elif not isinstance(kickoff_utc, str):
            errors.append(f"Fixture {index}: missing kickoff_utc")
        elif groups[group_id].get("kickoff_utc") != kickoff_utc:
            errors.append(f"Fixture {index}: kickoff does not match group {group_id}")
        else:
            _parse_utc(kickoff_utc)

        if fixture.get("canonical_event_id") is not None:
            errors.append(
                f"Fixture {index}: canonical_event_id must remain null in research manifest"
            )
        provider_ids = fixture.get("provider_event_ids")
        if not isinstance(provider_ids, dict) or provider_ids:
            errors.append(f"Fixture {index}: provider_event_ids must remain an empty object")

        if not isinstance(home_key, str) or not isinstance(away_key, str):
            errors.append(f"Fixture {index}: missing source identity key")
            continue
        observed_identity_keys.update((home_key, away_key))

        if isinstance(kickoff_utc, str):
            identity = (kickoff_utc, home_key, away_key)
            if identity in identities:
                errors.append(f"Duplicate fixture identity: {identity}")
            identities.add(identity)

    if indices != set(range(1, EXPECTED_FIXTURES + 1)):
        errors.append("fixture_index must cover exactly 1..40")

    for week in EXPECTED_MATCHWEEKS:
        if week_counts[week] != 10:
            errors.append(f"{week}: expected 10 fixtures, got {week_counts[week]}")

    identity_keys = data.get("source_identity_team_keys")
    if not isinstance(identity_keys, list) or len(identity_keys) != EXPECTED_TEAMS:
        errors.append(f"Expected {EXPECTED_TEAMS} source identity team keys")
        identity_key_set: set[str] = set()
    else:
        identity_key_set = {str(value) for value in identity_keys}
        if len(identity_key_set) != EXPECTED_TEAMS:
            errors.append("source_identity_team_keys contains duplicates")

    if observed_identity_keys != identity_key_set:
        errors.append("Observed fixture team identity keys do not exactly match declared team keys")

    aliases = data.get("source_label_aliases")
    if not isinstance(aliases, dict):
        errors.append("source_label_aliases must be an object")
    else:
        for source_label, target in aliases.items():
            if not isinstance(source_label, str) or not isinstance(target, str):
                errors.append("source_label_aliases entries must be string -> string")
            elif target not in identity_key_set:
                errors.append(
                    f"Alias target is not a declared identity key: {source_label} -> {target}"
                )

    return errors


def main() -> int:
    missing = [
        path.relative_to(ROOT) for path in (PLAN_MANIFEST, FIXTURE_MANIFEST) if not path.is_file()
    ]
    if missing:
        for path in missing:
            print(f"Missing Stage A manifest: {path}")
        return 1

    plan_data = json.loads(PLAN_MANIFEST.read_text(encoding="utf-8"))
    fixture_data = json.loads(FIXTURE_MANIFEST.read_text(encoding="utf-8"))

    errors = [
        *validate_plan_manifest(plan_data),
        *validate_fixture_manifest(fixture_data, plan_data),
    ]
    if errors:
        for error in errors:
            print(f"Stage A manifest error: {error}")
        return 1

    print(
        "Stage A manifests: PASS "
        f"({EXPECTED_GROUPS} kickoff groups, {EXPECTED_QUERY_COUNT} historical snapshots, "
        f"{EXPECTED_FIXTURES} fixtures, {EXPECTED_TEAMS} team identities)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
