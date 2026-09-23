"""Provenance contract for material records.

Every field must be supplied explicitly; there are no provenance defaults.
"""

from __future__ import annotations

from dataclasses import dataclass

from sports_quant.contracts.common import Contract, ContractError, require_non_empty
from sports_quant.contracts.data_state import DataState
from sports_quant.contracts.source import SourceRef
from sports_quant.contracts.time import TemporalMetadata


@dataclass(frozen=True, kw_only=True)
class Provenance(Contract):
    """Where a record came from, when it became usable and what state it is in.

    ``critical`` records must carry a defensible ``known_at`` (with its basis).
    """

    source: SourceRef
    external_id: str | None
    temporal: TemporalMetadata
    data_state: DataState
    critical: bool

    def _validate(self) -> None:
        if self.external_id is not None:
            require_non_empty(self.external_id, "external_id")
        if self.temporal.received_at is None:
            raise ContractError("RECEIVED_AT_MISSING", "provenance requires received_at")
        if self.critical and self.temporal.known_at is None:
            raise ContractError(
                "KNOWN_AT_MISSING",
                "critical provenance requires an explicit known_at and known_at_basis",
            )
