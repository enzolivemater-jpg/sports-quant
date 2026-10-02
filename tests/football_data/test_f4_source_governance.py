"""F4 source registry: taxonomy mapping and OD-24 governance (no provider approved)."""

from __future__ import annotations

import pytest

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.source import SourceTier
from sports_quant.data.provenance.sources import (
    API_FOOTBALL,
    OPENFOOTBALL,
    SOURCE_REGISTRY,
    SPORTMONKS,
    SPORTRADAR,
    STATSBOMB_OPEN_DATA,
    THE_ODDS_API,
    AdapterState,
    LiveIngestionState,
    ProviderApproval,
    SourceRole,
    source_descriptor,
)


def test_no_source_is_approved_while_od24_is_open() -> None:
    assert {d.approval for d in SOURCE_REGISTRY} == {ProviderApproval.NOT_APPROVED}
    assert [member.value for member in ProviderApproval] == ["NOT_APPROVED"]


def test_source_taxonomy_maps_to_canonical_f2_tiers() -> None:
    assert source_descriptor(OPENFOOTBALL).source_ref("git-blob:x").tier is SourceTier.AGGREGATOR
    assert source_descriptor(THE_ODDS_API).source_ref(None).tier is SourceTier.AGGREGATOR


@pytest.mark.parametrize("source_id", [STATSBOMB_OPEN_DATA, API_FOOTBALL, SPORTMONKS, SPORTRADAR])
def test_sources_without_adapter_cannot_produce_records(source_id: str) -> None:
    descriptor = source_descriptor(source_id)
    assert descriptor.tier is None
    assert descriptor.adapter is AdapterState.NOT_IMPLEMENTED
    with pytest.raises(ContractError, match="SOURCE_NOT_INGESTIBLE"):
        descriptor.source_ref(None)


def test_recorded_roles_match_the_evidence_matrix() -> None:
    roles = {d.source_id: d.roles for d in SOURCE_REGISTRY}
    assert roles[STATSBOMB_OPEN_DATA] == (SourceRole.VERIFIED_RESEARCH_SANDBOX,)
    assert roles[THE_ODDS_API] == (SourceRole.CANDIDATE_HISTORICAL_ODDS,)
    assert roles[API_FOOTBALL] == (SourceRole.CANDIDATE_PROSPECTIVE_CONTEXT,)
    assert roles[SPORTMONKS] == (SourceRole.CANDIDATE_BROAD_FOOTBALL_PROVIDER,)
    assert roles[SPORTRADAR] == (SourceRole.CANDIDATE_LICENSED_COMPREHENSIVE_DATA,)
    assert roles[OPENFOOTBALL] == (SourceRole.RESULTS_BASELINE_RESEARCH,)


def test_historical_odds_live_leg_is_explicitly_blocked() -> None:
    descriptor = source_descriptor(THE_ODDS_API)
    assert descriptor.live_ingestion is LiveIngestionState.EXPLICITLY_BLOCKED_WITH_EVIDENCE
    assert descriptor.adapter is AdapterState.EXPERIMENTAL


def test_unknown_source_is_rejected() -> None:
    with pytest.raises(ContractError, match="UNKNOWN_SOURCE"):
        source_descriptor("football_data_co_uk")


def test_tier_and_adapter_must_agree() -> None:
    descriptor = source_descriptor(STATSBOMB_OPEN_DATA)
    data = descriptor.to_dict()
    data["tier"] = "AGGREGATOR"
    with pytest.raises(ContractError, match="SOURCE_TIER_ADAPTER_MISMATCH"):
        type(descriptor).from_dict(data)
