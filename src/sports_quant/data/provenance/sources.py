"""F4 source registry: identity, F2 taxonomy tier and governance state of every source.

OD-24 (paid sports/odds providers) is OPEN. Nothing here approves a provider:
every descriptor is ``NOT_APPROVED``, and a role is a candidate/research role taken
from the provider evidence matrix, never a production assignment. The registry
introduces no source ranking; F4 never arbitrates between sources.

A source can feed the data layer only if it has an assigned F2 ``SourceTier`` and an
implemented adapter. Sources without an adapter carry no tier, so no record can be
attributed to them by accident.
"""

from __future__ import annotations

from dataclasses import dataclass

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    require_non_empty,
    require_unique,
)
from sports_quant.contracts.source import SourceRef, SourceTier


class SourceRole(CanonicalEnum):
    """Research/candidate role recorded in the provider evidence matrix (not approval)."""

    RESULTS_BASELINE_RESEARCH = "RESULTS_BASELINE_RESEARCH"
    CANDIDATE_HISTORICAL_ODDS = "CANDIDATE_HISTORICAL_ODDS"
    CANDIDATE_PROSPECTIVE_CONTEXT = "CANDIDATE_PROSPECTIVE_CONTEXT"
    CANDIDATE_BROAD_FOOTBALL_PROVIDER = "CANDIDATE_BROAD_FOOTBALL_PROVIDER"
    CANDIDATE_LICENSED_COMPREHENSIVE_DATA = "CANDIDATE_LICENSED_COMPREHENSIVE_DATA"
    VERIFIED_RESEARCH_SANDBOX = "VERIFIED_RESEARCH_SANDBOX"


class ProviderApproval(CanonicalEnum):
    """Only governance (OD-24 resolution) may add an approved state."""

    NOT_APPROVED = "NOT_APPROVED"


class AdapterState(CanonicalEnum):
    EXPERIMENTAL = "EXPERIMENTAL"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


class LiveIngestionState(CanonicalEnum):
    """Whether F4 can obtain data from the source itself (it never fetches)."""

    LOCAL_PINNED_FILE_ONLY = "LOCAL_PINNED_FILE_ONLY"
    EXPLICITLY_BLOCKED_WITH_EVIDENCE = "EXPLICITLY_BLOCKED_WITH_EVIDENCE"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"


@dataclass(frozen=True, kw_only=True)
class SourceDescriptor(Contract):
    source_id: str
    display_name: str
    tier: SourceTier | None
    roles: tuple[SourceRole, ...]
    approval: ProviderApproval
    adapter: AdapterState
    live_ingestion: LiveIngestionState
    evidence: str

    def _validate(self) -> None:
        require_non_empty(self.source_id, "source_id")
        require_non_empty(self.display_name, "display_name")
        require_non_empty(self.evidence, "evidence")
        require_unique(self.roles, "roles")
        if not self.roles:
            raise ContractError("EMPTY_VALUE", "a source needs at least one recorded role")
        if (self.adapter is AdapterState.EXPERIMENTAL) != (self.tier is not None):
            raise ContractError(
                "SOURCE_TIER_ADAPTER_MISMATCH",
                "exactly the sources with an implemented adapter carry a tier",
            )

    def source_ref(self, source_version: str | None) -> SourceRef:
        """The F2 ``SourceRef`` for a record from this source."""

        if self.tier is None or self.adapter is not AdapterState.EXPERIMENTAL:
            raise ContractError(
                "SOURCE_NOT_INGESTIBLE", f"{self.source_id} has no implemented adapter"
            )
        return SourceRef(source_id=self.source_id, tier=self.tier, source_version=source_version)


OPENFOOTBALL = "openfootball"
THE_ODDS_API = "the_odds_api"
STATSBOMB_OPEN_DATA = "statsbomb_open_data"
API_FOOTBALL = "api_football"
SPORTMONKS = "sportmonks"
SPORTRADAR = "sportradar"

SOURCE_REGISTRY: tuple[SourceDescriptor, ...] = (
    SourceDescriptor(
        source_id=OPENFOOTBALL,
        display_name="OpenFootball openfootball/england (CC0)",
        tier=SourceTier.AGGREGATOR,
        roles=(SourceRole.RESULTS_BASELINE_RESEARCH,),
        approval=ProviderApproval.NOT_APPROVED,
        adapter=AdapterState.EXPERIMENTAL,
        live_ingestion=LiveIngestionState.LOCAL_PINNED_FILE_ONLY,
        evidence="docs/research/FOOTBALL_OPENFOOTBALL_BASELINE_SOURCE_v0.1.md",
    ),
    SourceDescriptor(
        source_id=THE_ODDS_API,
        display_name="The Odds API (historical odds)",
        tier=SourceTier.AGGREGATOR,
        roles=(SourceRole.CANDIDATE_HISTORICAL_ODDS,),
        approval=ProviderApproval.NOT_APPROVED,
        adapter=AdapterState.EXPERIMENTAL,
        live_ingestion=LiveIngestionState.EXPLICITLY_BLOCKED_WITH_EVIDENCE,
        evidence="docs/research/FOOTBALL_F4_HISTORICAL_ODDS_BLOCK.md",
    ),
    SourceDescriptor(
        source_id=STATSBOMB_OPEN_DATA,
        display_name="StatsBomb Open Data",
        tier=None,
        roles=(SourceRole.VERIFIED_RESEARCH_SANDBOX,),
        approval=ProviderApproval.NOT_APPROVED,
        adapter=AdapterState.NOT_IMPLEMENTED,
        live_ingestion=LiveIngestionState.NOT_IMPLEMENTED,
        evidence="docs/research/STATSBOMB_OPEN_EPL_2015_16_PROBE.md",
    ),
    SourceDescriptor(
        source_id=API_FOOTBALL,
        display_name="API-Football",
        tier=None,
        roles=(SourceRole.CANDIDATE_PROSPECTIVE_CONTEXT,),
        approval=ProviderApproval.NOT_APPROVED,
        adapter=AdapterState.NOT_IMPLEMENTED,
        live_ingestion=LiveIngestionState.NOT_IMPLEMENTED,
        evidence="docs/research/FOOTBALL_PROVIDER_EVIDENCE_MATRIX_v0.1.md",
    ),
    SourceDescriptor(
        source_id=SPORTMONKS,
        display_name="Sportmonks",
        tier=None,
        roles=(SourceRole.CANDIDATE_BROAD_FOOTBALL_PROVIDER,),
        approval=ProviderApproval.NOT_APPROVED,
        adapter=AdapterState.NOT_IMPLEMENTED,
        live_ingestion=LiveIngestionState.NOT_IMPLEMENTED,
        evidence="docs/research/FOOTBALL_PROVIDER_EVIDENCE_MATRIX_v0.1.md",
    ),
    SourceDescriptor(
        source_id=SPORTRADAR,
        display_name="Sportradar Soccer",
        tier=None,
        roles=(SourceRole.CANDIDATE_LICENSED_COMPREHENSIVE_DATA,),
        approval=ProviderApproval.NOT_APPROVED,
        adapter=AdapterState.NOT_IMPLEMENTED,
        live_ingestion=LiveIngestionState.NOT_IMPLEMENTED,
        evidence="docs/research/FOOTBALL_PROVIDER_EVIDENCE_MATRIX_v0.1.md",
    ),
)

_BY_ID = {descriptor.source_id: descriptor for descriptor in SOURCE_REGISTRY}


def source_descriptor(source_id: str) -> SourceDescriptor:
    try:
        return _BY_ID[source_id]
    except KeyError:
        raise ContractError("UNKNOWN_SOURCE", f"{source_id!r} is not a registered source") from None
