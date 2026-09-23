"""Sports Intelligence, Market Risk, market catalog and dependency contracts."""

from __future__ import annotations

import dataclasses

import pytest
from contract_builders import data_state, entity, market, provenance

from sports_quant.contracts import market_risk
from sports_quant.contracts.common import ContractError
from sports_quant.contracts.data_state import ConflictState, VerificationState
from sports_quant.contracts.dependency import DependencyAssertion, DependencyClass
from sports_quant.contracts.entity import Sport
from sports_quant.contracts.market import (
    FOOTBALL_MARKET_CATALOG,
    CatalogPhase,
    MarketDescriptor,
    MarketFamily,
)
from sports_quant.contracts.market_risk import MarketRiskClass, MarketRiskMode
from sports_quant.contracts.sports_intelligence import (
    ClaimType,
    EffectChannel,
    SportsIntelligenceClaim,
)


def _claim(**overrides: object) -> SportsIntelligenceClaim:
    base = SportsIntelligenceClaim(
        claim_id="claim-1",
        claim_type=ClaimType.FACT,
        subjects=(entity(),),
        statement="Starting goalkeeper ruled out",
        provenance=provenance(data_state=data_state(verification=VerificationState.UNVERIFIED)),
        effect_channels=(EffectChannel.UNCERTAINTY, EffectChannel.REVIEW_STATE),
    )
    return dataclasses.replace(base, **overrides)


def test_fact_does_not_imply_verified() -> None:
    claim = _claim()
    assert claim.claim_type is ClaimType.FACT
    assert claim.provenance.data_state.verification is VerificationState.UNVERIFIED
    restored = SportsIntelligenceClaim.from_json(claim.to_json())
    assert restored.provenance.data_state.verification is VerificationState.UNVERIFIED


def test_conflict_claim_type_is_independent_of_conflict_state() -> None:
    claim = _claim(claim_type=ClaimType.CONFLICT)
    assert claim.provenance.data_state.conflict is ConflictState.NONE


def test_only_approved_effect_channels_are_accepted() -> None:
    for channel in EffectChannel:
        assert _claim(effect_channels=(channel,)).effect_channels == (channel,)
    for forbidden in ("P_SAFE", "PROBABILITY", "EDGE", "STAKE"):
        with pytest.raises(ContractError):
            EffectChannel.parse(forbidden)
        with pytest.raises(ContractError):
            _claim(effect_channels=(forbidden,))


def test_unknown_effect_channel_is_rejected_on_deserialization() -> None:
    payload = _claim().to_dict()
    payload["effect_channels"] = ["P_SAFE"]
    with pytest.raises(ContractError):
        SportsIntelligenceClaim.from_dict(payload)


def test_claim_cannot_carry_a_probability() -> None:
    names = {field.name for field in dataclasses.fields(SportsIntelligenceClaim)}
    assert not {name for name in names if name.startswith("p_") or "prob" in name}
    payload = _claim().to_dict()
    payload["p_safe"] = 0.9
    with pytest.raises(ContractError) as excinfo:
        SportsIntelligenceClaim.from_dict(payload)
    assert excinfo.value.code == "UNKNOWN_FIELD"


def test_duplicate_effect_channels_are_rejected() -> None:
    with pytest.raises(ContractError):
        _claim(effect_channels=(EffectChannel.GATES, EffectChannel.GATES))


def test_market_risk_classes_are_ordinal_not_probabilities() -> None:
    assert [member.ordinal for member in MarketRiskClass] == [1, 2, 3, 4, 5, 6]
    for member in MarketRiskClass:
        with pytest.raises(ValueError):
            float(member)


def test_deferred_market_risk_aggregates_are_absent() -> None:
    for name in ("weighted_average_mr", "dynamic_market_risk", "composite_market_risk"):
        assert not hasattr(market_risk, name)


def test_market_risk_mode_round_trip() -> None:
    for mode in MarketRiskMode:
        assert MarketRiskMode.parse(mode.value) is mode


def test_football_catalog_is_exactly_the_frozen_one() -> None:
    assert [
        (entry.sport, entry.market_family, entry.phase, entry.mr_base)
        for entry in FOOTBALL_MARKET_CATALOG
    ] == [
        (Sport.FOOTBALL, MarketFamily.FOOTBALL_1X2, CatalogPhase.PHASE_1, MarketRiskClass.MR2),
        (
            Sport.FOOTBALL,
            MarketFamily.FOOTBALL_TOTAL_GOALS_MAIN,
            CatalogPhase.PHASE_1,
            MarketRiskClass.MR2,
        ),
        (
            Sport.FOOTBALL,
            MarketFamily.FOOTBALL_ASIAN_HANDICAP,
            CatalogPhase.PHASE_2,
            MarketRiskClass.MR2,
        ),
        (Sport.FOOTBALL, MarketFamily.FOOTBALL_BTTS, CatalogPhase.PHASE_2, MarketRiskClass.MR2),
        (
            Sport.FOOTBALL,
            MarketFamily.FOOTBALL_TEAM_TOTALS,
            CatalogPhase.PHASE_2,
            MarketRiskClass.MR2,
        ),
    ]


def test_no_market_family_exists_outside_football() -> None:
    assert all(family.value.startswith("FOOTBALL_") for family in MarketFamily)
    for invented in ("BASKETBALL_MONEYLINE", "MMA_METHOD_OF_VICTORY", "TENNIS_MATCH_WINNER"):
        with pytest.raises(ContractError):
            MarketFamily.parse(invented)


def test_market_descriptor_enforces_catalog_mr_base_and_sport() -> None:
    base = market()
    with pytest.raises(ContractError) as excinfo:
        dataclasses.replace(base, mr_base=MarketRiskClass.MR1)
    assert excinfo.value.code == "MR_BASE_MISMATCH"
    with pytest.raises(ContractError) as excinfo:
        dataclasses.replace(base, sport=Sport.BASKETBALL)
    assert excinfo.value.code == "MARKET_SPORT_MISMATCH"
    assert MarketDescriptor.from_json(base.to_json()) == base


@pytest.mark.parametrize("dependency_class", list(DependencyClass))
def test_dependency_class_round_trip(dependency_class: DependencyClass) -> None:
    assertion = DependencyAssertion(
        selection_a="match-1:HOME",
        selection_b="match-1:OVER_2_5",
        dependency_class=dependency_class,
        basis="same match",
    )
    payload = assertion.to_dict()
    assert payload["dependency_class"] == dependency_class.value
    assert DependencyAssertion.from_dict(payload) == assertion


def test_dependency_rejects_self_dependency_and_unknown_class() -> None:
    with pytest.raises(ContractError):
        DependencyAssertion(
            selection_a="x", selection_b="x", dependency_class=DependencyClass.WEAK, basis="b"
        )
    with pytest.raises(ContractError):
        DependencyClass.parse("INDEPENDENT")


def test_dependency_contract_is_qualitative_only() -> None:
    names = {field.name for field in dataclasses.fields(DependencyAssertion)}
    assert names == {"selection_a", "selection_b", "dependency_class", "basis"}
