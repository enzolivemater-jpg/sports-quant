"""F4 deterministic entity resolution: exact lookups, aliases, collisions, curated EPL table."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sports_quant.contracts.common import ContractError
from sports_quant.data.entity_resolution.football_epl import (
    EPL_2024_25_MAPPINGS,
    NAMESPACE_TEAM,
    OPENFOOTBALL_EPL_2024_25_BLOB_SHA,
    OPENFOOTBALL_EPL_2024_25_TEAMS,
    epl_2024_25_table,
    league_event_id,
    season_id,
    team_id,
)
from sports_quant.data.entity_resolution.mapping import (
    EntityMapping,
    MappingMethod,
    MappingTable,
    ResolutionStatus,
    ReviewState,
)

ROOT = Path(__file__).resolve().parents[2]


def mapping(external_id: str, value: str, provider: str = "p") -> EntityMapping:
    return EntityMapping(
        provider_id=provider,
        namespace="TEAM",
        external_id=external_id,
        canonical_value=value,
        method=MappingMethod.CURATED_ALIAS,
        review_state=ReviewState.CURATED_PENDING_REVIEW,
        evidence="test",
    )


def test_exact_mapping_resolves() -> None:
    resolution = MappingTable([mapping("Arsenal FC", "ARSENAL")]).resolve("p", "TEAM", "Arsenal FC")
    assert (resolution.status, resolution.canonical_value) == (ResolutionStatus.RESOLVED, "ARSENAL")


@pytest.mark.parametrize("label", ["arsenal fc", "Arsenal FC ", "Arsenal", "Arsenal F.C."])
def test_no_normalization_or_fuzzy_matching(label: str) -> None:
    resolution = MappingTable([mapping("Arsenal FC", "ARSENAL")]).resolve("p", "TEAM", label)
    assert resolution.status is ResolutionStatus.UNMAPPED
    assert resolution.canonical_value is None and resolution.candidates == ()


def test_mappings_are_scoped_by_provider_and_namespace() -> None:
    table = MappingTable([mapping("Arsenal FC", "ARSENAL", provider="a")])
    assert table.resolve("b", "TEAM", "Arsenal FC").status is ResolutionStatus.UNMAPPED
    assert table.resolve("a", "COMPETITION", "Arsenal FC").status is ResolutionStatus.UNMAPPED


def test_aliases_of_one_team_resolve_to_one_identity() -> None:
    """Renamed/relabelled clubs keep their identity through explicit aliases."""

    table = MappingTable(
        [
            mapping("Wolverhampton Wanderers FC", "WOLVERHAMPTON_WANDERERS"),
            mapping("Wolves FC", "WOLVERHAMPTON_WANDERERS"),
        ]
    )
    values = {
        table.resolve("p", "TEAM", label).canonical_value
        for label in ("Wolverhampton Wanderers FC", "Wolves FC")
    }
    assert values == {"WOLVERHAMPTON_WANDERERS"}
    assert table.aliases("TEAM", "WOLVERHAMPTON_WANDERERS") == (
        ("p", "Wolverhampton Wanderers FC"),
        ("p", "Wolves FC"),
    )


def test_colliding_label_is_ambiguous_never_picked() -> None:
    table = MappingTable(
        [mapping("Manchester", "MANCHESTER_UNITED"), mapping("Manchester", "MANCHESTER_CITY")]
    )
    resolution = table.resolve("p", "TEAM", "Manchester")
    assert resolution.status is ResolutionStatus.AMBIGUOUS
    assert resolution.canonical_value is None
    assert resolution.candidates == ("MANCHESTER_CITY", "MANCHESTER_UNITED")
    assert table.collisions() == (("p", "TEAM", "Manchester"),)


def test_resolution_is_order_independent() -> None:
    entries = [mapping("A", "X"), mapping("B", "Y"), mapping("A", "Z")]
    forward, backward = MappingTable(entries), MappingTable(reversed(entries))
    assert forward.entries == backward.entries
    assert forward.resolve("p", "TEAM", "A") == backward.resolve("p", "TEAM", "A")


def test_duplicate_mapping_entries_are_rejected() -> None:
    with pytest.raises(ContractError, match="DUPLICATE_VALUE"):
        MappingTable([mapping("A", "X"), mapping("A", "X")])


def test_curated_epl_table_is_collision_free_and_pending_review() -> None:
    table = epl_2024_25_table()
    assert table.collisions() == ()
    assert {m.review_state for m in EPL_2024_25_MAPPINGS} == {ReviewState.CURATED_PENDING_REVIEW}
    values = list(OPENFOOTBALL_EPL_2024_25_TEAMS.values())
    assert len(values) == len(set(values)) == 20


def test_curated_labels_match_the_research_alias_manifest() -> None:
    manifest = json.loads(
        (ROOT / "data" / "manifests" / "football_openfootball_stage_a_aliases.json").read_text()
    )
    assert manifest["source_blob_sha"] == OPENFOOTBALL_EPL_2024_25_BLOB_SHA
    assert set(manifest["aliases"]) == set(OPENFOOTBALL_EPL_2024_25_TEAMS)
    for label in manifest["aliases"]:
        assert epl_2024_25_table().resolve("openfootball", NAMESPACE_TEAM, label).status is (
            ResolutionStatus.RESOLVED
        )


def test_curated_blob_is_the_pinned_season_blob() -> None:
    pinned = json.loads(
        (
            ROOT / "data" / "manifests" / "football_openfootball_epl_2000_2025_verified.json"
        ).read_text()
    )
    (entry,) = [s for s in pinned["seasons"] if s["season"] == "2024-25"]
    assert entry["blob_sha"] == OPENFOOTBALL_EPL_2024_25_BLOB_SHA


def test_league_event_identity_is_deterministic_and_directional() -> None:
    season = season_id("ENGLAND_PREMIER_LEAGUE:2024-25")
    home, away = team_id("ARSENAL"), team_id("FULHAM")
    assert league_event_id(season, home, away) == league_event_id(season, home, away)
    assert league_event_id(season, home, away) != league_event_id(season, away, home)
