"""PredictabilityAssessment: required fields, versioning, immutability, no numeric SP."""

from __future__ import annotations

import dataclasses
from datetime import UTC, datetime, timedelta

import pytest
from contract_builders import artifact, assessment, entity

from sports_quant.contracts.common import ContractError
from sports_quant.contracts.entity import CanonicalEntityId, EntityKind, Sport
from sports_quant.contracts.market import (
    FOOTBALL_MARKET_CATALOG,
    MarketDescriptor,
    MarketFamily,
)
from sports_quant.contracts.market_risk import MarketRiskClass
from sports_quant.contracts.predictability import (
    EvidenceStatus,
    PredictabilityAssessment,
    SportPredictabilityClass,
    require_successor,
)
from sports_quant.contracts.reproducibility import ArtifactKind

REQUIRED_FIELDS = [
    "assessment_version",
    "sport",
    "market_family",
    "competition",
    "predictability_prior",
    "predictability_empirical",
    "evidence_status",
    "oos_brier",
    "oos_log_loss",
    "oos_ece",
    "oos_skill",
    "sample_sizes",
    "evaluation_period",
    "stability",
    "data_quality",
    "drift",
    "baseline_scope",
    "model_scope",
    "dataset_version_or_snapshot",
    "code_version",
    "known_at",
]


def test_assessment_has_exactly_the_required_fields() -> None:
    # `competition` is the spec's `competition_optional`: required key, nullable value.
    assert [field.name for field in dataclasses.fields(PredictabilityAssessment)] == (
        REQUIRED_FIELDS
    )


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_every_field_is_required_on_deserialization(field: str) -> None:
    payload = assessment().to_dict()
    del payload[field]
    with pytest.raises(ContractError) as excinfo:
        PredictabilityAssessment.from_dict(payload)
    assert excinfo.value.code == "MISSING_FIELD"


def test_every_field_is_required_on_construction() -> None:
    kwargs = {field: getattr(assessment(), field) for field in REQUIRED_FIELDS[:-1]}
    with pytest.raises(TypeError):
        PredictabilityAssessment(**kwargs)


def test_prior_and_empirical_are_separate() -> None:
    value = assessment(
        predictability_prior=SportPredictabilityClass.SP2,
        predictability_empirical=SportPredictabilityClass.SP4,
        evidence_status=EvidenceStatus.PROVISIONAL,
    )
    assert value.predictability_prior is not value.predictability_empirical


def test_validated_evidence_requires_empirical_class() -> None:
    with pytest.raises(ContractError) as excinfo:
        assessment(evidence_status=EvidenceStatus.VALIDATED, predictability_empirical=None)
    assert excinfo.value.code == "EMPIRICAL_CLASS_REQUIRED"


def test_known_at_must_be_aware_and_not_before_evaluation_end() -> None:
    with pytest.raises(ContractError):
        assessment(known_at=datetime(2026, 6, 1))
    with pytest.raises(ContractError) as excinfo:
        assessment(known_at=datetime(2026, 5, 30, tzinfo=UTC))
    assert excinfo.value.code == "KNOWN_AT_BEFORE_EVALUATION_END"


@pytest.mark.parametrize(
    ("field", "value"),
    [("oos_brier", -0.1), ("oos_log_loss", -0.1), ("oos_ece", 1.5), ("oos_ece", -0.1)],
)
def test_metrics_outside_mathematical_range_are_rejected(field: str, value: float) -> None:
    with pytest.raises(ContractError):
        assessment(**{field: value})


def test_metrics_have_no_admission_thresholds() -> None:
    # Any mathematically valid metric is accepted; admission thresholds are not defined.
    value = assessment(
        evidence_status=EvidenceStatus.PROVISIONAL,
        predictability_empirical=SportPredictabilityClass.SP5,
        oos_brier=1.9,
        oos_log_loss=5.0,
        oos_ece=1.0,
        oos_skill=-3.0,
    )
    assert value.oos_skill == -3.0


def test_sp_class_is_not_numeric() -> None:
    for member in SportPredictabilityClass:
        with pytest.raises(ValueError):
            int(member)
    names = {field.name for field in dataclasses.fields(PredictabilityAssessment)}
    assert not {name for name in names if "score" in name or name.startswith("p_")}
    assert "edge" not in names and "market_risk" not in names


def test_competition_must_be_a_competition_of_the_same_sport() -> None:
    league = entity(EntityKind.COMPETITION, "premier-league")
    assert assessment(competition=league).competition == league
    with pytest.raises(ContractError):
        assessment(competition=entity(EntityKind.TEAM))
    with pytest.raises(ContractError):
        assessment(
            competition=CanonicalEntityId(
                sport=Sport.TENNIS, kind=EntityKind.COMPETITION, value="atp"
            )
        )


# Opaque, non-production scope identifiers used only by these tests. They are not
# proposals for Handball/Volleyball/Tennis market families (none are defined).
VALIDATION_ONLY_SCOPES = [
    (Sport.HANDBALL, "VALIDATION_SCOPE_A"),
    (Sport.VOLLEYBALL, "VALIDATION_SCOPE_B"),
    (Sport.TENNIS, "VALIDATION_SCOPE_C"),
]


@pytest.mark.parametrize(("sport", "scope"), VALIDATION_ONLY_SCOPES)
def test_validation_only_sports_are_assessable(sport: Sport, scope: str) -> None:
    # Regression for review P1-01: SP scope was hard-coupled to the Football catalog.
    value = assessment(sport=sport, market_family=scope)
    assert value.scope_key == (sport, scope, None)
    assert PredictabilityAssessment.from_json(value.to_json()) == value


@pytest.mark.parametrize(("sport", "scope"), VALIDATION_ONLY_SCOPES)
def test_assessing_a_scope_does_not_promote_it_to_the_production_catalog(
    sport: Sport, scope: str
) -> None:
    assessment(sport=sport, market_family=scope)
    with pytest.raises(ContractError):
        MarketFamily.parse(scope)
    assert {entry.sport for entry in FOOTBALL_MARKET_CATALOG} == {Sport.FOOTBALL}
    assert len(FOOTBALL_MARKET_CATALOG) == 5
    with pytest.raises(ContractError):
        MarketDescriptor(
            sport=sport,
            market_family=MarketFamily.FOOTBALL_1X2,
            market_type="T",
            market_instance="I",
            mr_base=MarketRiskClass.MR2,
        )


@pytest.mark.parametrize("family", list(MarketFamily))
def test_football_production_families_remain_assessable(family: MarketFamily) -> None:
    value = assessment(sport=Sport.FOOTBALL, market_family=family.value)
    assert PredictabilityAssessment.from_json(value.to_json()).market_family == family.value


@pytest.mark.parametrize("bad", ["", "lower_case", "WITH SPACE", "1X2", "DASH-ED"])
def test_market_family_scope_must_be_a_deterministic_identifier(bad: str) -> None:
    with pytest.raises(ContractError) as excinfo:
        assessment(market_family=bad)
    assert excinfo.value.code == "INVALID_IDENTIFIER"


def test_market_family_scope_must_be_a_string() -> None:
    with pytest.raises(ContractError):
        assessment(market_family=MarketFamily.FOOTBALL_1X2)


def test_dataset_reference_must_be_dataset_or_snapshot() -> None:
    assessment(dataset_version_or_snapshot=artifact(ArtifactKind.DATASET))
    with pytest.raises(ContractError):
        assessment(dataset_version_or_snapshot=artifact(ArtifactKind.MODEL))


@pytest.mark.parametrize("version", [0, -1])
def test_assessment_version_must_be_positive(version: int) -> None:
    with pytest.raises(ContractError):
        assessment(assessment_version=version)


def test_assessment_version_must_be_an_int() -> None:
    for value in (True, 1.0, "1"):
        with pytest.raises(ContractError):
            assessment(assessment_version=value)


def test_assessment_is_immutable() -> None:
    value = assessment()
    with pytest.raises(dataclasses.FrozenInstanceError):
        value.evidence_status = EvidenceStatus.VALIDATED  # type: ignore[misc]


def test_revision_is_a_new_version_and_leaves_the_original_untouched() -> None:
    original = assessment()
    original_json = original.to_json()
    revised = dataclasses.replace(
        original,
        assessment_version=2,
        evidence_status=EvidenceStatus.PROVISIONAL,
        predictability_empirical=SportPredictabilityClass.SP3,
        known_at=original.known_at + timedelta(days=30),
    )
    require_successor(original, revised)
    assert original.to_json() == original_json
    assert revised.scope_key == original.scope_key
    assert revised.content_digest() != original.content_digest()


@pytest.mark.parametrize(
    ("changes", "code"),
    [
        ({"assessment_version": 1}, "ASSESSMENT_VERSION_NOT_INCREASING"),
        (
            {"assessment_version": 2, "competition": entity(EntityKind.COMPETITION, "l")},
            "ASSESSMENT_SCOPE_MISMATCH",
        ),
    ],
)
def test_invalid_successors_are_rejected(changes: dict[str, object], code: str) -> None:
    original = assessment()
    with pytest.raises(ContractError) as excinfo:
        require_successor(original, dataclasses.replace(original, **changes))
    assert excinfo.value.code == code


def test_successor_version_may_skip_numbers() -> None:
    # Regression for review P2-03: only ordering is frozen, not "+1" numbering.
    original = assessment()
    require_successor(original, dataclasses.replace(original, assessment_version=5))


def test_successor_may_share_known_at() -> None:
    original = assessment()
    require_successor(original, dataclasses.replace(original, assessment_version=2))


def test_successor_known_at_cannot_regress() -> None:
    original = assessment(known_at=datetime(2026, 7, 1, tzinfo=UTC))
    successor = dataclasses.replace(
        original, assessment_version=2, known_at=datetime(2026, 6, 15, tzinfo=UTC)
    )
    with pytest.raises(ContractError) as excinfo:
        require_successor(original, successor)
    assert excinfo.value.code == "ASSESSMENT_KNOWN_AT_REGRESSION"


def test_assessment_serialization_round_trip() -> None:
    value = assessment(competition=entity(EntityKind.COMPETITION, "premier-league"))
    restored = PredictabilityAssessment.from_json(value.to_json())
    assert restored == value
    assert restored.to_json() == value.to_json()
