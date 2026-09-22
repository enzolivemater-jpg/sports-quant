#!/usr/bin/env python3
"""Plan or execute free/trial Football provider research probes safely."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data" / "manifests" / "football_provider_probe_plan_v0.1.json"
HARNESS = ROOT / "scripts" / "research" / "capture_provider_json.py"


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def build_probe_specs(data: dict[str, Any]) -> list[dict[str, str]]:
    specs: list[dict[str, str]] = []
    providers = data.get("providers")
    if not isinstance(providers, list):
        raise ValueError("Manifest must contain providers[]")

    for provider in providers:
        if not isinstance(provider, dict):
            raise ValueError("Each provider entry must be an object")
        provider_name = provider.get("provider")
        auth = provider.get("auth")
        probes = provider.get("probes")
        if not isinstance(provider_name, str) or not provider_name:
            raise ValueError("Provider name must be a non-empty string")
        if not isinstance(auth, dict):
            raise ValueError(f"{provider_name}: auth must be an object")
        if auth.get("type") != "header_env":
            raise ValueError(f"{provider_name}: only header_env auth is allowed in this runner")
        header = auth.get("name")
        env_name = auth.get("env")
        if not isinstance(header, str) or not header:
            raise ValueError(f"{provider_name}: invalid auth header")
        if not isinstance(env_name, str) or not env_name:
            raise ValueError(f"{provider_name}: invalid auth env var")
        if not isinstance(probes, list) or not probes:
            raise ValueError(f"{provider_name}: probes must be non-empty")

        for probe in probes:
            if not isinstance(probe, dict):
                raise ValueError(f"{provider_name}: probe must be an object")
            probe_name = probe.get("probe_name")
            url = probe.get("url")
            purpose = probe.get("purpose")
            if not all(isinstance(value, str) and value for value in (probe_name, url, purpose)):
                raise ValueError(f"{provider_name}: malformed probe entry")
            specs.append(
                {
                    "provider": provider_name,
                    "probe_name": probe_name,
                    "url": url,
                    "purpose": purpose,
                    "auth_header": header,
                    "auth_env": env_name,
                }
            )
    return specs


def select_specs(
    specs: list[dict[str, str]],
    *,
    providers: set[str],
    offset: int,
    limit: int,
    all_selected: bool,
) -> list[dict[str, str]]:
    if offset < 0:
        raise ValueError("offset must be >= 0")
    if limit < 1:
        raise ValueError("limit must be >= 1")

    filtered = [spec for spec in specs if not providers or spec["provider"] in providers]
    if all_selected:
        return filtered
    return filtered[offset : offset + limit]


def _print_plan(selected: list[dict[str, str]], total: int) -> None:
    print(f"Available free/trial probes: {total}")
    print(f"Selected probes: {len(selected)}")
    for index, spec in enumerate(selected, start=1):
        print(f"{index:02d}. {spec['provider']} / {spec['probe_name']}")
        print(f"    purpose: {spec['purpose']}")
        print(f"    url: {spec['url']}")
        print(f"    auth env: {spec['auth_env']} -> header {spec['auth_header']}")
    print("No provider request was sent.")


def _validate_execution(selected: list[dict[str, str]], ack_trial_quota: bool) -> None:
    if not ack_trial_quota:
        raise ValueError("--execute requires --ack-trial-quota")

    missing_env = sorted(
        {spec["auth_env"] for spec in selected if not os.environ.get(spec["auth_env"])}
    )
    if missing_env:
        raise ValueError("Missing required environment variable(s): " + ", ".join(missing_env))


def _execute(selected: list[dict[str, str]]) -> int:
    for index, spec in enumerate(selected, start=1):
        print(f"Executing {index}/{len(selected)}: {spec['provider']} / {spec['probe_name']}")
        command = [
            sys.executable,
            str(HARNESS),
            "--research-only",
            "--provider",
            spec["provider"],
            "--probe-name",
            spec["probe_name"],
            "--url",
            spec["url"],
            "--header-env",
            f"{spec['auth_header']}={spec['auth_env']}",
        ]
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            print(
                f"Stopping after failed probe {spec['provider']}/{spec['probe_name']} "
                f"(exit={result.returncode}).",
                file=sys.stderr,
            )
            return result.returncode
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provider",
        action="append",
        default=[],
        help="Restrict to one provider. May be repeated.",
    )
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument(
        "--all-selected",
        action="store_true",
        help="Select all probes after provider filtering.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually send the selected free/trial requests. Default is dry-run.",
    )
    parser.add_argument(
        "--ack-trial-quota",
        action="store_true",
        help="Acknowledge that execution may consume provider trial/free quota.",
    )
    args = parser.parse_args()

    try:
        data = load_manifest()
        specs = build_probe_specs(data)
        selected = select_specs(
            specs,
            providers=set(args.provider),
            offset=args.offset,
            limit=args.limit,
            all_selected=args.all_selected,
        )
        if not selected:
            raise ValueError("Selection is empty; check provider/offset/limit")
        unknown = sorted(set(args.provider) - {spec["provider"] for spec in specs})
        if unknown:
            raise ValueError("Unknown provider(s): " + ", ".join(unknown))
        if args.execute:
            _validate_execution(selected, args.ack_trial_quota)
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Provider probe configuration error: {exc}", file=sys.stderr)
        return 2

    if not args.execute:
        _print_plan(selected, len(specs))
        return 0

    return _execute(selected)


if __name__ == "__main__":
    sys.exit(main())
