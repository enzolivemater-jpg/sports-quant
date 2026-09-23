"""Gate result contract surface.

No S-Tier, model-agreement, drift or Sport Predictability thresholds are defined
here. A gate outcome is expressed as a canonical business decision state, and
outcomes combine only by precedence, so no aggregate score can override a
failing gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import (
    Contract,
    ContractError,
    require_non_empty,
    require_reason_code,
    require_unique,
)
from sports_quant.contracts.decision import DecisionState


@dataclass(frozen=True, kw_only=True)
class GateEvidenceRef(Contract):
    """Pointer to evidence a gate relied on; content is stored elsewhere."""

    key: str
    reference: str

    def _validate(self) -> None:
        require_non_empty(self.key, "key")
        require_non_empty(self.reference, "reference")


@dataclass(frozen=True, kw_only=True)
class GateResult(Contract):
    gate_id: str
    outcome: DecisionState
    reason_codes: tuple[str, ...]
    evidence: tuple[GateEvidenceRef, ...]
    evaluated_at: datetime
    decision_cutoff_at: datetime | None

    def _validate(self) -> None:
        require_reason_code(self.gate_id, "gate_id")
        for code in self.reason_codes:
            require_reason_code(code, "reason_codes")
        require_unique(self.reason_codes, "reason_codes")
        require_unique(tuple(item.key for item in self.evidence), "evidence keys")
        if self.outcome is not DecisionState.QUALIFIED and not self.reason_codes:
            raise ContractError(
                "REASON_CODE_REQUIRED", "a non-QUALIFIED gate outcome requires a reason code"
            )
