#!/usr/bin/env python3
"""Research-only reconciliation of The Odds API events to the Stage A EPL fixture manifest.

No fuzzy matching is performed. Provider IDs remain research evidence and are
never written back as canonical SPORTS QUANT entity IDs by this tool.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_MANIFEST = (
    ROOT / "data" / "manifests" / "football_odds_stage_a_epl_2024_25_fixtures.json"
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _provider_events(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        events = payload["data"]
    elif isinstance(payload, list):
        events = payload
    else:
        raise ValueError("Expected The Odds API historical wrapper with data[] or an event list")

    result: list[dict[str, Any]] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        event_id = event.get("id")
        commence_time = event.get("commence_time")
        home_team = event.get("home_team")
        away_team = event.get("away_team")
        if not all(isinstance(value, str) and value for value in (event_id, commence_time, home_team, away_team)):
            continue
        result.append(
            {
                "provider_event_id": event_id,
                "commence_time": commence_time,
                "provider_home_team": home_team,
                "provider_away_team": away_team,
            }
        )
    return result


def _load_alias_map(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    data = _load_json(path)
    if not isinstance(data, dict):
        raise ValueError("Alias map must be a JSON object mapping provider label -> source identity key")
    result: dict[str, str] = {}
    for provider_label, source_key in data.items():
        if not isinstance(provider_label, str) or not isinstance(source_key, str):
            raise ValueError("Alias-map keys and values must be strings")
        if not provider_label or not source_key:
            raise ValueError("Alias-map keys and values must be non-empty")
        result[provider_label] = source_key
    return result


def reconcile(
    fixture_manifest: dict[str, Any],
    provider_payload: Any,
    alias_map: dict[str, str],
) -> dict[str, Any]:
    fixtures = fixture_manifest.get("fixtures")
    if not isinstance(fixtures, list):
        raise ValueError("Fixture manifest is missing fixtures[]")

    official_by_kickoff: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fixture in fixtures:
        if isinstance(fixture, dict) and isinstance(fixture.get("kickoff_utc"), str):
            official_by_kickoff[fixture["kickoff_utc"]].append(fixture)

    provider_events = _provider_events(provider_payload)
    provider_by_kickoff: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in provider_events:
        provider_by_kickoff[event["commence_time"]].append(event)

    groups: list[dict[str, Any]] = []
    resolved_pairs: list[dict[str, Any]] = []
    unresolved_fixture_count = 0

    for kickoff_utc in sorted(official_by_kickoff):
        expected = official_by_kickoff[kickoff_utc]
        observed = provider_by_kickoff.get(kickoff_utc, [])

        if not observed:
            group_status = "NO_PROVIDER_EVENTS"
        elif len(observed) != len(expected):
            group_status = "COUNT_MISMATCH"
        else:
            group_status = "KICKOFF_CANDIDATES"

        unmatched_provider_ids = {event["provider_event_id"] for event in observed}
        fixture_results: list[dict[str, Any]] = []

        for fixture in expected:
            home_key = fixture["source_identity_home_key"]
            away_key = fixture["source_identity_away_key"]

            candidates: list[dict[str, Any]] = []
            for event in observed:
                mapped_home = alias_map.get(event["provider_home_team"])
                mapped_away = alias_map.get(event["provider_away_team"])
                if mapped_home == home_key and mapped_away == away_key:
                    candidates.append(event)

            if len(candidates) == 1:
                matched = candidates[0]
                status = "RESOLVED_EXACT_ALIAS"
                unmatched_provider_ids.discard(matched["provider_event_id"])
                resolved_pairs.append(
                    {
                        "fixture_index": fixture["fixture_index"],
                        "provider_event_id": matched["provider_event_id"],
                        "kickoff_utc": kickoff_utc,
                        "resolution_basis": "EXACT_PROVIDER_LABEL_ALIAS_AND_KICKOFF",
                    }
                )
            elif len(candidates) > 1:
                status = "AMBIGUOUS_ALIAS_MATCH"
                unresolved_fixture_count += 1
            else:
                status = "UNRESOLVED"
                unresolved_fixture_count += 1

            fixture_results.append(
                {
                    "fixture_index": fixture["fixture_index"],
                    "official_home_name": fixture["official_home_name"],
                    "official_away_name": fixture["official_away_name"],
                    "source_identity_home_key": home_key,
                    "source_identity_away_key": away_key,
                    "status": status,
                    "provider_candidates": candidates,
                }
            )

        groups.append(
            {
                "kickoff_utc": kickoff_utc,
                "kickoff_group_ids": sorted({fixture["kickoff_group_id"] for fixture in expected}),
                "expected_fixture_count": len(expected),
                "provider_event_count": len(observed),
                "group_status": group_status,
                "fixture_results": fixture_results,
                "unmatched_provider_event_ids": sorted(unmatched_provider_ids),
            }
        )

    official_kickoffs = set(official_by_kickoff)
    provider_events_outside_manifest = [
        event for event in provider_events if event["commence_time"] not in official_kickoffs
    ]

    return {
        "research_only": True,
        "provider": "THE_ODDS_API",
        "canonical_ids_assigned": False,
        "fuzzy_matching_used": False,
        "alias_map_entries": len(alias_map),
        "expected_fixture_count": len(fixtures),
        "provider_event_count_total": len(provider_events),
        "resolved_fixture_count": len(resolved_pairs),
        "unresolved_fixture_count": unresolved_fixture_count,
        "resolved_pairs": resolved_pairs,
        "groups": groups,
        "provider_events_outside_manifest": provider_events_outside_manifest,
        "warning": (
            "Resolved pairs are research reconciliation evidence only. "
            "They do not assign canonical SPORTS QUANT entity IDs."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-only", action="store_true", required=True)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--alias-map", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.research_only:
        print("This reconciler may only run in research-only mode.", file=sys.stderr)
        return 2

    try:
        fixture_manifest = _load_json(FIXTURE_MANIFEST)
        provider_payload = _load_json(args.payload)
        alias_map = _load_alias_map(args.alias_map)
        report = reconcile(fixture_manifest, provider_payload, alias_map)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Reconciliation error: {exc}", file=sys.stderr)
        return 1

    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output is None:
        print(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote reconciliation report: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
