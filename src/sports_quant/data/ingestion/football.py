"""Raw captures -> provider normalization -> canonical Football observations.

``build_football`` turns a set of immutable raw captures into canonical records,
each wrapped as an F3 ``PitRecord`` with full provenance and raw lineage. It never
reads a clock and never fetches anything; given the same captures, mappings and
context it returns the same build.

Temporal rule: the only ``known_at`` F4 assigns is ``SYSTEM_RECEIPT`` (``known_at``
= the capture's ``received_at``). Provider timestamps (snapshot times, last-update
times, Git history) are kept as data and never promoted to ``known_at``; no
``VERIFIED_SOURCE_AVAILABILITY`` mapping is approved for any source yet.

Nothing is dropped silently: unknown identifiers, unusable markets, unavailable
endpoints and disagreeing sources are reported in the build, and F4 never picks
between sources.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import (
    CanonicalEnum,
    Contract,
    ContractError,
    instant,
    require_identifier,
    require_non_empty,
)
from sports_quant.contracts.data_state import (
    ConflictState,
    DataState,
    FreshnessState,
    QualityState,
    VerificationState,
)
from sports_quant.contracts.entity import CanonicalEntityId, EntityKind, ProviderEntityRef
from sports_quant.contracts.market import MarketFamily
from sports_quant.contracts.provenance import Provenance
from sports_quant.contracts.source import SourceRef
from sports_quant.contracts.time import KnownAtBasis, TemporalMetadata
from sports_quant.data.canonical.football import (
    BookmakerRef,
    EventStatus,
    FixtureRecord,
    MatchResultRecord,
    OddsObservationRecord,
    OutcomeKey,
    phase_1_market,
)
from sports_quant.data.canonical.values import (
    IntValue,
    ValueState,
    missing_instant,
    missing_int,
    observed_int,
    quality_state,
)
from sports_quant.data.entity_resolution.football_epl import (
    NAMESPACE_BOOKMAKER,
    NAMESPACE_COMPETITION,
    NAMESPACE_SEASON,
    NAMESPACE_TEAM,
    competition_id,
    league_event_id,
    season_id,
    team_id,
)
from sports_quant.data.entity_resolution.mapping import MappingTable, Resolution, ResolutionStatus
from sports_quant.data.normalization import openfootball, the_odds_api
from sports_quant.data.point_in_time.records import PitRecord
from sports_quant.data.provenance.sources import OPENFOOTBALL, THE_ODDS_API, source_descriptor
from sports_quant.data.snapshots.raw import RawCapture, capture, sha256_hex

INGESTION_VERSION = "f4-football-ingestion-1"
PARSER_VERSIONS = (
    (OPENFOOTBALL, openfootball.PARSER_VERSION),
    (THE_ODDS_API, the_odds_api.PARSER_VERSION),
)
_ODDS_MARKETS = {"h2h": MarketFamily.FOOTBALL_1X2, "totals": MarketFamily.FOOTBALL_TOTAL_GOALS_MAIN}


_MappedOutcome = tuple[OutcomeKey | None, float | None, the_odds_api.OddsApiOutcome]


class RecordKind(CanonicalEnum):
    FIXTURE = "FIXTURE"
    RESULT = "RESULT"
    ODDS = "ODDS"


class CaptureMode(CanonicalEnum):
    """How captures were obtained; the only F4 input to the freshness axis.

    F4 defines no freshness windows (OD-13 is open). A retrospective capture of an
    archive is, by construction, not live or recent information: ``DELAYED``.
    """

    RETROSPECTIVE_ARCHIVE = "RETROSPECTIVE_ARCHIVE"


_FRESHNESS = {CaptureMode.RETROSPECTIVE_ARCHIVE: FreshnessState.DELAYED}
_FILE_KINDS = (RecordKind.FIXTURE, RecordKind.RESULT)


@dataclass(frozen=True, kw_only=True)
class CanonicalObservation(Contract):
    """One canonical record as observed in one capture, ready for F3."""

    kind: RecordKind
    capture_id: str
    pit_record: PitRecord
    fixture: FixtureRecord | None
    result: MatchResultRecord | None
    odds: OddsObservationRecord | None

    def _validate(self) -> None:
        present = {
            RecordKind.FIXTURE: self.fixture,
            RecordKind.RESULT: self.result,
            RecordKind.ODDS: self.odds,
        }
        if [kind for kind, record in present.items() if record is not None] != [self.kind]:
            raise ContractError("PAYLOAD_KIND_MISMATCH", f"exactly one {self.kind} payload")
        if self.pit_record.payload_sha256 != self.payload().content_digest():
            raise ContractError("PAYLOAD_DIGEST_MISMATCH", "PIT payload digest must hash record")

    def payload(self) -> Contract:
        record = self.fixture or self.result or self.odds
        assert record is not None
        return record


@dataclass(frozen=True, kw_only=True)
class BuildIssue(Contract):
    """Something visible that kept data out of, or degraded, the canonical layer."""

    code: str
    capture_id: str
    subject: str
    detail: str

    def _validate(self) -> None:
        require_identifier(self.code, "code")
        require_non_empty(self.subject, "subject")


@dataclass(frozen=True, kw_only=True)
class SourceGap(Contract):
    """A capture that produced no content, e.g. an HTTP error from the endpoint."""

    capture_id: str
    source_id: str
    resource: str
    state: ValueState
    http_status: int | None

    def _validate(self) -> None:
        if self.state is not ValueState.ENDPOINT_UNAVAILABLE:
            raise ContractError("INVALID_GAP_STATE", "a source gap is ENDPOINT_UNAVAILABLE")


@dataclass(frozen=True, kw_only=True)
class ConflictingObservation(Contract):
    source_id: str
    revision_id: str | None
    payload_sha256: str
    capture_id: str


@dataclass(frozen=True, kw_only=True)
class ObservationConflict(Contract):
    """Observations of one logical record that disagree. All are retained; none wins.

    Raised when different sources carry different content, or when one source
    version (same ``source_id`` and ``revision_id``) carries different content.
    Different revisions of one source are corrections, not conflicts.
    """

    logical_key: str
    observations: tuple[ConflictingObservation, ...]

    def _validate(self) -> None:
        require_non_empty(self.logical_key, "logical_key")
        digests = tuple(o.to_json() for o in self.observations)
        if digests != tuple(sorted(set(digests))) or len(self.observations) < 2:
            raise ContractError("NON_CANONICAL_CONFLICT", "observations must be unique+sorted")


@dataclass(frozen=True, kw_only=True)
class FootballBuild(Contract):
    observations: tuple[CanonicalObservation, ...]
    issues: tuple[BuildIssue, ...]
    gaps: tuple[SourceGap, ...]
    conflicts: tuple[ObservationConflict, ...]
    unresolved: tuple[Resolution, ...]
    capture_ids: tuple[str, ...]

    def _validate(self) -> None:
        for name, key in (
            ("observations", lambda o: (o.pit_record.logical_key, o.pit_record.content_digest())),
            ("issues", lambda i: i.to_json()),
            ("gaps", lambda g: g.capture_id),
            ("conflicts", lambda c: c.logical_key),
            ("unresolved", lambda r: r.to_json()),
            ("capture_ids", lambda c: c),
        ):
            keys = tuple(key(item) for item in getattr(self, name))
            if keys != tuple(sorted(set(keys))):
                raise ContractError("NON_CANONICAL_BUILD", f"{name} must be unique and ordered")

    def pit_records(self) -> tuple[PitRecord, ...]:
        return tuple(observation.pit_record for observation in self.observations)

    def by_record_digest(self) -> dict[str, CanonicalObservation]:
        return {o.pit_record.content_digest(): o for o in self.observations}


@dataclass(frozen=True, kw_only=True)
class IngestionContext:
    mappings: MappingTable
    capture_mode: CaptureMode
    openfootball_timezone: str


def git_blob_sha(payload: bytes) -> str:
    """Git's object id of ``payload``: the source-verifiable OpenFootball revision."""

    return hashlib.sha1(b"blob %d\0" % len(payload) + payload, usedforsecurity=False).hexdigest()


def openfootball_capture(payload: bytes, *, season_path: str, received_at: datetime) -> RawCapture:
    """Describe a local copy of an ``openfootball/england`` season file as a capture.

    The revision is the file's Git blob id, so it can be checked against the pinned
    manifest (``data/manifests/football_openfootball_epl_2000_2025_verified.json``).
    """

    return capture(
        payload,
        source_id=OPENFOOTBALL,
        resource=f"openfootball/england/{season_path}",
        request_parameters={},
        received_at=received_at,
        provider_timestamps={},
        source_revision=f"git-blob:{git_blob_sha(payload)}",
        media_type="text/plain; charset=utf-8",
        http_status=None,
        ingestion_version=INGESTION_VERSION,
    )


def build_football(
    captures: Iterable[tuple[RawCapture, bytes]], context: IngestionContext
) -> FootballBuild:
    builder = _Builder(context)
    unique: dict[str, tuple[RawCapture, bytes]] = {}
    for raw, payload in captures:
        if sha256_hex(payload) != raw.payload_sha256:
            raise ContractError("PAYLOAD_MISMATCH", f"capture {raw.capture_id} payload differs")
        unique[raw.capture_id] = (raw, payload)
    ordered = [unique[capture_id] for capture_id in sorted(unique)]
    # Fixtures first: odds events are resolved against canonical fixtures.
    for raw, payload in ordered:
        if raw.source_id != THE_ODDS_API:
            builder.ingest(raw, payload)
    for raw, payload in ordered:
        if raw.source_id == THE_ODDS_API:
            builder.ingest(raw, payload)
    return builder.finish(tuple(sorted(unique)))


class _Builder:
    def __init__(self, context: IngestionContext) -> None:
        self._context = context
        self._observations: dict[str, CanonicalObservation] = {}
        self._issues: set[BuildIssue] = set()
        self._gaps: list[SourceGap] = []
        self._unresolved: set[Resolution] = set()
        # resource -> revision -> (first capture, logical keys it carried)
        self._file_revisions: dict[str, dict[str, tuple[RawCapture, set[str]]]] = defaultdict(dict)
        self._fixtures: dict[tuple[CanonicalEntityId, CanonicalEntityId], set[FixtureRecord]] = (
            defaultdict(set)
        )

    # -- shared -------------------------------------------------------------------

    def ingest(self, raw: RawCapture, payload: bytes) -> None:
        descriptor = source_descriptor(raw.source_id)
        if not raw.succeeded:
            self._gaps.append(
                SourceGap(
                    capture_id=raw.capture_id,
                    source_id=raw.source_id,
                    resource=raw.resource,
                    state=ValueState.ENDPOINT_UNAVAILABLE,
                    http_status=raw.http_status,
                )
            )
            return
        source = descriptor.source_ref(raw.source_revision)
        if raw.source_id == OPENFOOTBALL:
            self._openfootball(raw, payload, source)
        elif raw.source_id == THE_ODDS_API:
            self._odds_api(raw, payload, source)
        else:  # pragma: no cover - every ingestible registry source is dispatched above
            raise ContractError("UNSUPPORTED_SOURCE", raw.source_id)

    def _issue(self, code: str, raw: RawCapture, subject: str, detail: str = "") -> None:
        self._issues.add(
            BuildIssue(code=code, capture_id=raw.capture_id, subject=subject, detail=detail)
        )

    def _resolve(self, raw: RawCapture, namespace: str, external_id: str) -> str | None:
        resolution = self._context.mappings.resolve(raw.source_id, namespace, external_id)
        if resolution.status is ResolutionStatus.RESOLVED:
            return resolution.canonical_value
        self._unresolved.add(resolution)
        self._issue(f"{resolution.status.value}_{namespace}", raw, external_id)
        return None

    def _add(
        self,
        kind: RecordKind,
        raw: RawCapture,
        source: SourceRef,
        *,
        logical_key: str,
        revision_id: str,
        record: FixtureRecord | MatchResultRecord | OddsObservationRecord,
        external_id: str,
        event_time: datetime | None,
        quality: QualityState,
    ) -> None:
        temporal = TemporalMetadata(
            event_time=event_time,
            published_at=None,
            received_at=raw.received_at,
            valid_from=None,
            valid_to=None,
            expires_at=None,
            known_at=raw.received_at,
            known_at_basis=KnownAtBasis.SYSTEM_RECEIPT,
        )
        pit_record = PitRecord(
            logical_key=logical_key,
            revision_id=revision_id,
            payload_sha256=record.content_digest(),
            provenance=Provenance(
                source=source,
                external_id=external_id,
                temporal=temporal,
                data_state=DataState(
                    quality=quality,
                    freshness=_FRESHNESS[self._context.capture_mode],
                    verification=VerificationState.UNVERIFIED,
                    conflict=ConflictState.NONE,
                ),
                critical=True,
            ),
            raw_snapshot=raw.snapshot_ref(),
        )
        observation = CanonicalObservation(
            kind=kind,
            capture_id=raw.capture_id,
            pit_record=pit_record,
            fixture=record if isinstance(record, FixtureRecord) else None,
            result=record if isinstance(record, MatchResultRecord) else None,
            odds=record if isinstance(record, OddsObservationRecord) else None,
        )
        self._observations[pit_record.content_digest()] = observation

    # -- OpenFootball ---------------------------------------------------------------

    def _openfootball(self, raw: RawCapture, payload: bytes, source: SourceRef) -> None:
        revision = f"git-blob:{git_blob_sha(payload)}"
        if raw.source_revision != revision:
            raise ContractError(
                "SOURCE_REVISION_MISMATCH",
                f"capture declares {raw.source_revision!r}, payload is {revision}",
            )
        season_file = openfootball.parse_season_file(
            payload, timezone_name=self._context.openfootball_timezone
        )
        competition_label = season_file.title.removesuffix(season_file.season_label).strip()
        competition_value = self._resolve(raw, NAMESPACE_COMPETITION, competition_label)
        season_value = self._resolve(raw, NAMESPACE_SEASON, season_file.title)
        if competition_value is None or season_value is None:
            return
        competition, season = competition_id(competition_value), season_id(season_value)
        revisions = self._file_revisions[raw.resource]
        known = revisions.get(revision)
        if known is None or instant(raw.received_at) < instant(known[0].received_at):
            revisions[revision] = (raw, known[1] if known else set())
        keys = revisions[revision][1]

        for match in season_file.matches:
            home_value = self._resolve(raw, NAMESPACE_TEAM, match.home_label)
            away_value = self._resolve(raw, NAMESPACE_TEAM, match.away_label)
            if home_value is None or away_value is None:
                self._issue("FIXTURE_NOT_CANONICALIZED", raw, f"line {match.line_number}")
                continue
            home, away = team_id(home_value), team_id(away_value)
            event = league_event_id(season, home, away)
            external_id = f"{season_file.title}|{match.home_label}|{match.away_label}"
            fixture = FixtureRecord(
                event_id=event,
                competition_id=competition,
                season_id=season,
                home_team_id=home,
                away_team_id=away,
                event_time=match.event_time,
                matchday=observed_int(match.matchday),
                provider_event_ref=ProviderEntityRef(
                    provider_id=OPENFOOTBALL, kind=EntityKind.EVENT, external_id=external_id
                ),
            )
            result = _openfootball_result(event, match)
            self._fixtures[(home, away)].add(fixture)
            keys.update(f"FOOTBALL_{kind.value}:{event.value}" for kind in _FILE_KINDS)
            for kind, record, values in (
                (RecordKind.FIXTURE, fixture, (fixture.matchday.state,)),
                (
                    RecordKind.RESULT,
                    result,
                    tuple(
                        v.state
                        for v in (
                            result.home_goals,
                            result.away_goals,
                            result.home_ht_goals,
                            result.away_ht_goals,
                            result.source_published_at,
                        )
                    ),
                ),
            ):
                self._add(
                    kind,
                    raw,
                    source,
                    logical_key=f"FOOTBALL_{kind.value}:{event.value}",
                    revision_id=revision,
                    record=record,
                    external_id=external_id,
                    event_time=match.event_time,
                    quality=quality_state(values),
                )

    # -- The Odds API ---------------------------------------------------------------

    def _odds_api(self, raw: RawCapture, payload: bytes, source: SourceRef) -> None:
        requested = raw.parameter("date")
        if requested is None:
            raise ContractError("MISSING_REQUESTED_DATE", "historical capture needs ?date=")
        snapshot = the_odds_api.parse_historical_odds(
            payload, requested_snapshot_at=the_odds_api.parse_utc(requested, "date")
        )
        revision = f"snapshot:{instant(snapshot.provider_snapshot_at).isoformat()}"
        for event in snapshot.events:
            event_id = self._odds_event(raw, event)
            if event_id is None:
                continue
            for bookmaker in event.bookmakers:
                bookmaker_value = self._resolve(raw, NAMESPACE_BOOKMAKER, bookmaker.key)
                if bookmaker_value is None:
                    continue
                ref = BookmakerRef(
                    provider_id=THE_ODDS_API,
                    external_key=bookmaker.key,
                    canonical_bookmaker_id=bookmaker_value,
                )
                for market in bookmaker.markets:
                    subject = f"{event.event_id}/{bookmaker.key}/{market.key}"
                    for outcome, line, provider_outcome in self._odds_outcomes(
                        raw, event, market, subject
                    ):
                        family = _ODDS_MARKETS[market.key]
                        record = OddsObservationRecord(
                            event_id=event_id,
                            bookmaker=ref,
                            market=phase_1_market(family, line),
                            outcome=outcome,
                            line=line,
                            decimal_odds=provider_outcome.price,
                            provider_snapshot_at=snapshot.provider_snapshot_at,
                            requested_snapshot_at=snapshot.requested_snapshot_at,
                            market_last_update_at=market.last_update,
                            bookmaker_last_update_at=bookmaker.last_update,
                            provider_outcome_label=provider_outcome.name,
                        )
                        quality = quality_state((record.decimal_odds.state,))
                        price = record.decimal_odds.value
                        if price is not None and price <= 1.0:
                            self._issue("ODDS_NOT_ABOVE_ONE", raw, subject, f"{price}")
                            quality = QualityState.ERROR
                        if record.decimal_odds.state is ValueState.PARSE_ERROR:
                            self._issue("ODDS_PRICE_PARSE_ERROR", raw, subject, outcome.value)
                        self._add(
                            RecordKind.ODDS,
                            raw,
                            source,
                            logical_key=record.logical_key(),
                            revision_id=revision,
                            record=record,
                            external_id=event.event_id,
                            event_time=None,
                            quality=quality,
                        )

    def _odds_event(
        self, raw: RawCapture, event: the_odds_api.OddsApiEvent
    ) -> CanonicalEntityId | None:
        """Canonical event of a provider event: resolved teams + exact kickoff instant."""

        competition_value = self._resolve(raw, NAMESPACE_COMPETITION, event.sport_key)
        home_value = self._resolve(raw, NAMESPACE_TEAM, event.home_team)
        away_value = self._resolve(raw, NAMESPACE_TEAM, event.away_team)
        if competition_value is None or home_value is None or away_value is None:
            self._issue("EVENT_NOT_CANONICALIZED", raw, event.event_id)
            return None
        candidates = {
            fixture.event_id
            for fixture in self._fixtures[(team_id(home_value), team_id(away_value))]
            if fixture.competition_id == competition_id(competition_value)
            and instant(fixture.event_time) == instant(event.commence_time)
        }
        if len(candidates) != 1:
            code = "EVENT_FIXTURE_UNMATCHED" if not candidates else "EVENT_FIXTURE_AMBIGUOUS"
            self._issue(code, raw, event.event_id, event.commence_time.isoformat())
            return None
        return candidates.pop()

    def _odds_outcomes(
        self,
        raw: RawCapture,
        event: the_odds_api.OddsApiEvent,
        market: the_odds_api.OddsApiMarket,
        subject: str,
    ) -> list[tuple[OutcomeKey, float | None, the_odds_api.OddsApiOutcome]]:
        family = _ODDS_MARKETS.get(market.key)
        if family is None:
            self._issue("NOT_PHASE_1_MARKET", raw, subject)
            return []
        names = [outcome.name for outcome in market.outcomes]
        points = {o.point for o in market.outcomes}
        if family is MarketFamily.FOOTBALL_TOTAL_GOALS_MAIN and (
            None in points or len(points) != 1
        ):
            # Only a single unambiguous line may be the main line; never merge lines.
            self._issue("MAIN_LINE_UNRESOLVED", raw, subject, repr(sorted(map(str, points))))
            return []
        if len(names) != len(set(names)):
            self._issue("DUPLICATE_OUTCOME", raw, subject)
            return []
        if family is MarketFamily.FOOTBALL_1X2:
            labels = {
                event.home_team: OutcomeKey.HOME,
                "Draw": OutcomeKey.DRAW,
                event.away_team: OutcomeKey.AWAY,
            }
            mapped: list[_MappedOutcome] = [(labels.get(o.name), None, o) for o in market.outcomes]
            if {key for key, _line, _o in mapped if key is not None} != set(labels.values()):
                self._issue("INCOMPLETE_1X2", raw, subject, ",".join(sorted(names)))
        else:
            labels = {"Over": OutcomeKey.OVER, "Under": OutcomeKey.UNDER}
            mapped = [(labels.get(o.name), o.point, o) for o in market.outcomes]
        result: list[tuple[OutcomeKey, float | None, the_odds_api.OddsApiOutcome]] = []
        for key, line, outcome in mapped:
            if key is None:
                self._issue("UNRECOGNIZED_OUTCOME", raw, subject, outcome.name)
                continue
            result.append((key, line, outcome))
        return result

    # -- finish ---------------------------------------------------------------------

    def _absences(self) -> None:
        """Report records an earlier file revision had and a later one dropped.

        F2/F3 define no supersession or deletion: F3 keeps selecting the last version
        of a dropped record. The drop is therefore surfaced here, never applied.
        """

        for revisions in self._file_revisions.values():
            ordered = sorted(revisions.items(), key=lambda item: instant(item[1][0].received_at))
            for index, (_revision, (_raw, keys)) in enumerate(ordered):
                for later_revision, (later_raw, later_keys) in ordered[index + 1 :]:
                    for key in sorted(keys - later_keys):
                        self._issue(
                            "RECORD_ABSENT_IN_LATER_REVISION", later_raw, key, later_revision
                        )

    def finish(self, capture_ids: tuple[str, ...]) -> FootballBuild:
        self._absences()
        observations = tuple(
            sorted(
                self._observations.values(),
                key=lambda o: (o.pit_record.logical_key, o.pit_record.content_digest()),
            )
        )
        return FootballBuild(
            observations=observations,
            issues=tuple(sorted(self._issues, key=lambda i: i.to_json())),
            gaps=tuple(sorted(self._gaps, key=lambda g: g.capture_id)),
            conflicts=detect_conflicts(observations),
            unresolved=tuple(sorted(self._unresolved, key=lambda r: r.to_json())),
            capture_ids=capture_ids,
        )


def _openfootball_result(
    event: CanonicalEntityId, match: openfootball.OpenFootballMatch
) -> MatchResultRecord:
    played = match.home_goals is not None and match.away_goals is not None

    def full_time(value: int | None) -> IntValue:
        return (
            observed_int(value) if value is not None else missing_int(ValueState.NOT_YET_PUBLISHED)
        )

    def half_time(value: int | None) -> IntValue:
        if value is not None:
            return observed_int(value)
        # A played match without a half-time score: the source simply omits it.
        return missing_int(
            ValueState.NOT_PROVIDED_BY_SOURCE if played else ValueState.NOT_YET_PUBLISHED
        )

    return MatchResultRecord(
        event_id=event,
        status=EventStatus.COMPLETED if played else EventStatus.SCHEDULED,
        home_goals=full_time(match.home_goals),
        away_goals=full_time(match.away_goals),
        home_ht_goals=half_time(match.home_ht_goals),
        away_ht_goals=half_time(match.away_ht_goals),
        # Football.TXT carries no publication timestamps at all.
        source_published_at=missing_instant(ValueState.UNSUPPORTED_BY_SOURCE),
    )


def detect_conflicts(
    observations: Iterable[CanonicalObservation],
) -> tuple[ObservationConflict, ...]:
    """Logical keys whose observations disagree across sources or within a version."""

    by_key: dict[str, list[CanonicalObservation]] = defaultdict(list)
    for observation in observations:
        by_key[observation.pit_record.logical_key].append(observation)
    conflicts = []
    for logical_key in sorted(by_key):
        group = by_key[logical_key]
        payloads_by_source: dict[str, set[str]] = defaultdict(set)
        payloads_by_version: dict[tuple[str, str | None], set[str]] = defaultdict(set)
        for o in group:
            source_id = o.pit_record.provenance.source.source_id
            payloads_by_source[source_id].add(o.pit_record.payload_sha256)
            payloads_by_version[(source_id, o.pit_record.revision_id)].add(
                o.pit_record.payload_sha256
            )
        cross_source = len(payloads_by_source) > 1 and (
            len(set().union(*payloads_by_source.values())) > 1
        )
        within_version = any(len(p) > 1 for p in payloads_by_version.values())
        if cross_source or within_version:
            members = {
                ConflictingObservation(
                    source_id=o.pit_record.provenance.source.source_id,
                    revision_id=o.pit_record.revision_id,
                    payload_sha256=o.pit_record.payload_sha256,
                    capture_id=o.capture_id,
                )
                for o in group
            }
            conflicts.append(
                ObservationConflict(
                    logical_key=logical_key,
                    observations=tuple(sorted(members, key=lambda m: m.to_json())),
                )
            )
    return tuple(conflicts)
