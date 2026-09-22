#!/usr/bin/env python3
"""Validate the committed EPL 2024/25 historical-odds Stage A manifest."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = (
    ROOT / "data" / "manifests" / "football_odds_stage_a_epl_2024_25.json"
)

EXPECTED_GROUPS = 23
EXPECTED_CUTOFFS = ("T-24h", "T-1h", "T-15m")
EXPECTED_QUERIES = EXPECTED_GROUPS * len(EXPECTED_CUTOFFS)


def _parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError(f"Expected UTC Z timestamp, got {value!r}")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError(f"Naive timestamp not allowed: {value!r}")
    return parsed


def validate_manifest(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    groups = data.get("kickoff_groups")
    queries = data.get("query_plan")
    if not isinstance(groups, list) or len(groups) != EXPECTED_GROUPS:
        errors.append(f"Expected {EXPECTED_GROUPS} kickoff groups")
        return errors
    if not isinstance(queries, list) or len(queries) != EXPECTED_QUERIES:
        errors.append(f"Expected {EXPECTED_QUERIES} query records")
        return errors

    if data.get("planned_query_count") != EXPECTED_QUERIES:
        errors.append("planned_query_count mismatch")
    if tuple(data.get("cutoffs_per_group", ())) != EXPECTED_CUTOFFS:
        errors.append("Unexpected cutoff set/order")

    expected_pairs: set[tuple[str, str]] = set()
    for group in groups:
        group_id = group.get("group_id")
        kickoff_utc = group.get("kickoff_utc")
        group_cutoffs = group.get("cutoffs")
        if not isinstance(group_id, str) or not group_id:
            errors.append("Missing group_id")
            continue
        if not isinstance(kickoff_utc, str):
            errors.append(f"{group_id}: missing kickoff_utc")
            continue
        if not isinstance(group_cutoffs, dict):
            errors.append(f"{group_id}: missing cutoffs")
            continue

        kickoff = _parse_utc(kickoff_utc)
        for cutoff_name in EXPECTED_CUTOFFS:
            value = group_cutoffs.get(cutoff_name)
            if not isinstance(value, str):
                errors.append(f"{group_id}: missing {cutoff_name}")
                continue
            cutoff = _parse_utc(value)
            if cutoff >= kickoff:
                errors.append(f"{group_id}: {cutoff_name} must be before kickoff")
            expected_pairs.add((group_id, cutoff_name))

    query_pairs: set[tuple[str, str]] = set()
    for query in queries:
        group_id = query.get("group_id")
        cutoff = query.get("cutoff")
        timestamp = query.get("requested_snapshot_at_utc")
        if not isinstance(group_id, str) or not isinstance(cutoff, str):
            errors.append("Query missing group_id/cutoff")
            continue
        if not isinstance(timestamp, str):
            errors.append(f"{group_id}/{cutoff}: missing requested timestamp")
            continue
        _parse_utc(timestamp)
        query_pairs.add((group_id, cutoff))

    if query_pairs != expected_pairs:
        errors.append("Query plan does not exactly cover every group/cutoff pair once")
    if len(query_pairs) != len(queries):
        errors.append("Duplicate group/cutoff query pair detected")

    return errors


def main() -> int:
    if not MANIFEST.is_file():
        print(f"Missing manifest: {MANIFEST.relative_to(ROOT)}")
        return 1

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    errors = validate_manifest(data)
    if errors:
        for error in errors:
            print(f"Stage A manifest error: {error}")
        return 1

    print(
        "Stage A manifest: PASS "
        f"({EXPECTED_GROUPS} kickoff groups, {EXPECTED_QUERIES} planned historical snapshots)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
