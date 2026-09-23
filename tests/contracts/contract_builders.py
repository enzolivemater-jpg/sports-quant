"""Valid baseline contract instances shared by the F2 contract tests."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from typing import Any

from sports_quant.contracts.data_state import (
    ConflictState,
    DataState,
    FreshnessState,
    QualityState,
    VerificationState,
)
from sports_quant.contracts.decision import DecisionState
from sports_quant.contracts.entity import CanonicalEntityId, EntityKind, Sport
from sports_quant.contracts.gates import GateEvidenceRef, GateResult
from sports_quant.contracts.market import MarketDescriptor, MarketFamily
from sports_quant.contracts.market_risk import MarketRiskClass
from sports_quant.contracts.predictability import (
    EvaluationPeriod,
    EvidenceStatus,
    PredictabilityAssessment,
    SampleSize,
    SportPredictabilityClass,
)
from sports_quant.contracts.probability import ProbabilityEstimate
from sports_quant.contracts.provenance import Provenance
from sports_quant.contracts.reproducibility import (
    ArtifactKind,
    ArtifactRef,
    CodeVersion,
    ReproducibilityRef,
)
from sports_quant.contracts.source import SourceRef, SourceTier
from sports_quant.contracts.time import KnownAtBasis, TemporalMetadata

CUTOFF = datetime(2026, 9, 20, 18, 0, tzinfo=UTC)
COMMIT = "0f5201f3222c6fbbb36088bbf25d56e6acf1e76d"


def temporal(**overrides: Any) -> TemporalMetadata:
    base = TemporalMetadata(
        event_time=CUTOFF + timedelta(hours=2),
        published_at=CUTOFF - timedelta(hours=3),
        received_at=CUTOFF - timedelta(hours=2),
        valid_from=None,
        valid_to=None,
        expires_at=None,
        known_at=CUTOFF - timedelta(hours=2),
        known_at_basis=KnownAtBasis.SYSTEM_RECEIPT,
    )
    return replace(base, **overrides)


def data_state(**overrides: Any) -> DataState:
    base = DataState(
        quality=QualityState.VALID,
        freshness=FreshnessState.RECENT,
        verification=VerificationState.VERIFIED,
        conflict=ConflictState.NONE,
    )
    return replace(base, **overrides)


def provenance(**overrides: Any) -> Provenance:
    base = Provenance(
        source=SourceRef(source_id="provider-a", tier=SourceTier.OFFICIAL, source_version="v1"),
        external_id="ext-1",
        temporal=temporal(),
        data_state=data_state(),
        critical=True,
    )
    return replace(base, **overrides)


def entity(kind: EntityKind = EntityKind.TEAM, value: str = "team-1") -> CanonicalEntityId:
    return CanonicalEntityId(sport=Sport.FOOTBALL, kind=kind, value=value)


def artifact(kind: ArtifactKind, identifier: str = "artifact") -> ArtifactRef:
    return ArtifactRef(kind=kind, identifier=identifier, version="1")


def probability(**overrides: Any) -> ProbabilityEstimate:
    base = ProbabilityEstimate(
        selection_id="match-1:HOME",
        p_raw=0.58,
        p_calibrated=0.55,
        p_safe=0.52,
    )
    return replace(base, **overrides)


def market() -> MarketDescriptor:
    return MarketDescriptor(
        sport=Sport.FOOTBALL,
        market_family=MarketFamily.FOOTBALL_1X2,
        market_type="MATCH_RESULT",
        market_instance="match-1:1X2",
        mr_base=MarketRiskClass.MR2,
    )


def reproducibility() -> ReproducibilityRef:
    return ReproducibilityRef(
        run_id="run-1",
        code_version=CodeVersion(commit=COMMIT),
        data_ref=artifact(ArtifactKind.SNAPSHOT, "snapshot"),
        config_ref=artifact(ArtifactKind.CONFIGURATION, "config"),
        model_refs=(artifact(ArtifactKind.MODEL, "model"),),
    )


def gate(
    gate_id: str = "DATA_QUALITY_GATE",
    outcome: DecisionState = DecisionState.QUALIFIED,
    reason_codes: tuple[str, ...] = (),
) -> GateResult:
    return GateResult(
        gate_id=gate_id,
        outcome=outcome,
        reason_codes=reason_codes,
        evidence=(GateEvidenceRef(key="snapshot", reference="snapshot:1"),),
        evaluated_at=CUTOFF - timedelta(minutes=5),
        decision_cutoff_at=CUTOFF,
    )


def assessment(**overrides: Any) -> PredictabilityAssessment:
    base = PredictabilityAssessment(
        assessment_version=1,
        sport=Sport.FOOTBALL,
        market_family=MarketFamily.FOOTBALL_1X2.value,
        competition=None,
        predictability_prior=SportPredictabilityClass.SP3,
        predictability_empirical=None,
        evidence_status=EvidenceStatus.INSUFFICIENT,
        oos_brier=None,
        oos_log_loss=None,
        oos_ece=None,
        oos_skill=None,
        sample_sizes=(SampleSize(label="oos_matches", count=0),),
        evaluation_period=EvaluationPeriod(
            start=datetime(2025, 8, 1, tzinfo=UTC), end=datetime(2026, 5, 31, tzinfo=UTC)
        ),
        stability="not assessed",
        data_quality="not assessed",
        drift="not assessed",
        baseline_scope="market no-vig baseline (method pending OD-07)",
        model_scope="none",
        dataset_version_or_snapshot=artifact(ArtifactKind.SNAPSHOT, "football-oos"),
        code_version=CodeVersion(commit=COMMIT),
        known_at=datetime(2026, 6, 1, tzinfo=UTC),
    )
    return replace(base, **overrides)
