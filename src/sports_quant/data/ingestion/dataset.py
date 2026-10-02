"""F3 materialization of a Football build and its reproducibility manifest.

``materialize_football`` is the only way F4 produces as-of data: it hands every
canonical observation to the F3 kernel (``point_in_time.manifest.materialize``) and
returns the canonical records F3 selected, grouped by kind. There is no
Football-specific as-of logic. The result is feature-ready in the sense that every
row is PIT-selected and lineage-backed; no feature is computed here.

``build_manifest`` records what is needed to reproduce a build: raw captures,
parser/ingestion/schema versions, code version, mapping table, counts and F3
evidence. Its ``content_hash`` excludes run identity and wall-clock times, so the
same inputs always yield the same hash.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import (
    Contract,
    ContractError,
    instant,
    require_aware_datetime,
    require_non_empty,
)
from sports_quant.contracts.reproducibility import ArtifactRef, CodeVersion
from sports_quant.data.canonical.football import (
    CANONICAL_SCHEMA_VERSION,
    FixtureRecord,
    MatchResultRecord,
    OddsObservationRecord,
)
from sports_quant.data.entity_resolution.mapping import MappingTable
from sports_quant.data.ingestion.football import (
    INGESTION_VERSION,
    PARSER_VERSIONS,
    CaptureMode,
    FootballBuild,
    RecordKind,
)
from sports_quant.data.point_in_time.manifest import PitManifest, materialize
from sports_quant.data.point_in_time.selection import SelectionStatus
from sports_quant.data.snapshots.raw import RawCapture

DATASET_SCHEMA_VERSION = "f4-football-pit-dataset-1"


@dataclass(frozen=True, kw_only=True)
class FootballPitDataset(Contract):
    """Canonical records usable at ``manifest.body.decision_cutoff_at``, per F3."""

    manifest: PitManifest
    fixtures: tuple[FixtureRecord, ...]
    results: tuple[MatchResultRecord, ...]
    odds: tuple[OddsObservationRecord, ...]
    unresolved_keys: tuple[str, ...]
    no_eligible_keys: tuple[str, ...]


def materialize_football(
    build: FootballBuild,
    *,
    decision_cutoff_at: datetime,
    code_version: CodeVersion,
    dataset_ref: ArtifactRef,
    created_at: datetime,
) -> FootballPitDataset:
    if not build.observations:
        raise ContractError("EMPTY_BUILD", "nothing to materialize")
    materialization = materialize(
        build.pit_records(),
        decision_cutoff_at=decision_cutoff_at,
        code_version=code_version,
        dataset_ref=dataset_ref,
        created_at=created_at,
    )
    by_digest = build.by_record_digest()
    selected = [by_digest[record.content_digest()] for record in materialization.selected]
    outcomes = materialization.manifest.body.key_outcomes
    return FootballPitDataset(
        manifest=materialization.manifest,
        fixtures=tuple(o.fixture for o in selected if o.fixture is not None),
        results=tuple(o.result for o in selected if o.result is not None),
        odds=tuple(o.odds for o in selected if o.odds is not None),
        unresolved_keys=tuple(
            o.logical_key for o in outcomes if o.status is SelectionStatus.UNRESOLVED
        ),
        no_eligible_keys=tuple(
            o.logical_key for o in outcomes if o.status is SelectionStatus.NO_ELIGIBLE_VERSION
        ),
    )


@dataclass(frozen=True, kw_only=True)
class NamedCount(Contract):
    name: str
    count: int

    def _validate(self) -> None:
        require_non_empty(self.name, "name")
        if self.count < 0:
            raise ContractError("INVALID_COUNT", "counts are >= 0")


@dataclass(frozen=True, kw_only=True)
class NamedVersion(Contract):
    name: str
    version: str


@dataclass(frozen=True, kw_only=True)
class PitEvidence(Contract):
    """What F3 decided for one cutoff, pinned by its manifest hash."""

    decision_cutoff_at: datetime
    manifest_content_hash: str
    selected_keys: int
    unresolved_keys: int
    no_eligible_keys: int


@dataclass(frozen=True, kw_only=True)
class FootballBuildManifestBody(Contract):
    dataset_schema_version: str
    canonical_schema_version: str
    ingestion_version: str
    parser_versions: tuple[NamedVersion, ...]
    code_version: CodeVersion
    capture_mode: CaptureMode
    openfootball_timezone: str
    mapping_table_sha256: str
    raw_captures: tuple[RawCapture, ...]
    record_counts: tuple[NamedCount, ...]
    issue_counts: tuple[NamedCount, ...]
    gap_count: int
    conflict_count: int
    unresolved_identifier_count: int
    observations_sha256: str
    pit_evidence: tuple[PitEvidence, ...]

    def _validate(self) -> None:
        ids = tuple(c.capture_id for c in self.raw_captures)
        if ids != tuple(sorted(set(ids))):
            raise ContractError("NON_CANONICAL_MANIFEST", "captures must be unique+ordered")
        cutoffs = tuple(instant(e.decision_cutoff_at) for e in self.pit_evidence)
        if cutoffs != tuple(sorted(set(cutoffs))):
            raise ContractError("NON_CANONICAL_MANIFEST", "PIT evidence must be unique+ordered")


@dataclass(frozen=True, kw_only=True)
class FootballBuildManifest(Contract):
    body: FootballBuildManifestBody
    content_hash: str
    extraction_run_id: str
    extraction_started_at: datetime
    extraction_completed_at: datetime

    def _validate(self) -> None:
        require_non_empty(self.extraction_run_id, "extraction_run_id")
        if self.content_hash != self.body.content_digest():
            raise ContractError("CONTENT_HASH_MISMATCH", "content_hash must hash the body")
        if instant(self.extraction_completed_at) < instant(self.extraction_started_at):
            raise ContractError("INVALID_RUN_WINDOW", "run completed before it started")


def mapping_table_sha256(mappings: MappingTable) -> str:
    lines = "\n".join(mapping.to_json() for mapping in mappings.entries)
    return hashlib.sha256(lines.encode("ascii")).hexdigest()


def build_manifest(
    build: FootballBuild,
    *,
    raw_captures: Iterable[RawCapture],
    mappings: MappingTable,
    capture_mode: CaptureMode,
    openfootball_timezone: str,
    code_version: CodeVersion,
    datasets: Iterable[FootballPitDataset],
    extraction_run_id: str,
    extraction_started_at: datetime,
    extraction_completed_at: datetime,
) -> FootballBuildManifest:
    require_aware_datetime(extraction_started_at, "extraction_started_at")
    captures = {raw.capture_id: raw for raw in raw_captures}
    if tuple(sorted(captures)) != build.capture_ids:
        raise ContractError("CAPTURE_SET_MISMATCH", "captures must be exactly the build inputs")
    kinds = Counter(o.kind for o in build.observations)
    issues = Counter(issue.code for issue in build.issues)
    evidence = sorted(
        (
            PitEvidence(
                decision_cutoff_at=d.manifest.body.decision_cutoff_at,
                manifest_content_hash=d.manifest.content_hash,
                selected_keys=len(d.fixtures) + len(d.results) + len(d.odds),
                unresolved_keys=len(d.unresolved_keys),
                no_eligible_keys=len(d.no_eligible_keys),
            )
            for d in datasets
        ),
        key=lambda e: instant(e.decision_cutoff_at),
    )
    body = FootballBuildManifestBody(
        dataset_schema_version=DATASET_SCHEMA_VERSION,
        canonical_schema_version=CANONICAL_SCHEMA_VERSION,
        ingestion_version=INGESTION_VERSION,
        parser_versions=tuple(NamedVersion(name=s, version=v) for s, v in PARSER_VERSIONS),
        code_version=code_version,
        capture_mode=capture_mode,
        openfootball_timezone=openfootball_timezone,
        mapping_table_sha256=mapping_table_sha256(mappings),
        raw_captures=tuple(captures[capture_id] for capture_id in build.capture_ids),
        record_counts=tuple(NamedCount(name=k.value, count=kinds[k]) for k in RecordKind),
        issue_counts=tuple(NamedCount(name=code, count=issues[code]) for code in sorted(issues)),
        gap_count=len(build.gaps),
        conflict_count=len(build.conflicts),
        unresolved_identifier_count=len(build.unresolved),
        observations_sha256=hashlib.sha256(
            "\n".join(o.pit_record.content_digest() for o in build.observations).encode("ascii")
        ).hexdigest(),
        pit_evidence=tuple(evidence),
    )
    return FootballBuildManifest(
        body=body,
        content_hash=body.content_digest(),
        extraction_run_id=extraction_run_id,
        extraction_started_at=extraction_started_at,
        extraction_completed_at=extraction_completed_at,
    )
