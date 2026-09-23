"""Serializable version/reference identifiers for reproducibility.

References only: run manifests and backtest reproducibility are later phases.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    require_non_empty,
    require_unique,
)

_FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class ArtifactKind(CanonicalEnum):
    DATASET = "DATASET"
    SNAPSHOT = "SNAPSHOT"
    CONFIGURATION = "CONFIGURATION"
    MODEL = "MODEL"
    CALIBRATOR = "CALIBRATOR"


DATA_ARTIFACT_KINDS = frozenset({ArtifactKind.DATASET, ArtifactKind.SNAPSHOT})
MODEL_ARTIFACT_KINDS = frozenset({ArtifactKind.MODEL, ArtifactKind.CALIBRATOR})


@dataclass(frozen=True, kw_only=True)
class CodeVersion(Contract):
    """Full 40-character lowercase Git commit SHA."""

    commit: str

    def _validate(self) -> None:
        if not _FULL_SHA_RE.fullmatch(self.commit):
            raise ContractError(
                "INVALID_COMMIT_REF", "commit must be a full 40-character lowercase SHA"
            )


@dataclass(frozen=True, kw_only=True)
class ArtifactRef(Contract):
    kind: ArtifactKind
    identifier: str
    version: str

    def _validate(self) -> None:
        require_non_empty(self.identifier, "identifier")
        require_non_empty(self.version, "version")


def require_artifact_kind(ref: ArtifactRef, allowed: frozenset[ArtifactKind], field: str) -> None:
    if ref.kind not in allowed:
        raise ContractError(
            "ARTIFACT_KIND_MISMATCH",
            f"{field} must be one of {sorted(allowed)}, got {ref.kind}",
        )


@dataclass(frozen=True, kw_only=True)
class ReproducibilityRef(Contract):
    """Everything needed to identify the exact inputs of a run or assessment."""

    run_id: str
    code_version: CodeVersion
    data_ref: ArtifactRef
    config_ref: ArtifactRef
    model_refs: tuple[ArtifactRef, ...]

    def _validate(self) -> None:
        require_non_empty(self.run_id, "run_id")
        require_artifact_kind(self.data_ref, DATA_ARTIFACT_KINDS, "data_ref")
        require_artifact_kind(
            self.config_ref, frozenset({ArtifactKind.CONFIGURATION}), "config_ref"
        )
        for ref in self.model_refs:
            require_artifact_kind(ref, MODEL_ARTIFACT_KINDS, "model_refs")
        require_unique(self.model_refs, "model_refs")
