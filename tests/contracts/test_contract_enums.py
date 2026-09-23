"""Canonical enums: exact values, round-trips, strict parsing, legacy normalization.

Expected values are read from the canonical Foundation YAML so code and governance
cannot drift apart silently.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

from sports_quant.contracts.common import CanonicalEnum, ContractError
from sports_quant.contracts.data_state import (
    ConflictState,
    FreshnessState,
    QualityState,
    VerificationState,
)
from sports_quant.contracts.decision import DecisionState
from sports_quant.contracts.dependency import DependencyClass
from sports_quant.contracts.market_risk import MarketRiskClass, MarketRiskMode
from sports_quant.contracts.predictability import EvidenceStatus, SportPredictabilityClass
from sports_quant.contracts.source import (
    LEGACY_SOURCE_TIER_NORMALIZATION,
    SourceTier,
    normalize_source_tier,
)
from sports_quant.contracts.sports_intelligence import ClaimType, EffectChannel
from sports_quant.contracts.time import KnownAtBasis

ROOT = Path(__file__).resolve().parents[2]
FOUNDATION = (ROOT / ".project" / "FOUNDATION_DECISIONS_v0.1.yaml").read_text(encoding="utf-8")


def _governance_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "validate_governance", ROOT / "scripts" / "validate_governance.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _yaml_list(key: str) -> list[str]:
    values: list[str] = _governance_validator()._yaml_list_after_key(FOUNDATION, key)
    return values


# (enum, key of its canonical list in FOUNDATION_DECISIONS_v0.1.yaml; first match)
CANONICAL_LISTS: list[tuple[type[CanonicalEnum], str]] = [
    (SourceTier, "canonical_values"),
    (QualityState, "quality_state"),
    (FreshnessState, "freshness_state"),
    (VerificationState, "verification_state"),
    (ConflictState, "conflict_state"),
    (KnownAtBasis, "known_at_basis"),
    (ClaimType, "claim_types"),
    (EffectChannel, "allowed_effect_channels"),
    (MarketRiskClass, "classes"),
    (MarketRiskMode, "modes"),
    (EvidenceStatus, "evidence_status_values"),
]

ALL_ENUMS: list[type[CanonicalEnum]] = [
    *(enum for enum, _key in CANONICAL_LISTS),
    DecisionState,
    DependencyClass,
    SportPredictabilityClass,
]


@pytest.mark.parametrize(("enum", "key"), CANONICAL_LISTS, ids=lambda item: str(item))
def test_enum_values_match_canonical_yaml(enum: type[CanonicalEnum], key: str) -> None:
    assert [member.value for member in enum] == _yaml_list(key)


def test_decision_states_match_canonical_values() -> None:
    assert [state.value for state in DecisionState] == [
        "QUALIFIED",
        "WAIT",
        "REVIEW",
        "NO_BET",
        "BLOCKED",
    ]


def test_dependency_classes_are_exact_lowercase_canonical_values() -> None:
    assert [member.value for member in DependencyClass] == [
        "independent",
        "weak",
        "moderate",
        "strong",
        "redundant",
        "contradictory",
    ]


def test_sp_classes_are_exactly_sp1_to_sp5() -> None:
    assert [member.value for member in SportPredictabilityClass] == [
        "SP1",
        "SP2",
        "SP3",
        "SP4",
        "SP5",
    ]


@pytest.mark.parametrize("enum", ALL_ENUMS, ids=lambda enum: enum.__name__)
def test_enum_exact_round_trip(enum: type[CanonicalEnum]) -> None:
    for member in enum:
        assert enum.parse(member.value) is member
        assert enum.parse(str(member)) is member
        assert str(member) == member.value


@pytest.mark.parametrize("enum", ALL_ENUMS, ids=lambda enum: enum.__name__)
def test_unknown_enum_values_are_rejected(enum: type[CanonicalEnum]) -> None:
    first = next(iter(enum)).value
    for bad in ("UNKNOWN", "", first.lower() if first.isupper() else first.upper(), f" {first}"):
        with pytest.raises(ContractError) as excinfo:
            enum.parse(bad)
        assert excinfo.value.code == "UNKNOWN_ENUM_VALUE"
    for non_string in (None, 1, 1.0, True):
        with pytest.raises(ContractError):
            enum.parse(non_string)


def test_members_of_another_enum_are_rejected_even_if_values_coincide() -> None:
    # "CONFLICT" claim type is not a ConflictState; ConflictState.NONE is not a claim type.
    with pytest.raises(ContractError):
        ClaimType.parse(ConflictState.NONE)
    with pytest.raises(ContractError):
        QualityState.parse(FreshnessState.LIVE)


@pytest.mark.parametrize(
    ("legacy", "canonical"),
    [
        ("LICENSED DATA", SourceTier.LICENSED_PRO),
        ("LICENSED PROFESSIONAL", SourceTier.LICENSED_PRO),
        ("SOCIAL", SourceTier.SOCIAL_UNVERIFIED),
        ("SOCIAL/UNVERIFIED", SourceTier.SOCIAL_UNVERIFIED),
    ],
)
def test_legacy_source_tiers_normalize(legacy: str, canonical: SourceTier) -> None:
    assert normalize_source_tier(legacy) is canonical


def test_legacy_normalization_table_is_exactly_the_approved_one() -> None:
    assert dict(LEGACY_SOURCE_TIER_NORMALIZATION) == {
        "LICENSED DATA": SourceTier.LICENSED_PRO,
        "LICENSED PROFESSIONAL": SourceTier.LICENSED_PRO,
        "SOCIAL": SourceTier.SOCIAL_UNVERIFIED,
        "SOCIAL/UNVERIFIED": SourceTier.SOCIAL_UNVERIFIED,
    }
    with pytest.raises(TypeError):
        LEGACY_SOURCE_TIER_NORMALIZATION["LICENSED"] = SourceTier.LICENSED_PRO  # type: ignore[index]


def test_canonical_source_tiers_normalize_to_themselves() -> None:
    for tier in SourceTier:
        assert normalize_source_tier(tier.value) is tier


@pytest.mark.parametrize(
    "value", ["LICENSED", "licensed data", "Social", "SOCIAL / UNVERIFIED", "TRUSTED", ""]
)
def test_unapproved_source_labels_are_rejected(value: str) -> None:
    with pytest.raises(ContractError) as excinfo:
        normalize_source_tier(value)
    assert excinfo.value.code == "UNKNOWN_SOURCE_TIER"


def test_legacy_labels_are_not_accepted_as_canonical_storage_values() -> None:
    for legacy in LEGACY_SOURCE_TIER_NORMALIZATION:
        with pytest.raises(ContractError):
            SourceTier.parse(legacy)
