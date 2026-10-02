"""Builders for F4 Football data-layer tests.

OpenFootball samples reproduce the real 2024/25 file format and labels (first
fixtures of the pinned blob), but are short excerpts. Odds payloads are SYNTHETIC
test fixtures shaped like the documented The Odds API historical response: they
are not real prices and must never be used as data.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

from sports_quant.contracts.reproducibility import ArtifactKind, ArtifactRef, CodeVersion
from sports_quant.data.entity_resolution.football_epl import (
    EPL,
    EPL_2024_25_MAPPINGS,
    NAMESPACE_BOOKMAKER,
    NAMESPACE_COMPETITION,
    NAMESPACE_TEAM,
)
from sports_quant.data.entity_resolution.mapping import (
    EntityMapping,
    MappingMethod,
    MappingTable,
    ReviewState,
)
from sports_quant.data.ingestion.football import (
    INGESTION_VERSION,
    CaptureMode,
    FootballBuild,
    IngestionContext,
    build_football,
    openfootball_capture,
)
from sports_quant.data.provenance.sources import THE_ODDS_API
from sports_quant.data.snapshots.raw import RawCapture, capture

SEASON_PATH = "2024-25/1-premierleague.txt"
CODE = CodeVersion(commit="00a01efad79294692263e841510ab78514da51da")
DATASET = ArtifactRef(kind=ArtifactKind.SNAPSHOT, identifier="f4-test", version="1")

# Receipt instants used by tests (all after the 2024/25 season).
T1 = datetime(2026, 10, 1, 9, 0, tzinfo=UTC)
T2 = datetime(2026, 10, 2, 9, 0, tzinfo=UTC)

HEADER = """= English Premier League 2024/25

# Date       Fri Aug 16 2024 - Sun May 25 2025 (282d)
# Teams      20
# Matches    380
"""

MATCHDAY_1 = """
▪ Matchday 1
  Fri Aug 16 2024
    20:00  Manchester United FC    v Fulham FC                1-0 (0-0)
  Sat Aug 17
    12:30  Ipswich Town FC         v Liverpool FC             0-2 (0-0)
    15:00  Arsenal FC              v Wolverhampton Wanderers FC  2-0 (1-0)
           Everton FC              v Brighton & Hove Albion FC  0-3
"""


def season_text(body: str = MATCHDAY_1, header: str | None = None) -> bytes:
    """A season excerpt; the default header is trimmed of counts it would contradict."""

    if header is None:
        header = HEADER.split("# Teams")[0]
    return (header + body).encode("utf-8")


def of_capture(payload: bytes, received_at: datetime = T1) -> tuple[RawCapture, bytes]:
    return openfootball_capture(payload, season_path=SEASON_PATH, received_at=received_at), payload


ODDS_TEAM_LABELS = {
    "Manchester United": "MANCHESTER_UNITED",
    "Fulham": "FULHAM",
    "Arsenal": "ARSENAL",
    "Wolverhampton Wanderers": "WOLVERHAMPTON_WANDERERS",
}


def _test_mapping(namespace: str, external_id: str, value: str) -> EntityMapping:
    return EntityMapping(
        provider_id=THE_ODDS_API,
        namespace=namespace,
        external_id=external_id,
        canonical_value=value,
        method=MappingMethod.EXACT_EXTERNAL_ID,
        review_state=ReviewState.CURATED_PENDING_REVIEW,
        evidence="SYNTHETIC TEST MAPPING",
    )


def odds_test_mappings(*extra: EntityMapping) -> MappingTable:
    """Curated EPL table plus synthetic The Odds API labels (test only)."""

    return MappingTable(
        (
            *EPL_2024_25_MAPPINGS,
            _test_mapping(NAMESPACE_COMPETITION, "soccer_epl", EPL),
            *(_test_mapping(NAMESPACE_TEAM, k, v) for k, v in ODDS_TEAM_LABELS.items()),
            _test_mapping(NAMESPACE_BOOKMAKER, "bookie_a", "BOOKIE_A"),
            _test_mapping(NAMESPACE_BOOKMAKER, "bookie_b", "BOOKIE_B"),
            *extra,
        )
    )


def context(mappings: MappingTable | None = None) -> IngestionContext:
    return IngestionContext(
        mappings=mappings if mappings is not None else odds_test_mappings(),
        capture_mode=CaptureMode.RETROSPECTIVE_ARCHIVE,
        openfootball_timezone="Europe/London",
    )


def build(
    *captures: tuple[RawCapture, bytes], mappings: MappingTable | None = None
) -> FootballBuild:
    return build_football(captures, context(mappings))


def z(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


MUFC_FULHAM_KICKOFF = datetime(2024, 8, 16, 19, 0, tzinfo=UTC)
SNAPSHOT_AT = MUFC_FULHAM_KICKOFF - timedelta(hours=1, minutes=3)
REQUESTED_AT = MUFC_FULHAM_KICKOFF - timedelta(hours=1)


def h2h(home: Any = 1.5, draw: Any = 4.2, away: Any = 6.5, **market: Any) -> dict[str, Any]:
    return {
        "key": "h2h",
        "last_update": z(SNAPSHOT_AT - timedelta(minutes=2)),
        "outcomes": [
            {"name": "Manchester United", "price": home},
            {"name": "Draw", "price": draw},
            {"name": "Fulham", "price": away},
        ],
        **market,
    }


def totals(point: float = 2.5, over: Any = 1.9, under: Any = 1.95) -> dict[str, Any]:
    return {
        "key": "totals",
        "last_update": z(SNAPSHOT_AT - timedelta(minutes=4)),
        "outcomes": [
            {"name": "Over", "price": over, "point": point},
            {"name": "Under", "price": under, "point": point},
        ],
    }


def odds_event(
    *bookmakers: dict[str, Any], commence: datetime = MUFC_FULHAM_KICKOFF
) -> dict[str, Any]:
    return {
        "id": "synthetic-event-0001",
        "sport_key": "soccer_epl",
        "sport_title": "EPL",
        "commence_time": z(commence),
        "home_team": "Manchester United",
        "away_team": "Fulham",
        "bookmakers": list(bookmakers),
    }


def bookmaker(key: str = "bookie_a", *markets: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": key,
        "title": key.upper(),
        "last_update": z(SNAPSHOT_AT - timedelta(minutes=1)),
        "markets": list(markets) if markets else [h2h(), totals()],
    }


def odds_payload(*events: dict[str, Any], snapshot_at: datetime = SNAPSHOT_AT) -> bytes:
    document = {
        "timestamp": z(snapshot_at),
        "previous_timestamp": z(snapshot_at - timedelta(minutes=5)),
        "next_timestamp": z(snapshot_at + timedelta(minutes=5)),
        "data": list(events) if events else [odds_event(bookmaker())],
    }
    return json.dumps(document, sort_keys=True).encode("utf-8")


def odds_capture(
    payload: bytes | None = None,
    *,
    received_at: datetime = T2,
    requested_at: datetime = REQUESTED_AT,
    http_status: int = 200,
    api_key: str = "synthetic-secret-api-key",
) -> tuple[RawCapture, bytes]:
    payload = payload if payload is not None else odds_payload()
    raw = capture(
        payload,
        source_id=THE_ODDS_API,
        resource="https://api.the-odds-api.com/v4/historical/sports/soccer_epl/odds",
        request_parameters={
            "apiKey": api_key,
            "date": z(requested_at),
            "markets": "h2h,totals",
            "oddsFormat": "decimal",
            "regions": "eu",
        },
        received_at=received_at,
        provider_timestamps={},
        source_revision=None,
        media_type="application/json",
        http_status=http_status,
        ingestion_version=INGESTION_VERSION,
    )
    return raw, payload
