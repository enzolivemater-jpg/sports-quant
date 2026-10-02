"""Curated canonical identities for the F4 Football pilot: EPL 2024/25.

Canonical values are SPORTS QUANT identifiers, never provider identifiers. The only
provider labels mapped here are the exact OpenFootball labels of the pinned
``openfootball/england`` 2024-25 file; they match the label set recorded in
``data/manifests/football_openfootball_stage_a_aliases.json``. Every other provider
must bring its own alias evidence: nothing is inherited by name similarity.

All mappings are ``CURATED_PENDING_REVIEW`` until independent review.
"""

from __future__ import annotations

from sports_quant.contracts.entity import CanonicalEntityId, EntityKind, Sport
from sports_quant.data.entity_resolution.mapping import (
    EntityMapping,
    MappingMethod,
    MappingTable,
    ReviewState,
)
from sports_quant.data.provenance.sources import OPENFOOTBALL

NAMESPACE_COMPETITION = "COMPETITION"
NAMESPACE_SEASON = "SEASON"
NAMESPACE_TEAM = "TEAM"
NAMESPACE_BOOKMAKER = "BOOKMAKER"

EPL = "ENGLAND_PREMIER_LEAGUE"
EPL_2024_25 = f"{EPL}:2024-25"

OPENFOOTBALL_EPL_2024_25_BLOB_SHA = "ca0fe4923f0164d0f879f796ab0759253e13bc06"
_EVIDENCE = (
    f"openfootball/england 2024-25/1-premierleague.txt blob {OPENFOOTBALL_EPL_2024_25_BLOB_SHA}; "
    "labels cross-checked against data/manifests/football_openfootball_stage_a_aliases.json"
)

# OpenFootball 2024/25 label -> canonical team value.
OPENFOOTBALL_EPL_2024_25_TEAMS: dict[str, str] = {
    "AFC Bournemouth": "AFC_BOURNEMOUTH",
    "Arsenal FC": "ARSENAL",
    "Aston Villa FC": "ASTON_VILLA",
    "Brentford FC": "BRENTFORD",
    "Brighton & Hove Albion FC": "BRIGHTON_AND_HOVE_ALBION",
    "Chelsea FC": "CHELSEA",
    "Crystal Palace FC": "CRYSTAL_PALACE",
    "Everton FC": "EVERTON",
    "Fulham FC": "FULHAM",
    "Ipswich Town FC": "IPSWICH_TOWN",
    "Leicester City FC": "LEICESTER_CITY",
    "Liverpool FC": "LIVERPOOL",
    "Manchester City FC": "MANCHESTER_CITY",
    "Manchester United FC": "MANCHESTER_UNITED",
    "Newcastle United FC": "NEWCASTLE_UNITED",
    "Nottingham Forest FC": "NOTTINGHAM_FOREST",
    "Southampton FC": "SOUTHAMPTON",
    "Tottenham Hotspur FC": "TOTTENHAM_HOTSPUR",
    "West Ham United FC": "WEST_HAM_UNITED",
    "Wolverhampton Wanderers FC": "WOLVERHAMPTON_WANDERERS",
}


def _curated(namespace: str, external_id: str, canonical_value: str) -> EntityMapping:
    return EntityMapping(
        provider_id=OPENFOOTBALL,
        namespace=namespace,
        external_id=external_id,
        canonical_value=canonical_value,
        method=MappingMethod.CURATED_ALIAS,
        review_state=ReviewState.CURATED_PENDING_REVIEW,
        evidence=_EVIDENCE,
    )


EPL_2024_25_MAPPINGS: tuple[EntityMapping, ...] = (
    _curated(NAMESPACE_COMPETITION, "English Premier League", EPL),
    _curated(NAMESPACE_SEASON, "English Premier League 2024/25", EPL_2024_25),
    *(
        _curated(NAMESPACE_TEAM, label, value)
        for label, value in OPENFOOTBALL_EPL_2024_25_TEAMS.items()
    ),
)


def epl_2024_25_table() -> MappingTable:
    return MappingTable(EPL_2024_25_MAPPINGS)


def team_id(value: str) -> CanonicalEntityId:
    return CanonicalEntityId(sport=Sport.FOOTBALL, kind=EntityKind.TEAM, value=value)


def competition_id(value: str) -> CanonicalEntityId:
    return CanonicalEntityId(sport=Sport.FOOTBALL, kind=EntityKind.COMPETITION, value=value)


def season_id(value: str) -> CanonicalEntityId:
    return CanonicalEntityId(sport=Sport.FOOTBALL, kind=EntityKind.SEASON, value=value)


def league_event_id(
    season: CanonicalEntityId, home: CanonicalEntityId, away: CanonicalEntityId
) -> CanonicalEntityId:
    """Canonical league-fixture identity: one home/away pairing per league season.

    Independent of kickoff time, so a rescheduled fixture keeps its identity.
    """

    return CanonicalEntityId(
        sport=Sport.FOOTBALL,
        kind=EntityKind.EVENT,
        value=f"{season.value}:{home.value}:{away.value}",
    )
