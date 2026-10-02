#!/usr/bin/env python3
"""Rebuild the canonical Football dataset from a raw store and print its manifest.

Deterministic: the same store, code version and cutoffs always print the same
``content_hash`` (run identity and wall-clock times are outside the hash).
The store is only read.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

from sports_quant.contracts.common import ContractError, require_aware_datetime
from sports_quant.contracts.reproducibility import ArtifactKind, ArtifactRef, CodeVersion
from sports_quant.data.entity_resolution.football_epl import epl_2024_25_table
from sports_quant.data.ingestion.dataset import build_manifest, materialize_football
from sports_quant.data.ingestion.football import CaptureMode, IngestionContext, build_football
from sports_quant.data.snapshots.store import RawSnapshotStore

TIMEZONE = "Europe/London"


def _head_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--cutoff", action="append", default=[], help="ISO-8601 with offset")
    parser.add_argument("--code-version", help="full commit SHA (default: git HEAD)")
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    started = datetime.now(UTC)
    try:
        cutoffs = [require_aware_datetime(datetime.fromisoformat(c), "cutoff") for c in args.cutoff]
        code_version = CodeVersion(commit=args.code_version or _head_commit())
        store = RawSnapshotStore(args.store)
        captures = store.load()
        mappings = epl_2024_25_table()
        build = build_football(
            captures,
            IngestionContext(
                mappings=mappings,
                capture_mode=CaptureMode.RETROSPECTIVE_ARCHIVE,
                openfootball_timezone=TIMEZONE,
            ),
        )
        dataset_ref = ArtifactRef(
            kind=ArtifactKind.SNAPSHOT,
            identifier="football-raw-store",
            version=args.dataset_version,
        )
        datasets = [
            materialize_football(
                build,
                decision_cutoff_at=cutoff,
                code_version=code_version,
                dataset_ref=dataset_ref,
                created_at=started,
            )
            for cutoff in cutoffs
        ]
        manifest = build_manifest(
            build,
            raw_captures=(raw for raw, _payload in captures),
            mappings=mappings,
            capture_mode=CaptureMode.RETROSPECTIVE_ARCHIVE,
            openfootball_timezone=TIMEZONE,
            code_version=code_version,
            datasets=datasets,
            extraction_run_id=str(uuid.uuid4()),
            extraction_started_at=started,
            extraction_completed_at=datetime.now(UTC),
        )
    except (ContractError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(manifest.to_json(), encoding="ascii")
    body = manifest.body
    print(f"content_hash {manifest.content_hash}")
    print(f"captures {len(body.raw_captures)}")
    for count in body.record_counts:
        print(f"records {count.name} {count.count}")
    for count in body.issue_counts:
        print(f"issues {count.name} {count.count}")
    print(f"gaps {body.gap_count} conflicts {body.conflict_count}")
    for evidence in body.pit_evidence:
        print(
            f"pit {evidence.decision_cutoff_at.isoformat()} {evidence.manifest_content_hash} "
            f"selected={evidence.selected_keys} unresolved={evidence.unresolved_keys} "
            f"no_eligible={evidence.no_eligible_keys}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
