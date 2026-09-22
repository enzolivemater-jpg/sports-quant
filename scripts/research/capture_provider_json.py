#!/usr/bin/env python3
"""Research-only HTTP JSON capture harness for provider bake-offs.

This script is deliberately outside the production data layer.
It records retrieval evidence only. It MUST NOT assign canonical known_at,
normalize provider entities, or feed production decisions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = (ROOT / "data" / "research-probes").resolve()

SENSITIVE_QUERY_KEYS = {
    "api_key",
    "apikey",
    "api-key",
    "api_token",
    "key",
    "token",
    "access_token",
    "access-token",
    "x-api-key",
    "x-apisports-key",
    "auth",
    "authorization",
}


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _redact_url(url: str, extra_sensitive_keys: set[str] | None = None) -> str:
    parts = urllib.parse.urlsplit(url)
    sensitive_keys = set(SENSITIVE_QUERY_KEYS)
    if extra_sensitive_keys:
        sensitive_keys.update(key.lower() for key in extra_sensitive_keys)

    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    redacted = [
        (key, "***REDACTED***" if key.lower() in sensitive_keys else value) for key, value in query
    ]
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(redacted), parts.fragment)
    )


def _parse_env_assignments(items: list[str], option_name: str) -> list[tuple[str, str]]:
    values: list[tuple[str, str]] = []
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid {option_name} value {item!r}; expected NAME=ENV_VAR")
        name, env_name = item.split("=", 1)
        name = name.strip()
        env_name = env_name.strip()
        if not name or not env_name:
            raise ValueError(f"Invalid {option_name} value {item!r}")
        value = os.environ.get(env_name)
        if not value:
            raise ValueError(f"Missing required environment variable: {env_name}")
        values.append((name, value))
    return values


def _parse_header_env(items: list[str]) -> dict[str, str]:
    return dict(_parse_env_assignments(items, "--header-env"))


def _build_request_url(url: str, query_env: list[str]) -> tuple[str, set[str]]:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https":
        raise ValueError("Only HTTPS provider URLs are allowed.")
    if parts.username is not None or parts.password is not None:
        raise ValueError("Credentials embedded in provider URLs are prohibited.")

    existing_query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    direct_sensitive = sorted(
        {key for key, _value in existing_query if key.lower() in SENSITIVE_QUERY_KEYS}
    )
    if direct_sensitive:
        joined = ", ".join(direct_sensitive)
        raise ValueError(
            "Sensitive query parameter(s) must use --query-env instead of --url: " + joined
        )

    injected = _parse_env_assignments(query_env, "--query-env")
    existing_names = {key for key, _value in existing_query}
    duplicates = sorted({key for key, _value in injected if key in existing_names})
    if duplicates:
        raise ValueError(
            "Query parameter provided both in --url and --query-env: " + ", ".join(duplicates)
        )

    request_query = urllib.parse.urlencode(existing_query + injected)
    request_url = urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, request_query, parts.fragment)
    )
    injected_names = {key for key, _value in injected}
    return request_url, injected_names


def _safe_output_dir(provider: str, probe_name: str) -> Path:
    safe_provider = "".join(ch for ch in provider if ch.isalnum() or ch in "-_").strip("._")
    safe_probe = "".join(ch for ch in probe_name if ch.isalnum() or ch in "-_").strip("._")
    if not safe_provider or not safe_probe:
        raise ValueError("provider and probe-name must contain safe filename characters")

    out = (OUTPUT_ROOT / safe_provider / safe_probe).resolve()
    out.relative_to(OUTPUT_ROOT)
    return out


def _json_or_text(body: bytes) -> tuple[Any | None, str]:
    text = body.decode("utf-8", errors="replace")
    try:
        return json.loads(text), text
    except json.JSONDecodeError:
        return None, text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-only", action="store_true", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--probe-name", required=True)
    parser.add_argument(
        "--url",
        required=True,
        help="HTTPS provider URL without credentials or sensitive query values.",
    )
    parser.add_argument(
        "--header-env",
        action="append",
        default=[],
        metavar="HEADER=ENV_VAR",
        help="Read a secret/non-secret header value from an environment variable.",
    )
    parser.add_argument(
        "--query-env",
        action="append",
        default=[],
        metavar="PARAM=ENV_VAR",
        help="Inject a query parameter from an environment variable without exposing its value.",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    if not args.research_only:
        print("This harness may only run in research-only mode.", file=sys.stderr)
        return 2

    try:
        headers = _parse_header_env(args.header_env)
        request_url, injected_query_keys = _build_request_url(args.url, args.query_env)
        output_dir = _safe_output_dir(args.provider, args.probe_name)
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    output_dir.mkdir(parents=True, exist_ok=True)

    requested_at = _utc_now()
    request = urllib.request.Request(request_url, headers=headers, method="GET")

    status: int | None = None
    response_headers: dict[str, str] = {}
    body = b""
    error: str | None = None

    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            status = response.status
            response_headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower()
                in {
                    "content-type",
                    "date",
                    "etag",
                    "last-modified",
                    "x-ratelimit-limit",
                    "x-ratelimit-remaining",
                    "x-ratelimit-reset",
                }
            }
            body = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        response_headers = {
            key: value
            for key, value in exc.headers.items()
            if key.lower()
            in {
                "content-type",
                "date",
                "etag",
                "last-modified",
                "x-ratelimit-limit",
                "x-ratelimit-remaining",
                "x-ratelimit-reset",
            }
        }
        body = exc.read()
        error = f"HTTPError {exc.code}: {exc.reason}"
    except urllib.error.URLError as exc:
        error = f"URLError: {exc.reason}"

    received_at = _utc_now()
    digest = hashlib.sha256(body).hexdigest()
    parsed_json, decoded_text = _json_or_text(body)

    stamp = received_at.replace(":", "").replace("+00:00", "Z").replace(".", "_")
    stem = f"{stamp}_{digest[:12]}"

    raw_path = output_dir / f"{stem}.json"
    if parsed_json is not None:
        raw_path.write_text(
            json.dumps(parsed_json, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    else:
        raw_path = output_dir / f"{stem}.txt"
        raw_path.write_text(decoded_text, encoding="utf-8")

    metadata = {
        "research_only": True,
        "provider": args.provider,
        "probe_name": args.probe_name,
        "requested_at": requested_at,
        "received_at": received_at,
        "request_url_redacted": _redact_url(request_url, injected_query_keys),
        "http_status": status,
        "selected_response_headers": response_headers,
        "payload_sha256": digest,
        "payload_bytes": len(body),
        "payload_file": raw_path.name,
        "error": error,
        "canonical_known_at_assigned": False,
        "warning": (
            "This capture is research evidence only. received_at is SPORTS QUANT retrieval time; "
            "it is not automatically canonical known_at for any underlying provider field."
        ),
    }
    metadata_path = output_dir / f"{stem}.metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0 if error is None and status is not None and 200 <= status < 300 else 1


if __name__ == "__main__":
    sys.exit(main())
