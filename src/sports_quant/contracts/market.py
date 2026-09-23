"""Market taxonomy and the frozen Football market catalog.

Only Football families are approved. Basketball and MMA/UFC catalogs are
NOT_DEFINED_DO_NOT_IMPLEMENT (OD-29); Handball, Volleyball and Tennis production
catalogs are not defined either.
"""

from __future__ import annotations

from dataclasses import dataclass

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    require_non_empty,
)
from sports_quant.contracts.entity import Sport
from sports_quant.contracts.market_risk import MarketRiskClass


class MarketFamily(CanonicalEnum):
    FOOTBALL_1X2 = "FOOTBALL_1X2"
    FOOTBALL_TOTAL_GOALS_MAIN = "FOOTBALL_TOTAL_GOALS_MAIN"
    FOOTBALL_ASIAN_HANDICAP = "FOOTBALL_ASIAN_HANDICAP"
    FOOTBALL_BTTS = "FOOTBALL_BTTS"
    FOOTBALL_TEAM_TOTALS = "FOOTBALL_TEAM_TOTALS"


class CatalogPhase(CanonicalEnum):
    PHASE_1 = "PHASE_1"
    PHASE_2 = "PHASE_2"


@dataclass(frozen=True, kw_only=True)
class MarketCatalogEntry(Contract):
    sport: Sport
    market_family: MarketFamily
    phase: CatalogPhase
    mr_base: MarketRiskClass


FOOTBALL_MARKET_CATALOG: tuple[MarketCatalogEntry, ...] = (
    MarketCatalogEntry(
        sport=Sport.FOOTBALL,
        market_family=MarketFamily.FOOTBALL_1X2,
        phase=CatalogPhase.PHASE_1,
        mr_base=MarketRiskClass.MR2,
    ),
    MarketCatalogEntry(
        sport=Sport.FOOTBALL,
        market_family=MarketFamily.FOOTBALL_TOTAL_GOALS_MAIN,
        phase=CatalogPhase.PHASE_1,
        mr_base=MarketRiskClass.MR2,
    ),
    MarketCatalogEntry(
        sport=Sport.FOOTBALL,
        market_family=MarketFamily.FOOTBALL_ASIAN_HANDICAP,
        phase=CatalogPhase.PHASE_2,
        mr_base=MarketRiskClass.MR2,
    ),
    MarketCatalogEntry(
        sport=Sport.FOOTBALL,
        market_family=MarketFamily.FOOTBALL_BTTS,
        phase=CatalogPhase.PHASE_2,
        mr_base=MarketRiskClass.MR2,
    ),
    MarketCatalogEntry(
        sport=Sport.FOOTBALL,
        market_family=MarketFamily.FOOTBALL_TEAM_TOTALS,
        phase=CatalogPhase.PHASE_2,
        mr_base=MarketRiskClass.MR2,
    ),
)

_CATALOG_BY_FAMILY = {entry.market_family: entry for entry in FOOTBALL_MARKET_CATALOG}


def catalog_entry(market_family: MarketFamily) -> MarketCatalogEntry:
    return _CATALOG_BY_FAMILY[market_family]


@dataclass(frozen=True, kw_only=True)
class MarketDescriptor(Contract):
    """A concrete market, placed in the sport / family / type / instance taxonomy.

    ``mr_base`` must match the sport-specific catalog entry for the family.
    """

    sport: Sport
    market_family: MarketFamily
    market_type: str
    market_instance: str
    mr_base: MarketRiskClass

    def _validate(self) -> None:
        require_non_empty(self.market_type, "market_type")
        require_non_empty(self.market_instance, "market_instance")
        entry = catalog_entry(self.market_family)
        if entry.sport is not self.sport:
            raise ContractError(
                "MARKET_SPORT_MISMATCH",
                f"{self.market_family} belongs to {entry.sport}, not {self.sport}",
            )
        if entry.mr_base is not self.mr_base:
            raise ContractError(
                "MR_BASE_MISMATCH",
                f"{self.market_family} has catalog MR_base {entry.mr_base}",
            )
