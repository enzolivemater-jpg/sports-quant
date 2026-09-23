"""Market Risk classes and modes.

MR is ordinal and structural. It is not a probability and never modifies P_safe.
``weighted_average_mr`` (OD-17) and composite Dynamic Market Risk (OD-16) are
DEFERRED and intentionally absent. Modes carry no parameters: a mode cannot alter
P_safe or weaken calibration, uncertainty, edge, data-quality or dependency gates.
"""

from __future__ import annotations

from sports_quant.contracts.common import CanonicalEnum


class MarketRiskClass(CanonicalEnum):
    MR1 = "MR1"
    MR2 = "MR2"
    MR3 = "MR3"
    MR4 = "MR4"
    MR5 = "MR5"
    MR6 = "MR6"

    @property
    def ordinal(self) -> int:
        """Ordinal rank (MR1=1 .. MR6=6). Order only; differences carry no meaning."""

        return int(self.value[2:])


class MarketRiskMode(CanonicalEnum):
    CONSERVATIVE = "CONSERVATIVE"
    BALANCED = "BALANCED"
    AGGRESSIVE = "AGGRESSIVE"
    SPECULATIVE = "SPECULATIVE"
