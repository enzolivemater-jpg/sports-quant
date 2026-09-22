#!/usr/bin/env python3
"""Research-only coverage analysis for one The Odds API Stage A snapshot."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_utc(value: str) -> datetime:
    if not value.endswith("Z"):
        raise ValueError(f"Expected UTC Z timestamp, got {value!r}")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError(f"Naive timestamp not allowed: {value!r}")
    return parsed


def _requested_snapshot_at(metadata: dict[str, Any]) -> str:
    value = metadata.get("request_url_redacted")
    if not isinstance(value, str):
        raise ValueError("Capture metadata is missing request_url_redacted")
    query = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(value).query))
    requested = query.get("date")
    if not requested:
        raise ValueError("Capture metadata URL is missing historical date parameter")
    _parse_utc(requested)
    return requested


def _wrapper(payload: Any) -> tuple[str, list[dict[str, Any]]]:
    if not isinstance(payload, dict):
        raise ValueError("Expected historical wrapper object")
    timestamp = payload.get("timestamp")
    data = payload.get("data")
    if not isinstance(timestamp, str):
        raise ValueError("Historical wrapper is missing timestamp")
    if not isinstance(data, list):
        raise ValueError("Historical wrapper is missing data[]")
    _parse_utc(timestamp)
    return timestamp, [event for event in data if isinstance(event, dict)]


def _complete_h2h(market: dict[str, Any], event: dict[str, Any]) -> bool:
    outcomes = market.get("outcomes")
    if not isinstance(outcomes, list):
        return False
    names = {
        outcome.get("name")
        for outcome in outcomes
        if isinstance(outcome, dict) and isinstance(outcome.get("name"), str)
    }
    home = event.get("home_team")
    away = event.get("away_team")
    return isinstance(home, str) and isinstance(away, str) and {home, away, "Draw"} <= names


def _totals_points(market: dict[str, Any]) -> list[float]:
    outcomes = market.get("outcomes")
    if not isinstance(outcomes, list):
        return []
    points: set[float] = set()
    for outcome in outcomes:
        if not isinstance(outcome, dict):
            continue
        name = outcome.get("name")
        point = outcome.get("point")
        if name not in {"Over", "Under"}:
            continue
        if isinstance(point, int | float):
            points.add(float(point))
    return sorted(points)


def _event_market_summary(event: dict[str, Any]) -> dict[str, Any]:
    bookmakers = event.get("bookmakers")
    if not isinstance(bookmakers, list):
        bookmakers = []

    bookmaker_count = 0
    h2h_bookmakers = 0
    totals_bookmakers = 0
    complete_h2h_bookmakers = 0
    totals_points: set[float] = set()

    for bookmaker in bookmakers:
        if not isinstance(bookmaker, dict):
            continue
        bookmaker_count += 1
        markets = bookmaker.get("markets")
        if not isinstance(markets, list):
            continue

        saw_h2h = False
        saw_totals = False
        complete_h2h = False
        bookmaker_total_points: set[float] = set()

        for market in markets:
            if not isinstance(market, dict):
                continue
            key = market.get("key")
            if key == "h2h":
                saw_h2h = True
                complete_h2h = complete_h2h or _complete_h2h(market, event)
            elif key == "totals":
                saw_totals = True
                bookmaker_total_points.update(_totals_points(market))

        if saw_h2h:
            h2h_bookmakers += 1
        if saw_totals:
            totals_bookmakers += 1
        if complete_h2h:
            complete_h2h_bookmakers += 1
        totals_points.update(bookmaker_total_points)

    return {
        "provider_event_id": event.get("id"),
        "provider_home_team": event.get("home_team"),
        "provider_away_team": event.get("away_team"),
        "commence_time": event.get("commence_time"),
        "bookmaker_count": bookmaker_count,
        "h2h_bookmaker_count": h2h_bookmakers,
        "complete_h2h_bookmaker_count": complete_h2h_bookmakers,
        "totals_bookmaker_count": totals_bookmakers,
        "totals_distinct_points": sorted(totals_points),
        "h2h_present": h2h_bookmakers > 0,
        "h2h_complete_present": complete_h2h_bookmakers > 0,
        "totals_present": totals_bookmakers > 0,
    }


def _distribution(values: list[int]) -> dict[str, float | int | None]:
    if not values:
        return {"min": None, "median": None, "max": None}
    return {
        "min": min(values),
        "median": float(statistics.median(values)),
        "max": max(values),
    }


def analyze_snapshot(
    payload: Any,
    metadata: dict[str, Any],
    reconciliation: dict[str, Any],
) -> dict[str, Any]:
    provider_snapshot_at, events = _wrapper(payload)
    requested_snapshot_at = _requested_snapshot_at(metadata)

    requested_dt = _parse_utc(requested_snapshot_at)
    provider_dt = _parse_utc(provider_snapshot_at)
    snapshot_lag_seconds = (requested_dt - provider_dt).total_seconds()

    event_by_id = {
        event["id"]: event
        for event in events
        if isinstance(event.get("id"), str) and event.get("id")
    }

    expected_fixture_count = reconciliation.get("expected_fixture_count")
    resolved_pairs = reconciliation.get("resolved_pairs")
    if not isinstance(expected_fixture_count, int):
        raise ValueError("Reconciliation report is missing expected_fixture_count")
    if not isinstance(resolved_pairs, list):
        raise ValueError("Reconciliation report is missing resolved_pairs[]")

    summaries: list[dict[str, Any]] = []
    missing_resolved_provider_ids: list[str] = []

    for pair in resolved_pairs:
        if not isinstance(pair, dict):
            continue
        provider_event_id = pair.get("provider_event_id")
        fixture_index = pair.get("fixture_index")
        if not isinstance(provider_event_id, str):
            continue
        event = event_by_id.get(provider_event_id)
        if event is None:
            missing_resolved_provider_ids.append(provider_event_id)
            continue
        summary = _event_market_summary(event)
        summary["fixture_index"] = fixture_index
        summaries.append(summary)

    resolved_fixture_count = len(resolved_pairs)
    h2h_present_count = sum(bool(item["h2h_present"]) for item in summaries)
    complete_h2h_count = sum(bool(item["h2h_complete_present"]) for item in summaries)
    totals_present_count = sum(bool(item["totals_present"]) for item in summaries)
    bookmaker_counts = [int(item["bookmaker_count"]) for item in summaries]

    def ratio(numerator: int, denominator: int) -> float | None:
        return numerator / denominator if denominator else None

    return {
        "research_only": True,
        "provider": "THE_ODDS_API",
        "requested_snapshot_at": requested_snapshot_at,
        "provider_snapshot_at": provider_snapshot_at,
        "snapshot_lag_seconds": snapshot_lag_seconds,
        "snapshot_not_after_request": provider_dt <= requested_dt,
        "received_at": metadata.get("received_at"),
        "payload_sha256": metadata.get("payload_sha256"),
        "expected_fixture_count": expected_fixture_count,
        "resolved_fixture_count": resolved_fixture_count,
        "unresolved_fixture_count": expected_fixture_count - resolved_fixture_count,
        "fixture_resolution_coverage": ratio(resolved_fixture_count, expected_fixture_count),
        "resolved_event_summaries": summaries,
        "missing_resolved_provider_ids": missing_resolved_provider_ids,
        "h2h_present_count": h2h_present_count,
        "complete_h2h_count": complete_h2h_count,
        "totals_present_count": totals_present_count,
        "h2h_coverage_expected_denominator": ratio(h2h_present_count, expected_fixture_count),
        "complete_h2h_coverage_expected_denominator": ratio(
            complete_h2h_count, expected_fixture_count
        ),
        "totals_coverage_expected_denominator": ratio(
            totals_present_count, expected_fixture_count
        ),
        "bookmaker_count_distribution_resolved": _distribution(bookmaker_counts),
        "canonical_known_at_assigned": False,
        "no_vig_calculated": False,
        "edge_calculated": False,
        "warning": (
            "Coverage metrics are research evidence only. Main totals line qualification, no-vig, "
            "known_at and canonical provider roles remain unresolved."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-only", action="store_true", required=True)
    parser.add_argument("--payload", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--reconciliation", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.research_only:
        print("This analyzer may only run in research-only mode.", file=sys.stderr)
        return 2

    try:
        report = analyze_snapshot(
            _load_json(args.payload),
            _load_json(args.metadata),
            _load_json(args.reconciliation),
        )
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Coverage analysis error: {exc}", file=sys.stderr)
        return 1

    rendered = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output is None:
        print(rendered)
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote coverage report: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
