from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "research"
    / "analyze_odds_stage_a_snapshot.py"
)


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("analyze_odds_stage_a_snapshot", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _payload() -> dict[str, object]:
    return {
        "timestamp": "2024-08-16T17:55:00Z",
        "previous_timestamp": "2024-08-16T17:50:00Z",
        "next_timestamp": "2024-08-16T18:00:00Z",
        "data": [
            {
                "id": "provider-1",
                "commence_time": "2024-08-16T19:00:00Z",
                "home_team": "Manchester United",
                "away_team": "Fulham",
                "bookmakers": [
                    {
                        "key": "book-a",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Manchester United", "price": 1.5},
                                    {"name": "Draw", "price": 4.0},
                                    {"name": "Fulham", "price": 6.0},
                                ],
                            },
                            {
                                "key": "totals",
                                "outcomes": [
                                    {"name": "Over", "point": 2.5, "price": 1.9},
                                    {"name": "Under", "point": 2.5, "price": 1.9},
                                ],
                            },
                        ],
                    },
                    {
                        "key": "book-b",
                        "markets": [
                            {
                                "key": "h2h",
                                "outcomes": [
                                    {"name": "Manchester United", "price": 1.52},
                                    {"name": "Draw", "price": 3.9},
                                    {"name": "Fulham", "price": 5.8},
                                ],
                            }
                        ],
                    },
                ],
            }
        ],
    }


def _metadata() -> dict[str, object]:
    return {
        "request_url_redacted": (
            "https://api.the-odds-api.com/v4/historical/sports/soccer_epl/odds?"
            "regions=eu&markets=h2h%2Ctotals&oddsFormat=decimal&"
            "date=2024-08-16T18%3A00%3A00Z&apiKey=%2A%2A%2AREDACTED%2A%2A%2A"
        ),
        "received_at": "2026-09-22T17:00:00+00:00",
        "payload_sha256": "abc123",
    }


def _reconciliation() -> dict[str, object]:
    return {
        "expected_fixture_count": 40,
        "resolved_pairs": [
            {
                "fixture_index": 1,
                "provider_event_id": "provider-1",
                "resolution_basis": "EXACT_PROVIDER_LABEL_ALIAS_AND_KICKOFF",
            }
        ],
    }


def test_snapshot_analysis_keeps_expected_40_fixture_denominator() -> None:
    module = _load_module()

    report = module.analyze_snapshot(_payload(), _metadata(), _reconciliation())

    assert report["expected_fixture_count"] == 40
    assert report["resolved_fixture_count"] == 1
    assert report["unresolved_fixture_count"] == 39
    assert report["fixture_resolution_coverage"] == 1 / 40
    assert report["h2h_coverage_expected_denominator"] == 1 / 40
    assert report["totals_coverage_expected_denominator"] == 1 / 40


def test_snapshot_lag_uses_requested_minus_provider_snapshot() -> None:
    module = _load_module()

    report = module.analyze_snapshot(_payload(), _metadata(), _reconciliation())

    assert report["requested_snapshot_at"] == "2024-08-16T18:00:00Z"
    assert report["provider_snapshot_at"] == "2024-08-16T17:55:00Z"
    assert report["snapshot_lag_seconds"] == 300.0
    assert report["snapshot_not_after_request"] is True


def test_market_coverage_does_not_calculate_no_vig_or_edge() -> None:
    module = _load_module()

    report = module.analyze_snapshot(_payload(), _metadata(), _reconciliation())

    assert report["h2h_present_count"] == 1
    assert report["complete_h2h_count"] == 1
    assert report["totals_present_count"] == 1
    assert report["no_vig_calculated"] is False
    assert report["edge_calculated"] is False
    summary = report["resolved_event_summaries"][0]
    assert summary["bookmaker_count"] == 2
    assert summary["h2h_bookmaker_count"] == 2
    assert summary["complete_h2h_bookmaker_count"] == 2
    assert summary["totals_bookmaker_count"] == 1
    assert summary["totals_distinct_points"] == [2.5]


def test_provider_snapshot_after_requested_time_is_flagged() -> None:
    module = _load_module()
    payload = _payload()
    payload["timestamp"] = "2024-08-16T18:05:00Z"

    report = module.analyze_snapshot(payload, _metadata(), _reconciliation())

    assert report["snapshot_lag_seconds"] == -300.0
    assert report["snapshot_not_after_request"] is False
