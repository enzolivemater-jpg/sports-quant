"""Qualitative dependency contract.

Quantitative dependency estimation (OD-19) and joint/Monte-Carlo modelling (OD-23)
belong to later phases.
"""

from __future__ import annotations

from dataclasses import dataclass

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    require_non_empty,
)


class DependencyClass(CanonicalEnum):
    INDEPENDENT = "independent"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    REDUNDANT = "redundant"
    CONTRADICTORY = "contradictory"


@dataclass(frozen=True, kw_only=True)
class DependencyAssertion(Contract):
    """Qualitative dependency between two selections, with its justification."""

    selection_a: str
    selection_b: str
    dependency_class: DependencyClass
    basis: str

    def _validate(self) -> None:
        require_non_empty(self.selection_a, "selection_a")
        require_non_empty(self.selection_b, "selection_b")
        require_non_empty(self.basis, "basis")
        if self.selection_a == self.selection_b:
            raise ContractError("SELF_DEPENDENCY", "a selection cannot depend on itself")
