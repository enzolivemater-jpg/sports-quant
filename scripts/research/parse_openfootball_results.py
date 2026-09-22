#!/usr/bin/env python3
"""Research-only parser for OpenFootball Football.TXT result files.

This tool is intentionally outside the production Football Data Layer.
It does not assign canonical entity IDs or known_at.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

DATE_RE = re.compile(
    r"^\s{2}(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+"
    r"(?P<month>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})(?:\s+(?P<year>\d{4}))?\s*$"
)
MATCHDAY_RE = re.compile(r"^▪\s+Matchday\s+(?P<matchday>\d+)\s*$")
MATCH_RE = re.compile(
    r"^\s{4}(?:(?P<time>\d{1,2}:\d{2})\s+)?"
    r"(?P<home>.+?)\s+v\s+(?P<away>.+?)\s+"
    r"(?P<hg>\d+)-(?P<ag>\d+)"
    r"(?:\s+\((?P<hhg>\d+)-(?P<hag>\d+)\))?\s*$"
)

MONTHS = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def _event_time_utc(date_text: str, kickoff: str, timezone_name: str) -> str:
    local_dt = datetime.strptime(f"{date_text} {kickoff}", "%Y-%m-%d %H:%M").replace(
        tzinfo=ZoneInfo(timezone_name)
    )
    return local_dt.astimezone(ZoneInfo("UTC")).isoformat().replace("+00:00", "Z")


def parse_openfootball(
    text: str,
    *,
    timezone_name: str,
    expected_matches: int | None = None,
) -> list[dict[str, Any]]:
    """Parse a completed-season Football.TXT file into research rows."""
    matches: list[dict[str, Any]] = []
    current_matchday: int | None = None
    current_date: str | None = None
    current_year: int | None = None
    current_time: str | None = None

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip()

        matchday_match = MATCHDAY_RE.match(line)
        if matchday_match:
            current_matchday = int(matchday_match.group("matchday"))
            continue

        date_match = DATE_RE.match(line)
        if date_match:
            explicit_year = date_match.group("year")
            if explicit_year is not None:
                current_year = int(explicit_year)
            if current_year is None:
                raise ValueError(
                    f"Line {line_number}: date has no year before any explicit year was observed"
                )

            month_name = date_match.group("month")
            month = MONTHS.get(month_name)
            if month is None:
                raise ValueError(f"Line {line_number}: unsupported month {month_name!r}")

            day = int(date_match.group("day"))
            current_date = f"{current_year:04d}-{month:02d}-{day:02d}"
            current_time = None
            continue

        match = MATCH_RE.match(line)
        if not match:
            continue

        if current_matchday is None:
            raise ValueError(f"Line {line_number}: match appears before a Matchday")
        if current_date is None:
            raise ValueError(f"Line {line_number}: match appears before a date")

        explicit_time = match.group("time")
        if explicit_time is not None:
            current_time = explicit_time
        if current_time is None:
            raise ValueError(
                f"Line {line_number}: match has no kickoff time and no prior time to inherit"
            )

        home = match.group("home").strip()
        away = match.group("away").strip()
        if not home or not away:
            raise ValueError(f"Line {line_number}: empty team name")

        half_home = match.group("hhg")
        half_away = match.group("hag")

        matches.append(
            {
                "matchday": current_matchday,
                "date_local": current_date,
                "kickoff_local": current_time,
                "timezone_assumption": timezone_name,
                "event_time_utc": _event_time_utc(current_date, current_time, timezone_name),
                "home_team": home,
                "away_team": away,
                "home_goals": int(match.group("hg")),
                "away_goals": int(match.group("ag")),
                "home_ht_goals": int(half_home) if half_home is not None else None,
                "away_ht_goals": int(half_away) if half_away is not None else None,
                "source_line_number": line_number,
            }
        )

    if expected_matches is not None and len(matches) != expected_matches:
        raise ValueError(f"Expected {expected_matches} matches, parsed {len(matches)}")

    identities = [
        (
            row["event_time_utc"],
            row["home_team"],
            row["away_team"],
        )
        for row in matches
    ]
    if len(identities) != len(set(identities)):
        raise ValueError("Duplicate research match identity detected")

    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-only", action="store_true", required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timezone", required=True)
    parser.add_argument("--source-repository", required=True)
    parser.add_argument("--source-path", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--expected-matches", type=int)
    args = parser.parse_args()

    if not args.research_only:
        print("This parser may only run in research-only mode.", file=sys.stderr)
        return 2
    if not args.input.is_file():
        print(f"Input file does not exist: {args.input}", file=sys.stderr)
        return 2

    try:
        ZoneInfo(args.timezone)
        rows = parse_openfootball(
            args.input.read_text(encoding="utf-8"),
            timezone_name=args.timezone,
            expected_matches=args.expected_matches,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Parse error: {exc}", file=sys.stderr)
        return 1

    teams = sorted({str(row["home_team"]) for row in rows} | {str(row["away_team"]) for row in rows})
    output = {
        "research_only": True,
        "source": {
            "repository": args.source_repository,
            "path": args.source_path,
            "revision": args.source_revision,
        },
        "parser": "scripts/research/parse_openfootball_results.py",
        "timezone_assumption": args.timezone,
        "canonical_known_at_assigned": False,
        "canonical_entity_ids_assigned": False,
        "match_count": len(rows),
        "team_count": len(teams),
        "teams": teams,
        "matches": rows,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(f"Parsed {len(rows)} matches / {len(teams)} teams -> {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
