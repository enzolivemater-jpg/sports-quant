"""Immutable raw captures: the exact bytes a source returned, with their metadata.

A ``RawCapture`` describes one receipt by SPORTS QUANT of one source response. The
payload itself is stored separately, addressed by ``payload_sha256``. Captures are
never edited: a re-fetch, a correction or a retry is a new capture.

Secrets never enter a capture. Request parameters whose name is credential-like are
redacted at capture time, credentials embedded in the resource are rejected, and a
capture whose sensitive parameter is not redacted cannot be constructed.
"""

from __future__ import annotations

import hashlib
import urllib.parse
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from sports_quant.contracts.common import Contract, ContractError, require_non_empty
from sports_quant.data.point_in_time.records import RawSnapshotRef, require_sha256

REDACTED = "***REDACTED***"

SENSITIVE_PARAMETER_NAMES = frozenset(
    {
        "access-token",
        "access_token",
        "api-key",
        "api_key",
        "api_token",
        "apikey",
        "auth",
        "authorization",
        "key",
        "password",
        "secret",
        "token",
        "x-api-key",
        "x-apisports-key",
    }
)


def is_sensitive_parameter(name: str) -> bool:
    return name.lower() in SENSITIVE_PARAMETER_NAMES


@dataclass(frozen=True, kw_only=True)
class RequestParameter(Contract):
    name: str
    value: str

    def _validate(self) -> None:
        require_non_empty(self.name, "name")
        if is_sensitive_parameter(self.name) and self.value != REDACTED:
            raise ContractError(
                "UNREDACTED_SECRET", f"request parameter {self.name!r} must be redacted"
            )


@dataclass(frozen=True, kw_only=True)
class ProviderTimestamp(Contract):
    """A timestamp the source itself reported, kept verbatim under its source name."""

    name: str
    value: datetime

    def _validate(self) -> None:
        require_non_empty(self.name, "name")


@dataclass(frozen=True, kw_only=True)
class RawCapture(Contract):
    """Metadata of one immutable raw source response.

    ``resource`` names the endpoint or file (no query string, no credentials);
    ``source_revision`` is a version identifier declared or verifiable by the source
    (e.g. a Git blob SHA), ``None`` when the source exposes none. ``http_status`` is
    ``None`` for non-HTTP sources.
    """

    source_id: str
    resource: str
    request_parameters: tuple[RequestParameter, ...]
    received_at: datetime
    provider_timestamps: tuple[ProviderTimestamp, ...]
    source_revision: str | None
    payload_sha256: str
    payload_size: int
    media_type: str
    http_status: int | None
    ingestion_version: str

    def _validate(self) -> None:
        require_non_empty(self.source_id, "source_id")
        require_non_empty(self.media_type, "media_type")
        require_non_empty(self.ingestion_version, "ingestion_version")
        _require_clean_resource(self.resource)
        names = tuple(parameter.name for parameter in self.request_parameters)
        if names != tuple(sorted(set(names))):
            raise ContractError("NON_CANONICAL_PARAMETERS", "parameters must be unique+sorted")
        stamps = tuple(stamp.name for stamp in self.provider_timestamps)
        if stamps != tuple(sorted(set(stamps))):
            raise ContractError("NON_CANONICAL_TIMESTAMPS", "timestamps must be unique+sorted")
        if self.source_revision is not None:
            require_non_empty(self.source_revision, "source_revision")
        require_sha256(self.payload_sha256, "payload_sha256")
        if self.payload_size < 0:
            raise ContractError("INVALID_SIZE", "payload_size must be >= 0")
        if self.http_status is not None and not 100 <= self.http_status <= 599:
            raise ContractError("INVALID_HTTP_STATUS", "http_status must be in 100..599")

    @property
    def capture_id(self) -> str:
        """Identity of this capture: the digest of its full metadata."""

        return self.content_digest()

    @property
    def succeeded(self) -> bool:
        """Whether the source answered with content (non-HTTP sources always do)."""

        return self.http_status is None or 200 <= self.http_status <= 299

    def request_identity(self) -> str:
        query = urllib.parse.urlencode([(p.name, p.value) for p in self.request_parameters])
        return f"{self.resource}?{query}" if query else self.resource

    def parameter(self, name: str) -> str | None:
        for parameter in self.request_parameters:
            if parameter.name == name:
                return parameter.value
        return None

    def snapshot_ref(self) -> RawSnapshotRef:
        """F3 lineage hook for records normalized from this capture."""

        return RawSnapshotRef(
            source_id=self.source_id,
            request_identity=self.request_identity(),
            payload_sha256=self.payload_sha256,
            received_at=self.received_at,
            ingestion_version=self.ingestion_version,
        )


def _require_clean_resource(resource: str) -> None:
    require_non_empty(resource, "resource")
    parts = urllib.parse.urlsplit(resource)
    if parts.query or parts.fragment or "?" in resource:
        raise ContractError(
            "RESOURCE_HAS_QUERY", "pass request parameters separately, never in resource"
        )
    if parts.username is not None or parts.password is not None:
        raise ContractError("CREDENTIALS_IN_RESOURCE", "credentials must never be captured")


def sha256_hex(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def capture(
    payload: bytes,
    *,
    source_id: str,
    resource: str,
    request_parameters: Mapping[str, str],
    received_at: datetime,
    provider_timestamps: Mapping[str, datetime],
    source_revision: str | None,
    media_type: str,
    http_status: int | None,
    ingestion_version: str,
) -> RawCapture:
    """Describe ``payload`` as a raw capture, redacting credential-like parameters."""

    return RawCapture(
        source_id=source_id,
        resource=resource,
        request_parameters=tuple(
            RequestParameter(name=name, value=REDACTED if is_sensitive_parameter(name) else value)
            for name, value in sorted(request_parameters.items())
        ),
        received_at=received_at,
        provider_timestamps=tuple(
            ProviderTimestamp(name=name, value=value)
            for name, value in sorted(provider_timestamps.items())
        ),
        source_revision=source_revision,
        payload_sha256=sha256_hex(payload),
        payload_size=len(payload),
        media_type=media_type,
        http_status=http_status,
        ingestion_version=ingestion_version,
    )
