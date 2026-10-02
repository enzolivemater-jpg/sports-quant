"""OpenFootball Football.TXT season files -> typed normalized match records.

Experimental adapter for a research-baseline source (not an approved provider).
The grammar follows the research parser (``scripts/research/parse_openfootball_results.py``)
and adds what the data layer needs:

- every non-blank line must be recognized; anything else fails with its line number;
- date lines are checked against their weekday, catching year-rollover errors;
- local kickoff times are converted with the F3 ``localize_provider_time``, which
  rejects ambiguous/nonexistent DST wall times instead of guessing;
- ``# Matches``/``# Teams`` headers must agree with the parsed content;
- a home/away pairing may appear once per file (a league season has no duplicates);
- a modern-format fixture line without a score is a not-yet-played fixture.

Source labels are kept verbatim; no entity resolution or ``known_at`` happens here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

from sports_quant.contracts.common import Contract, ContractError, require_non_empty
from sports_quant.data.point_in_time.timezones import localize_provider_time

PARSER_VERSION = "openfootball-txt-1"

LINE_FORMAT_MODERN = "HOME_V_AWAY_SCORE"
LINE_FORMAT_LEGACY = "HOME_SCORE_AWAY"

_TITLE_RE = re.compile(r"^=\s+(?P<title>.+?)\s*$")
_SEASON_RE = re.compile(r"(?P<season>\d{4}/\d{2})$")
_HEADER_RE = re.compile(r"^#\s+(?P<key>[A-Za-z]+)\s+(?P<value>.+?)\s*$")
_DATE_RANGE_RE = re.compile(
    r"^(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+[A-Z][a-z]{2}\s+\d{1,2}\s+(?P<start_year>\d{4})\s+-\s+"
)
_MATCHDAY_RE = re.compile(r"^▪\s+Matchday\s+(?P<matchday>\d+)\s*$")
_DATE_RE = re.compile(
    r"^\s*(?P<weekday>Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+"
    r"(?P<month>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})(?:\s+(?P<year>\d{4}))?\s*$"
)
_MODERN_RE = re.compile(
    r"^\s+(?:(?P<time>\d{1,2}:\d{2})\s+)?"
    r"(?P<home>.+?)\s+v\s+(?P<away>.+?)"
    r"(?:\s+(?P<hg>\d+)-(?P<ag>\d+)(?:\s+\((?P<hhg>\d+)-(?P<hag>\d+)\))?)?\s*$"
)
_LEGACY_RE = re.compile(
    r"^\s+(?:(?P<time>\d{1,2}:\d{2})\s+)?"
    r"(?P<home>.+?)\s+(?P<hg>\d+)-(?P<ag>\d+)"
    r"(?:\s+\((?P<hhg>\d+)-(?P<hag>\d+)\))?\s+(?P<away>.+?)\s*$"
)
_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
_WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


@dataclass(frozen=True, kw_only=True)
class OpenFootballMatch(Contract):
    """One match line. Goals are ``None`` exactly when the source gives no score."""

    matchday: int
    date_local: str
    kickoff_local: str
    timezone_name: str
    event_time: datetime
    home_label: str
    away_label: str
    home_goals: int | None
    away_goals: int | None
    home_ht_goals: int | None
    away_ht_goals: int | None
    line_number: int
    line_format: str

    def _validate(self) -> None:
        require_non_empty(self.home_label, "home_label")
        require_non_empty(self.away_label, "away_label")
        if (self.home_goals is None) != (self.away_goals is None):
            raise ContractError("PARTIAL_SCORE", "full-time score must be complete or absent")
        if (self.home_ht_goals is None) != (self.away_ht_goals is None):
            raise ContractError("PARTIAL_SCORE", "half-time score must be complete or absent")
        if self.home_goals is None and self.home_ht_goals is not None:
            raise ContractError("PARTIAL_SCORE", "half-time score without full-time score")


@dataclass(frozen=True, kw_only=True)
class OpenFootballSeasonFile(Contract):
    title: str
    season_label: str
    header_teams: int | None
    header_matches: int | None
    matches: tuple[OpenFootballMatch, ...]


def _fail(code: str, line_number: int, message: str) -> ContractError:
    return ContractError(code, f"line {line_number}: {message}")


def parse_season_file(payload: bytes, *, timezone_name: str) -> OpenFootballSeasonFile:
    """Parse one completed or in-progress season file. Fails on anything unexpected."""

    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError("PAYLOAD_NOT_UTF8", "OpenFootball files are UTF-8") from exc

    title: str | None = None
    season_label: str | None = None
    headers: dict[str, str] = {}
    matchday: int | None = None
    current_date: date | None = None
    current_year: int | None = None
    previous_month: int | None = None
    current_time: str | None = None
    matches: list[OpenFootballMatch] = []
    pairings: dict[tuple[str, str], int] = {}

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip()
        if not line.strip():
            continue

        if title is None:
            title_match = _TITLE_RE.match(line)
            season_match = _SEASON_RE.search(title_match.group("title")) if title_match else None
            if title_match is None or season_match is None:
                raise _fail("MISSING_TITLE", line_number, "expected '= <Competition> YYYY/YY'")
            title = title_match.group("title")
            season_label = season_match.group("season")
            continue

        header = _HEADER_RE.match(line)
        if header:
            key, value = header.group("key"), header.group("value")
            if key in headers:
                raise _fail("DUPLICATE_HEADER", line_number, f"header {key!r} repeated")
            headers[key] = value
            if key == "Date":
                date_range = _DATE_RANGE_RE.match(value)
                if date_range is None:
                    raise _fail("MALFORMED_LINE", line_number, "unrecognized # Date range")
                current_year = int(date_range.group("start_year"))
            continue

        matchday_match = _MATCHDAY_RE.match(line)
        if matchday_match:
            matchday = int(matchday_match.group("matchday"))
            continue

        date_match = _DATE_RE.match(line)
        if date_match:
            if date_match.group("month") not in _MONTHS:
                raise _fail("INVALID_DATE", line_number, "unknown month")
            month = _MONTHS.index(date_match.group("month")) + 1
            if date_match.group("year") is not None:
                current_year = int(date_match.group("year"))
            elif current_year is None:
                raise _fail("INVALID_DATE", line_number, "date without a known year")
            elif previous_month is not None and month < previous_month:
                current_year += 1
            try:
                current_date = date(current_year, month, int(date_match.group("day")))
            except ValueError:
                raise _fail("INVALID_DATE", line_number, "no such calendar date") from None
            if _WEEKDAYS[current_date.weekday()] != date_match.group("weekday"):
                raise _fail("WEEKDAY_MISMATCH", line_number, f"{current_date} weekday differs")
            previous_month = month
            current_time = None
            continue

        modern = _MODERN_RE.match(line)
        legacy = None if modern else _LEGACY_RE.match(line)
        parsed = modern or legacy
        if parsed is None:
            raise _fail("MALFORMED_LINE", line_number, f"unrecognized line {line.strip()!r}")
        if matchday is None:
            raise _fail("MATCH_BEFORE_MATCHDAY", line_number, "match before any Matchday")
        if current_date is None:
            raise _fail("MATCH_BEFORE_DATE", line_number, "match before any date")
        if parsed.group("time") is not None:
            current_time = parsed.group("time")
        if current_time is None:
            raise _fail("MISSING_KICKOFF_TIME", line_number, "no kickoff time to apply")

        home = parsed.group("home").strip()
        away = parsed.group("away").strip()
        if home == away:
            raise _fail("SAME_TEAM_FIXTURE", line_number, f"{home!r} plays itself")
        if (home, away) in pairings:
            raise _fail(
                "DUPLICATE_FIXTURE",
                line_number,
                f"{home} v {away} already on line {pairings[(home, away)]}",
            )
        pairings[(home, away)] = line_number

        hour, minute = (int(part) for part in current_time.split(":"))
        try:
            wall_time = datetime(current_date.year, current_date.month, current_date.day)
            wall_time = wall_time.replace(hour=hour, minute=minute)
        except ValueError:
            raise _fail("INVALID_TIME", line_number, f"invalid kickoff {current_time}") from None
        try:
            event_time = localize_provider_time(wall_time, timezone_name)
        except ContractError as exc:
            raise _fail(exc.code, line_number, str(exc)) from exc

        matches.append(
            OpenFootballMatch(
                matchday=matchday,
                date_local=current_date.isoformat(),
                kickoff_local=f"{hour:02d}:{minute:02d}",
                timezone_name=timezone_name,
                event_time=event_time,
                home_label=home,
                away_label=away,
                home_goals=_int_or_none(parsed.group("hg")),
                away_goals=_int_or_none(parsed.group("ag")),
                home_ht_goals=_int_or_none(parsed.group("hhg")),
                away_ht_goals=_int_or_none(parsed.group("hag")),
                line_number=line_number,
                line_format=LINE_FORMAT_MODERN if modern else LINE_FORMAT_LEGACY,
            )
        )

    if title is None or season_label is None:
        raise ContractError("MISSING_TITLE", "empty OpenFootball file")
    header_matches = _header_int(headers, "Matches")
    header_teams = _header_int(headers, "Teams")
    if header_matches is not None and header_matches != len(matches):
        raise ContractError(
            "MATCH_COUNT_MISMATCH", f"header says {header_matches}, parsed {len(matches)}"
        )
    teams = {m.home_label for m in matches} | {m.away_label for m in matches}
    if header_teams is not None and header_teams != len(teams):
        raise ContractError(
            "TEAM_COUNT_MISMATCH", f"header says {header_teams}, parsed {len(teams)}"
        )
    return OpenFootballSeasonFile(
        title=title,
        season_label=season_label,
        header_teams=header_teams,
        header_matches=header_matches,
        matches=tuple(matches),
    )


def _int_or_none(value: str | None) -> int | None:
    return int(value) if value is not None else None


def _header_int(headers: dict[str, str], key: str) -> int | None:
    value = headers.get(key)
    if value is None:
        return None
    if not value.isdigit():
        raise ContractError("MALFORMED_HEADER", f"# {key} must be an integer, got {value!r}")
    return int(value)
