#!/usr/bin/env python3
"""Plan or execute The Odds API historical Stage A research probes safely."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "manifests" / "football_odds_stage_a_epl_2024_25.json"
HARNESS = ROOT / "scripts" / "research" / "capture_provider_json.py"
KEY_ENV = "THE_ODDS_API_KEY"


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def build_probe_specs(data: dict[str, Any]) -> list[dict[str, str]]:
    sport_key = data["sport_key"]
    regions = ",".join(data["regions"])
    markets = ",".join(data["markets"])
    odds_format = data["odds_format"]

    base_url = f"https://api.the-odds-api.com/v4/historical/sports/{sport_key}/odds"
    specs: list[dict[str, str]] = []

    for query in data["query_plan"]:
        params = urllib.parse.urlencode(
            {
                "regions": regions,
                "markets": markets,
                "oddsFormat": odds_format,
                "date": query["requested_snapshot_at_utc"],
            },
            safe=",",
        )
        cutoff_slug = query["cutoff"].lower().replace("-", "").replace("h", "h-")
        cutoff_slug = cutoff_slug.replace("m", "m")
        probe_name = f"stage-a-{query['group_id'].lower()}-{cutoff_slug}".strip("-")
        specs.append(
            {
                "group_id": query["group_id"],
                "cutoff": query["cutoff"],
                "requested_snapshot_at_utc": query["requested_snapshot_at_utc"],
                "probe_name": probe_name,
                "url": f"{base_url}?{params}",
            }
        )

    return specs


def select_specs(
    specs: list[dict[str, str]],
    *,
    offset: int,
    limit: int,
    all_stage_a: bool,
) -> list[dict[str, str]]:
    if offset < 0:
        raise ValueError("offset must be >= 0")
    if limit < 1:
        raise ValueError("limit must be >= 1")
    if all_stage_a:
        return specs
    return specs[offset : offset + limit]


def estimate_credits(data: dict[str, Any], request_count: int) -> int:
    assumption = data.get("historical_credit_assumption")
    if not isinstance(assumption, dict):
        raise ValueError("Manifest is missing historical_credit_assumption")
    credits_per_request = assumption.get("credits_per_request")
    if not isinstance(credits_per_request, int) or credits_per_request < 1:
        raise ValueError("historical_credit_assumption.credits_per_request must be >= 1")
    return credits_per_request * request_count


def _print_plan(
    selected: list[dict[str, str]],
    total: int,
    estimated_credits: int,
) -> None:
    print(f"Stage A available probes: {total}")
    print(f"Selected probes: {len(selected)}")
    print(f"Estimated credits under current manifest assumption: {estimated_credits}")
    print("Credit assumption MUST be rechecked against provider docs before paid execution.")
    for index, spec in enumerate(selected, start=1):
        print(
            f"{index:02d}. {spec['group_id']} {spec['cutoff']} {spec['requested_snapshot_at_utc']}"
        )
        print(f"    {spec['url']}")
    print("No API request was sent.")


def _validate_execution_ack(
    *,
    execute: bool,
    ack_paid_provider_access: bool,
    all_stage_a: bool,
    confirm_request_count: int | None,
    selected_count: int,
    estimated_credits: int,
    max_credits: int | None,
) -> None:
    if not execute:
        return
    if not ack_paid_provider_access:
        raise ValueError("--execute requires --ack-paid-provider-access")
    if all_stage_a and confirm_request_count != selected_count:
        raise ValueError(
            f"Full Stage A execution requires --confirm-request-count {selected_count}"
        )
    if max_credits is None:
        raise ValueError("--execute requires --max-credits")
    if max_credits < 1:
        raise ValueError("--max-credits must be >= 1")
    if estimated_credits > max_credits:
        raise ValueError(
            f"Estimated Stage A cost {estimated_credits} credits exceeds "
            f"--max-credits {max_credits}"
        )
    if not os.environ.get(KEY_ENV):
        raise ValueError(f"Missing required environment variable: {KEY_ENV}")


def _execute(selected: list[dict[str, str]]) -> int:
    for index, spec in enumerate(selected, start=1):
        print(f"Executing {index}/{len(selected)}: {spec['group_id']} {spec['cutoff']}")
        command = [
            sys.executable,
            str(HARNESS),
            "--research-only",
            "--provider",
            "the-odds-api",
            "--probe-name",
            spec["probe_name"],
            "--url",
            spec["url"],
            "--query-env",
            f"apiKey={KEY_ENV}",
        ]
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            print(
                f"Stopping after failed probe {spec['probe_name']} (exit={result.returncode}).",
                file=sys.stderr,
            )
            return result.returncode
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually send selected historical API requests. Default is dry-run.",
    )
    parser.add_argument(
        "--ack-paid-provider-access",
        action="store_true",
        help="Acknowledge that selected historical requests may consume paid quota.",
    )
    parser.add_argument(
        "--all-stage-a",
        action="store_true",
        help="Select the complete 69-request Stage A plan.",
    )
    parser.add_argument(
        "--confirm-request-count",
        type=int,
        default=None,
        help="Required for full Stage A execution; must equal the selected count.",
    )
    parser.add_argument(
        "--max-credits",
        type=int,
        default=None,
        help="Hard execution cap. Required with --execute and checked against manifest estimate.",
    )
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument(
        "--limit",
        type=int,
        default=1,
        help="Number of requests selected when --all-stage-a is not used.",
    )
    args = parser.parse_args()

    try:
        data = load_manifest()
        specs = build_probe_specs(data)
        selected = select_specs(
            specs,
            offset=args.offset,
            limit=args.limit,
            all_stage_a=args.all_stage_a,
        )
        if not selected:
            raise ValueError("Selection is empty; check --offset/--limit")
        estimated_credits = estimate_credits(data, len(selected))
        _validate_execution_ack(
            execute=args.execute,
            ack_paid_provider_access=args.ack_paid_provider_access,
            all_stage_a=args.all_stage_a,
            confirm_request_count=args.confirm_request_count,
            selected_count=len(selected),
            estimated_credits=estimated_credits,
            max_credits=args.max_credits,
        )
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Stage A configuration error: {exc}", file=sys.stderr)
        return 2

    if not args.execute:
        _print_plan(selected, len(specs), estimated_credits)
        return 0

    return _execute(selected)


if __name__ == "__main__":
    sys.exit(main())
