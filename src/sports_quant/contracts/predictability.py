"""Sport Predictability assessment contract.

SP is classified at SPORT x MARKET_FAMILY (optionally competition), with separate
prior and empirical classes. It is not P_safe, edge, uncertainty, Market Risk, odds
or profitability, and it bypasses no gate. There is no numeric SP score, no
empirical admission threshold and no parlay aggregation.

The assessed market family is an opaque scope identifier, deliberately
independent of the production market catalog (``market.MarketFamily``): the
validation-only sports (Handball, Volleyball, Tennis) must be assessable before
any production catalog exists, and assessing a scope never adds it to that
catalog.

Assessments are immutable; a revision is a new assessment with a higher
``assessment_version`` and a ``known_at`` no earlier than its predecessor's, so
later phases can retrieve the version known at any cutoff.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    require_identifier,
    require_non_empty,
    require_probability,
    require_unique,
)
from sports_quant.contracts.entity import CanonicalEntityId, EntityKind, Sport
from sports_quant.contracts.reproducibility import (
    DATA_ARTIFACT_KINDS,
    ArtifactRef,
    CodeVersion,
    require_artifact_kind,
)


class SportPredictabilityClass(CanonicalEnum):
    SP1 = "SP1"
    SP2 = "SP2"
    SP3 = "SP3"
    SP4 = "SP4"
    SP5 = "SP5"


class EvidenceStatus(CanonicalEnum):
    INSUFFICIENT = "INSUFFICIENT"
    PROVISIONAL = "PROVISIONAL"
    VALIDATED = "VALIDATED"
    DEGRADED = "DEGRADED"


@dataclass(frozen=True, kw_only=True)
class SampleSize(Contract):
    label: str
    count: int

    def _validate(self) -> None:
        require_non_empty(self.label, "label")
        if self.count < 0:
            raise ContractError("NEGATIVE_SAMPLE_SIZE", "count must be >= 0")


@dataclass(frozen=True, kw_only=True)
class EvaluationPeriod(Contract):
    start: datetime
    end: datetime

    def _validate(self) -> None:
        if self.start > self.end:
            raise ContractError("INVALID_EVALUATION_PERIOD", "start must be <= end")


@dataclass(frozen=True, kw_only=True)
class PredictabilityAssessment(Contract):
    """One immutable, versioned Sport Predictability assessment.

    ``market_family`` is an UPPER_SNAKE_CASE scope identifier (for approved Football
    production families it is the ``MarketFamily`` value); it is not validated
    against, and does not extend, the production catalog.

    Out-of-sample metrics are ``None`` when not measured. ``stability``,
    ``data_quality`` and ``drift`` are descriptors/evidence references only; drift
    thresholds remain open (OD-09).
    """

    assessment_version: int
    sport: Sport
    market_family: str
    competition: CanonicalEntityId | None
    predictability_prior: SportPredictabilityClass | None
    predictability_empirical: SportPredictabilityClass | None
    evidence_status: EvidenceStatus
    oos_brier: float | None
    oos_log_loss: float | None
    oos_ece: float | None
    oos_skill: float | None
    sample_sizes: tuple[SampleSize, ...]
    evaluation_period: EvaluationPeriod
    stability: str
    data_quality: str
    drift: str
    baseline_scope: str
    model_scope: str
    dataset_version_or_snapshot: ArtifactRef
    code_version: CodeVersion
    known_at: datetime

    @property
    def scope_key(self) -> tuple[Sport, str, CanonicalEntityId | None]:
        """Identity shared by all versions of the same assessment scope."""

        return (self.sport, self.market_family, self.competition)

    def _validate(self) -> None:
        if self.assessment_version < 1:
            raise ContractError("INVALID_ASSESSMENT_VERSION", "assessment_version must be >= 1")
        require_identifier(self.market_family, "market_family")
        if self.competition is not None and (
            self.competition.kind is not EntityKind.COMPETITION
            or self.competition.sport is not self.sport
        ):
            raise ContractError(
                "INVALID_COMPETITION", "competition must be a COMPETITION of the same sport"
            )
        if (
            self.evidence_status is EvidenceStatus.VALIDATED
            and self.predictability_empirical is None
        ):
            raise ContractError(
                "EMPIRICAL_CLASS_REQUIRED",
                "VALIDATED evidence requires predictability_empirical",
            )
        if self.oos_brier is not None and self.oos_brier < 0:
            raise ContractError("INVALID_METRIC", "oos_brier must be >= 0")
        if self.oos_log_loss is not None and self.oos_log_loss < 0:
            raise ContractError("INVALID_METRIC", "oos_log_loss must be >= 0")
        if self.oos_ece is not None:
            require_probability(self.oos_ece, "oos_ece")
        require_unique(tuple(item.label for item in self.sample_sizes), "sample_sizes labels")
        for name in ("stability", "data_quality", "drift", "baseline_scope", "model_scope"):
            require_non_empty(getattr(self, name), name)
        require_artifact_kind(
            self.dataset_version_or_snapshot, DATA_ARTIFACT_KINDS, "dataset_version_or_snapshot"
        )
        if self.known_at < self.evaluation_period.end:
            raise ContractError(
                "KNOWN_AT_BEFORE_EVALUATION_END",
                "an assessment cannot be known before its evaluation period ends",
            )


def require_successor(
    previous: PredictabilityAssessment, successor: PredictabilityAssessment
) -> None:
    """Validate that ``successor`` can follow ``previous`` for as-of retrieval.

    Only ordering is required: same scope, a higher version, and no ``known_at``
    regression. Version numbering policy (e.g. gaps) is not constrained.
    """

    if successor.scope_key != previous.scope_key:
        raise ContractError("ASSESSMENT_SCOPE_MISMATCH", "successor must share the same scope")
    if successor.assessment_version <= previous.assessment_version:
        raise ContractError(
            "ASSESSMENT_VERSION_NOT_INCREASING",
            "successor assessment_version must be greater than previous",
        )
    if successor.known_at < previous.known_at:
        raise ContractError(
            "ASSESSMENT_KNOWN_AT_REGRESSION",
            "successor known_at cannot precede previous known_at",
        )
