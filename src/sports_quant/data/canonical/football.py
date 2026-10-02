"""Canonical Football records for the F4 pilot.

Only what the first milestone needs: fixtures, final results and Phase 1 odds
observations. Records hold canonical identifiers and explicit-missingness values;
provider labels survive only as provenance (``ProviderEntityRef``, outcome labels).

A canonical record is the *payload* of a point-in-time observation: its content
digest is the F3 ``payload_sha256``. Temporal metadata, source and ``DataState``
live in the F2 ``Provenance`` attached when the record becomes a ``PitRecord``.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    instant,
    require_non_empty,
)
from sports_quant.contracts.entity import CanonicalEntityId, EntityKind, ProviderEntityRef
from sports_quant.contracts.market import (
    CatalogPhase,
    MarketDescriptor,
    MarketFamily,
    catalog_entry,
)
from sports_quant.contracts.market_risk import MarketRiskClass
from sports_quant.data.canonical.values import DecimalValue, InstantValue, IntValue, ValueState

CANONICAL_SCHEMA_VERSION = "f4-football-canonical-1"

PHASE_1_MARKET_FAMILIES = frozenset(
    entry.market_family
    for entry in (catalog_entry(family) for family in MarketFamily)
    if entry.phase is CatalogPhase.PHASE_1
)


def _require_kind(entity: CanonicalEntityId, kind: EntityKind, field: str) -> None:
    if entity.kind is not kind:
        raise ContractError("ENTITY_KIND_MISMATCH", f"{field} must be a {kind} id")


class OutcomeKey(CanonicalEnum):
    HOME = "HOME"
    DRAW = "DRAW"
    AWAY = "AWAY"
    OVER = "OVER"
    UNDER = "UNDER"


class EventStatus(CanonicalEnum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"


@dataclass(frozen=True, kw_only=True)
class FixtureRecord(Contract):
    """Who plays whom, where in the competition, and the scheduled kickoff instant."""

    event_id: CanonicalEntityId
    competition_id: CanonicalEntityId
    season_id: CanonicalEntityId
    home_team_id: CanonicalEntityId
    away_team_id: CanonicalEntityId
    event_time: datetime
    matchday: IntValue
    provider_event_ref: ProviderEntityRef

    def _validate(self) -> None:
        _require_kind(self.event_id, EntityKind.EVENT, "event_id")
        _require_kind(self.competition_id, EntityKind.COMPETITION, "competition_id")
        _require_kind(self.season_id, EntityKind.SEASON, "season_id")
        _require_kind(self.home_team_id, EntityKind.TEAM, "home_team_id")
        _require_kind(self.away_team_id, EntityKind.TEAM, "away_team_id")
        if self.home_team_id == self.away_team_id:
            raise ContractError("SAME_TEAM_FIXTURE", "home and away teams must differ")
        if self.provider_event_ref.kind is not EntityKind.EVENT:
            raise ContractError("ENTITY_KIND_MISMATCH", "provider_event_ref must be an EVENT")


@dataclass(frozen=True, kw_only=True)
class MatchResultRecord(Contract):
    """Final result of one event: a label, never a pre-match feature of that event."""

    event_id: CanonicalEntityId
    status: EventStatus
    home_goals: IntValue
    away_goals: IntValue
    home_ht_goals: IntValue
    away_ht_goals: IntValue
    source_published_at: InstantValue

    def _validate(self) -> None:
        _require_kind(self.event_id, EntityKind.EVENT, "event_id")
        goals = (self.home_goals, self.away_goals, self.home_ht_goals, self.away_ht_goals)
        if any(v.value is not None and v.value < 0 for v in goals):
            raise ContractError("IMPOSSIBLE_SCORE", "goals cannot be negative")
        full_time_observed = {
            v.state is ValueState.OBSERVED for v in (self.home_goals, self.away_goals)
        }
        if len(full_time_observed) != 1:
            raise ContractError("PARTIAL_SCORE", "full-time score must be complete or absent")
        if (self.status is EventStatus.COMPLETED) != full_time_observed.pop():
            raise ContractError(
                "STATUS_SCORE_MISMATCH", "exactly COMPLETED events carry a full-time score"
            )
        for half, full in (
            (self.home_ht_goals, self.home_goals),
            (self.away_ht_goals, self.away_goals),
        ):
            if half.value is not None and (full.value is None or half.value > full.value):
                raise ContractError("IMPOSSIBLE_SCORE", "half-time goals exceed full-time goals")

    def outcome_1x2(self) -> OutcomeKey | None:
        if self.home_goals.value is None or self.away_goals.value is None:
            return None
        if self.home_goals.value > self.away_goals.value:
            return OutcomeKey.HOME
        if self.home_goals.value < self.away_goals.value:
            return OutcomeKey.AWAY
        return OutcomeKey.DRAW

    def total_goals(self) -> int | None:
        if self.home_goals.value is None or self.away_goals.value is None:
            return None
        return self.home_goals.value + self.away_goals.value


_OUTCOMES = {
    MarketFamily.FOOTBALL_1X2: frozenset({OutcomeKey.HOME, OutcomeKey.DRAW, OutcomeKey.AWAY}),
    MarketFamily.FOOTBALL_TOTAL_GOALS_MAIN: frozenset({OutcomeKey.OVER, OutcomeKey.UNDER}),
}


def phase_1_market(family: MarketFamily, line: float | None) -> MarketDescriptor:
    """Market descriptor of a Phase 1 Football market; anything else is rejected."""

    if family not in PHASE_1_MARKET_FAMILIES:
        raise ContractError("NOT_PHASE_1_MARKET", f"{family} is not a Phase 1 market")
    if family is MarketFamily.FOOTBALL_1X2:
        if line is not None:
            raise ContractError("UNEXPECTED_LINE", "1X2 has no line")
        market_type, instance = "1X2_FULL_TIME", "FULL_TIME"
    else:
        if line is None or line <= 0 or (line * 4) != int(line * 4):
            raise ContractError("INVALID_LINE", "total-goals line must be a positive quarter")
        market_type, instance = "TOTAL_GOALS_FULL_TIME", f"LINE_{line:g}"
    return MarketDescriptor(
        sport=catalog_entry(family).sport,
        market_family=family,
        market_type=market_type,
        market_instance=instance,
        mr_base=MarketRiskClass.MR2,
    )


@dataclass(frozen=True, kw_only=True)
class BookmakerRef(Contract):
    provider_id: str
    external_key: str
    canonical_bookmaker_id: str

    def _validate(self) -> None:
        require_non_empty(self.provider_id, "provider_id")
        require_non_empty(self.external_key, "external_key")
        require_non_empty(self.canonical_bookmaker_id, "canonical_bookmaker_id")


@dataclass(frozen=True, kw_only=True)
class OddsObservationRecord(Contract):
    """One price for one outcome, as one bookmaker showed it in one provider snapshot.

    Observations stay distinct by bookmaker, market, outcome and snapshot time, so
    no legitimate price change is ever deduplicated away. The provider's
    next-snapshot navigation timestamp is deliberately not a field.
    """

    event_id: CanonicalEntityId
    bookmaker: BookmakerRef
    market: MarketDescriptor
    outcome: OutcomeKey
    line: float | None
    decimal_odds: DecimalValue
    provider_snapshot_at: datetime
    requested_snapshot_at: datetime
    market_last_update_at: InstantValue
    bookmaker_last_update_at: InstantValue
    provider_outcome_label: str

    def _validate(self) -> None:
        _require_kind(self.event_id, EntityKind.EVENT, "event_id")
        require_non_empty(self.provider_outcome_label, "provider_outcome_label")
        if phase_1_market(self.market.market_family, self.line) != self.market:
            raise ContractError("MARKET_MISMATCH", "market does not match family and line")
        if self.outcome not in _OUTCOMES[self.market.market_family]:
            raise ContractError("OUTCOME_MISMATCH", f"{self.outcome} not in {self.market}")

    def logical_key(self) -> str:
        return ":".join(
            (
                "FOOTBALL_ODDS",
                self.event_id.value,
                self.bookmaker.canonical_bookmaker_id,
                self.market.market_family.value,
                self.market.market_instance,
                self.outcome.value,
                instant(self.provider_snapshot_at).isoformat(),
            )
        )
