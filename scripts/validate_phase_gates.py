"""Machine-checkable SPORTS QUANT phase gate.

This script enforces the current governance boundary between F1 and F2.
It does not replace an independent critical review.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATE_FILE = ROOT / ".project" / "PHASE_GATES.toml"

PASS_REVIEW_STATES = {"PASS", "PASS_WITH_P2"}
ALLOWED_REVIEW_STATES = PASS_REVIEW_STATES | {"PENDING", "BLOCKED", "NEEDS_DECISION"}


def _load_gates() -> dict[str, Any]:
    if not GATE_FILE.exists():
        raise RuntimeError(f"Missing phase gate file: {GATE_FILE.relative_to(ROOT)}")
    with GATE_FILE.open("rb") as handle:
        return tomllib.load(handle)


def _f2_implementation_files() -> list[Path]:
    contracts = ROOT / "src" / "sports_quant" / "contracts"
    if not contracts.exists():
        return []

    allowed_scaffold_names = {"README.md", "__init__.py"}
    return sorted(
        path
        for path in contracts.rglob("*")
        if path.is_file() and path.name not in allowed_scaffold_names
    )


def main() -> int:
    try:
        gates = _load_gates()
    except (OSError, RuntimeError, tomllib.TOMLDecodeError) as exc:
        print(f"Phase-gate configuration error: {exc}")
        return 1

    review = gates.get("foundation_review", {})
    f2 = gates.get("f2", {})

    status = review.get("status")
    if status not in ALLOWED_REVIEW_STATES:
        print(f"Invalid foundation review status: {status!r}")
        return 1

    authorized = f2.get("authorized")
    if not isinstance(authorized, bool):
        print("f2.authorized must be a boolean")
        return 1

    f2_files = _f2_implementation_files()

    if not authorized:
        if f2_files:
            print("F2 implementation exists while the F2 gate is closed:")
            for path in f2_files:
                print(f"  - {path.relative_to(ROOT)}")
            return 1

        print(f"Phase gate: PASS (F2 closed; F0 review status={status})")
        return 0

    if status not in PASS_REVIEW_STATES:
        print(f"F2 cannot be authorized while F0 review status is {status!r}")
        return 1

    reviewer = review.get("independent_reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        print("F2 authorization requires foundation_review.independent_reviewer")
        return 1

    artifact = review.get("review_artifact")
    if not isinstance(artifact, str) or not artifact.strip():
        print("F2 authorization requires foundation_review.review_artifact")
        return 1

    artifact_path = ROOT / artifact
    if not artifact_path.is_file():
        print(f"Recorded F0 review artifact does not exist: {artifact}")
        return 1

    if review.get("p0_open") != 0 or review.get("p1_open") != 0:
        print("F2 authorization requires p0_open=0 and p1_open=0")
        return 1

    if review.get("blocking_findings_cleared") is not True:
        print("F2 authorization requires blocking_findings_cleared=true")
        return 1

    print(
        "Phase gate: PASS "
        f"(F2 authorized by independent review artifact {artifact!r}; reviewer={reviewer!r})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
