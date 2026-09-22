#!/usr/bin/env python3
"""Render a research-only provider probe evidence skeleton from safe capture metadata."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = (ROOT / "data" / "research-probes").resolve()


def _require_research_metadata(metadata: dict[str, Any]) -> None:
    if metadata.get("research_only") is not True:
        raise ValueError("Metadata is not marked research_only=true")
    if metadata.get("canonical_known_at_assigned") is not False:
        raise ValueError("Metadata must record canonical_known_at_assigned=false")

    required = (
        "provider",
        "probe_name",
        "requested_at",
        "received_at",
        "request_url_redacted",
        "payload_sha256",
        "payload_bytes",
        "payload_file",
    )
    missing = [key for key in required if key not in metadata]
    if missing:
        raise ValueError("Metadata missing required field(s): " + ", ".join(missing))


def render_evidence(metadata: dict[str, Any]) -> str:
    _require_research_metadata(metadata)

    headers = metadata.get("selected_response_headers")
    if not isinstance(headers, dict):
        headers = {}

    header_lines = (
        "\n".join(f"- {key}: {value}" for key, value in sorted(headers.items()))
        if headers
        else "- None captured"
    )

    http_status = metadata.get("http_status")
    error = metadata.get("error")
    error_text = str(error) if error else "None"

    return f"""# Provider Probe Evidence — LOCAL RESEARCH DRAFT

Status: LOCAL_RESEARCH_EVIDENCE__NOT_PROVIDER_APPROVAL

Provider: {metadata["provider"]}
Probe: {metadata["probe_name"]}

## Capture facts

Requested at: {metadata["requested_at"]}
SPORTS QUANT received_at: {metadata["received_at"]}
HTTP status: {http_status}
Error: {error_text}
Redacted request URL: {metadata["request_url_redacted"]}
Payload SHA-256: {metadata["payload_sha256"]}
Payload bytes: {metadata["payload_bytes"]}
Local raw payload file: {metadata["payload_file"]}
Canonical known_at assigned: NO

Selected response headers:
{header_lines}

## Identity

Stable event ID:
UNKNOWN

Stable team IDs:
UNKNOWN

Stable player IDs if applicable:
UNKNOWN

Competition/season IDs:
UNKNOWN

Entity collisions observed:
UNKNOWN

Result:
UNKNOWN

## Timestamp semantics

Provider timestamp fields:
UNKNOWN

For each field classify as one of:
- event time
- validity time
- provider processing/update time
- retrieval time
- publication/availability time
- unclear

Any field defensibly usable as historical known_at:
UNKNOWN

Important:
SPORTS QUANT received_at is retrieval evidence only and must not be silently converted into historical known_at for underlying provider facts.

## Historical as-of behavior

Historical query supported:
UNKNOWN

Old versions/revisions retrievable:
UNKNOWN

Current state overwrites old state:
UNKNOWN

Returned snapshot guaranteed <= requested cutoff:
UNKNOWN

Observed contradictions:
UNKNOWN

Result:
UNKNOWN

## Coverage and missingness

Requested records:
UNKNOWN

Returned records:
UNKNOWN

Missing fixtures:
UNKNOWN

Missing markets/context:
UNKNOWN

Unsupported vs empty distinguishable:
UNKNOWN

Pagination complete:
UNKNOWN

Observed data gaps:
UNKNOWN

Result:
UNKNOWN

## Corrections / revisions

Repeat retrieval performed:
UNKNOWN

Payload changed:
UNKNOWN

Old payload retained locally:
YES

Provider exposes revision identity/time:
UNKNOWN

Historical previous version retrievable:
UNKNOWN

Result:
UNKNOWN

## Licensing / storage

Official terms/docs reviewed:
UNKNOWN

Raw storage allowed:
UNKNOWN

Retention limit:
UNKNOWN

Derived model use:
UNKNOWN

Decision-support/betting use:
UNKNOWN

Redistribution/display:
UNKNOWN

Ambiguities requiring written confirmation:
UNKNOWN

Result:
UNKNOWN

## Cost / quota

Requests consumed:
1 attempted capture

Credits consumed:
UNKNOWN

Rate-limit behavior:
Use captured headers above where meaningful; otherwise UNKNOWN.

Observed marginal cost:
UNKNOWN

Projected pilot cost:
UNKNOWN

Projected scale risk:
UNKNOWN

## Security

Key only from environment/secret store:
TO_VERIFY

Secret absent from captured metadata:
TO_VERIFY

Secret absent from committed repository:
TO_VERIFY

Security result:
UNKNOWN

## Proposed role outcome

Role tested:
UNKNOWN

Outcome:
UNKNOWN

Residual risks:
UNKNOWN

## OD-24 impact

Does this probe justify resolving any provider role?
NO — unless a later reviewed evidence record explicitly demonstrates sufficient PIT, licensing, coverage, cost and reproducibility evidence.

Remaining evidence required:
UNKNOWN

## Review rule

Do not commit this local draft as a verified provider conclusion without human review.

Do not replace UNKNOWN values with assumptions.
"""


def _resolve_local_path(path: Path) -> Path:
    resolved = path.resolve()
    resolved.relative_to(OUTPUT_ROOT)
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-only", action="store_true", required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if not args.research_only:
        print("This renderer may only run in research-only mode.", file=sys.stderr)
        return 2

    try:
        metadata_path = _resolve_local_path(args.metadata)
        if not metadata_path.is_file():
            raise ValueError(f"Metadata file does not exist: {metadata_path}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict):
            raise ValueError("Metadata JSON must be an object")

        output_path = (
            _resolve_local_path(args.output)
            if args.output is not None
            else metadata_path.with_suffix(".evidence.md")
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_evidence(metadata), encoding="utf-8")
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"Evidence rendering error: {exc}", file=sys.stderr)
        return 1

    print(f"Rendered local research evidence draft -> {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
