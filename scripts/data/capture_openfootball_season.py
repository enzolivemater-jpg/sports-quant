#!/usr/bin/env python3
"""Capture a local copy of a pinned OpenFootball season file into a raw store.

No network access: obtain the file yourself, e.g. by its pinned blob id::

    gh api repos/openfootball/england/git/blobs/<blob_sha> --jq .content | base64 -d

The file's Git blob id must equal the entry pinned in
``data/manifests/football_openfootball_epl_2000_2025_verified.json``. ``received_at``
is the current system time: the moment SPORTS QUANT received the content, which is
the only ``known_at`` basis F4 assigns (``SYSTEM_RECEIPT``).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from sports_quant.contracts.common import ContractError
from sports_quant.data.ingestion.football import git_blob_sha, openfootball_capture
from sports_quant.data.snapshots.store import RawSnapshotStore

ROOT = Path(__file__).resolve().parents[2]
PINNED = ROOT / "data" / "manifests" / "football_openfootball_epl_2000_2025_verified.json"


def pinned_blob_sha(season_path: str, manifest: Path = PINNED) -> str:
    seasons = json.loads(manifest.read_text(encoding="utf-8"))["seasons"]
    matches = [entry["blob_sha"] for entry in seasons if entry["path"] == season_path]
    if len(matches) != 1:
        raise ValueError(f"{season_path!r} is not pinned in {manifest.name}")
    return str(matches[0])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--season-path", required=True, help="e.g. 2024-25/1-premierleague.txt")
    parser.add_argument("--store", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = args.input.read_bytes()
    try:
        expected = pinned_blob_sha(args.season_path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    actual = git_blob_sha(payload)
    if actual != expected:
        print(f"Blob {actual} differs from pinned {expected}", file=sys.stderr)
        return 1
    raw = openfootball_capture(payload, season_path=args.season_path, received_at=datetime.now(UTC))
    try:
        RawSnapshotStore(args.store).put(raw, payload)
    except ContractError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Captured {args.season_path} blob {actual} as {raw.capture_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
