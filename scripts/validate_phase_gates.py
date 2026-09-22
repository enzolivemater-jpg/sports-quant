"""Machine-checkable SPORTS QUANT phase gate.

This script enforces the current governance boundary between F1 and F2.
It does not replace an independent critical review.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATE_FILE = ROOT / ".project" / "PHASE_GATES.toml"
REVIEW_DIR = ROOT / ".project" / "reviews"

PASS_REVIEW_STATES = {"PASS", "PASS_WITH_P2"}
ALLOWED_REVIEW_STATES = PASS_REVIEW_STATES | {"PENDING", "BLOCKED", "NEEDS_DECISION"}
REVIEW_FINAL_STATUSES = {"GO", "GO_WITH_CONDITIONS"}
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


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


def _extract_value(text: str, label: str) -> str | None:
    prefix = f"{label}:"
    for line in text.splitlines():
        if line.strip().startswith(prefix):
            return line.split(":", 1)[1].strip()
    return None


def _extract_final_status(text: str) -> str | None:
    marker = "## Final status"
    if marker not in text:
        return None
    tail = text.split(marker, 1)[1]
    for line in tail.splitlines():
        candidate = line.strip().lstrip("-").strip()
        if candidate in {"GO", "GO_WITH_CONDITIONS", "NO_GO", "NEEDS_DECISION"}:
            return candidate
    return None


def _validate_review_artifact(artifact: str) -> list[str]:
    errors: list[str] = []

    artifact_path = (ROOT / artifact).resolve()
    review_dir = REVIEW_DIR.resolve()

    try:
        artifact_path.relative_to(review_dir)
    except ValueError:
        errors.append("F0 review artifact must live under .project/reviews/")
        return errors

    if artifact_path.name == "F0_REVIEW_RECORD_TEMPLATE.md":
        errors.append("F0 review artifact cannot be the review template")
        return errors

    if not artifact_path.is_file():
        errors.append(f"Recorded F0 review artifact does not exist: {artifact}")
        return errors

    text = artifact_path.read_text(encoding="utf-8")

    reviewed_head = _extract_value(text, "Reviewed HEAD")
    if reviewed_head is None or not FULL_SHA_RE.fullmatch(reviewed_head):
        errors.append("F0 review artifact requires a full 40-character Reviewed HEAD SHA")

    p0 = _extract_value(text, "P0 open")
    p1 = _extract_value(text, "P1 open")
    cleared = _extract_value(text, "Blocking findings cleared")

    if p0 != "0":
        errors.append("F0 review artifact must record P0 open: 0")
    if p1 != "0":
        errors.append("F0 review artifact must record P1 open: 0")
    if cleared is None or cleared.lower() != "true":
        errors.append("F0 review artifact must record Blocking findings cleared: true")

    final_status = _extract_final_status(text)
    if final_status not in REVIEW_FINAL_STATUSES:
        errors.append(
            "F0 review artifact final status must be GO or GO_WITH_CONDITIONS "
            "before F2 authorization"
        )

    if "F2 MAY BEGIN. No unresolved P0/P1 remains." not in text:
        errors.append("F0 review artifact must explicitly authorize F2 to begin")

    placeholder_markers = (
        "<full commit SHA>",
        "<integer>",
        "<free text>",
        "YYYY-MM-DD",
        "YES / NO",
        "PASS / FAIL",
    )
    unresolved = [marker for marker in placeholder_markers if marker in text]
    if unresolved:
        errors.append(
            "F0 review artifact still contains template placeholders: "
            + ", ".join(repr(marker) for marker in unresolved)
        )

    return errors


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
        if status in PASS_REVIEW_STATES:
            print(
                "Inconsistent gate: F0 review is marked as passed but F2 remains unauthorized. "
                "Complete the review-recording/authorization procedure."
            )
            return 1

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

    artifact_errors = _validate_review_artifact(artifact)
    if artifact_errors:
        for error in artifact_errors:
            print(f"F0 review artifact error: {error}")
        return 1

    if review.get("p0_open") != 0 or review.get("p1_open") != 0:
        print("F2 authorization requires p0_open=0 and p1_open=0")
        return 1

    if review.get("blocking_findings_cleared") is not True:
        print("F2 authorization requires blocking_findings_cleared=true")
        return 1

    basis = f2.get("authorization_basis")
    if not isinstance(basis, str) or not basis.strip():
        print("F2 authorization requires a non-empty authorization_basis")
        return 1
    if basis == "PENDING_INDEPENDENT_F0_REVIEW":
        print("F2 authorization_basis still indicates a pending review")
        return 1

    print(
        "Phase gate: PASS "
        f"(F2 authorized by independent review artifact {artifact!r}; reviewer={reviewer!r})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
