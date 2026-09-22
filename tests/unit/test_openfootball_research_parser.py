from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[2] / "scripts" / "research" / "parse_openfootball_results.py"
)


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("parse_openfootball_results", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODERN_SAMPLE = """= English Premier League 2024/25

# Date       Fri Aug 16 2024 - Sun May 25 2025 (282d)

▪ Matchday 1
  Fri Aug 16 2024
    20:00  Manchester United FC    v Fulham FC                1-0 (0-0)
  Sat Aug 17
    15:00  Arsenal FC              v Wolves FC                2-0 (1-0)
           Everton FC              v Brighton FC              0-3 (0-1)

▪ Matchday 20
  Wed Jan 1 2025
    15:00  Team A                  v Team B                    0-0
"""

LEGACY_SAMPLE = """= English Premier League 2000/01

# Date       Sat Aug 19 2000 - Sat May 19 2001 (273d)

▪ Matchday 1
Sat Aug 19
  15:00  Charlton Athletic        4-0 (2-0)  Manchester City
         Chelsea FC               4-2 (1-0)  West Ham United
Sun Aug 20
  16:00  Manchester United        2-0 (1-0)  Newcastle United

▪ Matchday 20
Mon Jan 1
  15:00  Team A                   0-0  Team B
"""


def test_modern_parser_inherits_time_and_year_state() -> None:
    module = _load_module()

    rows = module.parse_openfootball(
        MODERN_SAMPLE,
        timezone_name="Europe/London",
        expected_matches=4,
    )

    assert rows[0]["date_local"] == "2024-08-16"
    assert rows[0]["event_time_utc"] == "2024-08-16T19:00:00Z"
    assert rows[1]["date_local"] == "2024-08-17"
    assert rows[2]["kickoff_local"] == "15:00"
    assert rows[2]["event_time_utc"] == "2024-08-17T14:00:00Z"
    assert rows[3]["date_local"] == "2025-01-01"
    assert rows[3]["event_time_utc"] == "2025-01-01T15:00:00Z"
    assert {row["source_line_format"] for row in rows} == {"HOME_V_AWAY_SCORE"}


def test_legacy_parser_uses_header_year_and_rolls_over_in_january() -> None:
    module = _load_module()

    rows = module.parse_openfootball(
        LEGACY_SAMPLE,
        timezone_name="Europe/London",
        expected_matches=4,
    )

    assert rows[0]["date_local"] == "2000-08-19"
    assert rows[0]["home_team"] == "Charlton Athletic"
    assert rows[0]["away_team"] == "Manchester City"
    assert rows[1]["kickoff_local"] == "15:00"
    assert rows[2]["date_local"] == "2000-08-20"
    assert rows[3]["date_local"] == "2001-01-01"
    assert rows[3]["event_time_utc"] == "2001-01-01T15:00:00Z"
    assert {row["source_line_format"] for row in rows} == {"HOME_SCORE_AWAY"}


def test_missing_halftime_score_remains_missing_in_both_formats() -> None:
    module = _load_module()

    modern = module.parse_openfootball(MODERN_SAMPLE, timezone_name="Europe/London")
    legacy = module.parse_openfootball(LEGACY_SAMPLE, timezone_name="Europe/London")

    assert modern[3]["home_ht_goals"] is None
    assert modern[3]["away_ht_goals"] is None
    assert legacy[3]["home_ht_goals"] is None
    assert legacy[3]["away_ht_goals"] is None


def test_parser_does_not_create_known_at_or_canonical_ids() -> None:
    module = _load_module()

    rows = module.parse_openfootball(MODERN_SAMPLE, timezone_name="Europe/London")

    keys = set().union(*(row.keys() for row in rows))
    assert "known_at" not in keys
    assert "canonical_event_id" not in keys
    assert "canonical_home_team_id" not in keys


def test_match_without_time_to_inherit_is_rejected() -> None:
    module = _load_module()
    text = """= English Premier League 2024/25

# Date       Fri Aug 16 2024 - Sun May 25 2025 (282d)

▪ Matchday 1
  Fri Aug 16 2024
           Team A                  v Team B                    1-0
"""

    with pytest.raises(ValueError, match="no kickoff time"):
        module.parse_openfootball(text, timezone_name="Europe/London")


def test_expected_match_count_is_enforced() -> None:
    module = _load_module()

    with pytest.raises(ValueError, match="Expected 5 matches, parsed 4"):
        module.parse_openfootball(MODERN_SAMPLE, timezone_name="Europe/London", expected_matches=5)


def test_duplicate_match_identity_is_rejected() -> None:
    module = _load_module()
    text = """= English Premier League 2024/25

# Date       Fri Aug 16 2024 - Sun May 25 2025 (282d)

▪ Matchday 1
  Fri Aug 16 2024
    20:00  Team A                  v Team B                    1-0
           Team A                  v Team B                    1-0
"""

    with pytest.raises(ValueError, match="Duplicate research match identity"):
        module.parse_openfootball(text, timezone_name="Europe/London")


def test_date_without_year_or_header_is_rejected() -> None:
    module = _load_module()
    text = """▪ Matchday 1
Sat Aug 19
  15:00  Team A                   1-0  Team B
"""

    with pytest.raises(ValueError, match="before a season/header year"):
        module.parse_openfootball(text, timezone_name="Europe/London")
