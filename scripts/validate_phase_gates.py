"""Machine-checkable SPORTS QUANT phase gate.

This script enforces the current governance boundary between F1 and F2.
It does not replace an independent critical review.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GATE_FILE = ROOT / ".project" / "PHASE_GATES.toml"
REVIEW_DIR = ROOT / ".project" / "reviews"
F1_SOURCE_ALLOWLIST_FILE = ROOT / ".project" / "F1_SOURCE_ALLOWLIST.toml"
SOURCE_ROOT = ROOT / "src" / "sports_quant"

PASS_REVIEW_STATES = {"PASS", "PASS_WITH_P2"}
ALLOWED_REVIEW_STATES = PASS_REVIEW_STATES | {"PENDING", "BLOCKED", "NEEDS_DECISION"}
REVIEW_FINAL_STATUSES = {"GO", "GO_WITH_CONDITIONS"}
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

REVIEW_PROTECTED_PATHS = (
    ".project/FOUNDATION_DECISIONS_v0.1.yaml",
    ".project/OPEN_DECISIONS.yaml",
    ".project/SPORT_PREDICTABILITY_POLICY.yaml",
    ".project/PROJECT_PROFILE.yaml",
    ".project/F1_SOURCE_ALLOWLIST.toml",
    "docs/adr/ADR-0001-foundation-v0.1.md",
    "docs/adr/ADR-0002-mandatory-sports-scope.md",
    "docs/adr/ADR-0003-additional-sports-allowlist.md",
    "docs/adr/ADR-0004-football-first-pilot.md",
    ".ai/AI_CHARTER.md",
    ".ai/AI_DECISIONS.md",
    ".ai/handoffs/F0_INDEPENDENT_REVIEW.md",
    "scripts/validate_phase_gates.py",
    "docs/runbooks/GOVERNANCE_DEVIATION_F1_BEFORE_F0_REVIEW.md",
    ".github/workflows/ci.yml",
)


def _load_gates() -> dict[str, Any]:
    if not GATE_FILE.exists():
        raise RuntimeError(f"Missing phase gate file: {GATE_FILE.relative_to(ROOT)}")
    with GATE_FILE.open("rb") as handle:
        return tomllib.load(handle)


def _load_f1_source_allowlist() -> tuple[set[str], str]:
    if not F1_SOURCE_ALLOWLIST_FILE.exists():
        raise RuntimeError(
            f"Missing F1 source allowlist: {F1_SOURCE_ALLOWLIST_FILE.relative_to(ROOT)}"
        )

    with F1_SOURCE_ALLOWLIST_FILE.open("rb") as handle:
        data = tomllib.load(handle)

    raw_allowed = data.get("allowed_source_files")
    if not isinstance(raw_allowed, list) or not raw_allowed:
        raise RuntimeError("F1 source allowlist must contain allowed_source_files")

    allowed: set[str] = set()
    for item in raw_allowed:
        if not isinstance(item, str) or not item.strip():
            raise RuntimeError("F1 source allowlist entries must be non-empty strings")
        path = Path(item)
        if path.is_absolute() or ".." in path.parts:
            raise RuntimeError(f"Unsafe F1 source allowlist entry: {item!r}")
        normalized = path.as_posix()
        if not normalized.startswith("src/sports_quant/"):
            raise RuntimeError(
                f"F1 source allowlist entries must live under src/sports_quant/: {item!r}"
            )
        allowed.add(normalized)

    scaffold = data.get("scaffold", {})
    allowed_filename = scaffold.get("allowed_filename")
    if not isinstance(allowed_filename, str) or not allowed_filename.strip():
        raise RuntimeError("F1 source allowlist requires scaffold.allowed_filename")

    return allowed, allowed_filename


def _unauthorized_pre_f2_source_files() -> list[Path]:
    allowed, scaffold_filename = _load_f1_source_allowlist()
    if not SOURCE_ROOT.exists():
        return []

    unauthorized: list[Path] = []
    for path in SOURCE_ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if path.name == scaffold_filename:
            continue
        if relative not in allowed:
            unauthorized.append(path)

    return sorted(unauthorized)


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


def _git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _validate_reviewed_head_scope(reviewed_head: str) -> list[str]:
    if not (ROOT / ".git").exists():
        return []

    errors: list[str] = []

    exists = _git(["cat-file", "-e", f"{reviewed_head}^{{commit}}"])
    if exists.returncode != 0:
        return [f"Reviewed HEAD is not available in this Git checkout: {reviewed_head}"]

    ancestor = _git(["merge-base", "--is-ancestor", reviewed_head, "HEAD"])
    if ancestor.returncode != 0:
        return [f"Reviewed HEAD is not an ancestor of current HEAD: {reviewed_head}"]

    diff = _git(
        [
            "diff",
            "--name-only",
            f"{reviewed_head}..HEAD",
            "--",
            *REVIEW_PROTECTED_PATHS,
        ]
    )
    if diff.returncode != 0:
        errors.append("Unable to compare reviewed HEAD with current protected F0 files")
        return errors

    changed = [line.strip() for line in diff.stdout.splitlines() if line.strip()]
    if changed:
        errors.append(
            "Protected F0 files changed after the independent review; re-review is required: "
            + ", ".join(changed)
        )

    return errors


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
    else:
        errors.extend(_validate_reviewed_head_scope(reviewed_head))

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

    if not authorized:
        if status in PASS_REVIEW_STATES:
            print(
                "Inconsistent gate: F0 review is marked as passed but F2 remains unauthorized. "
                "Complete the review-recording/authorization procedure."
            )
            return 1

        try:
            unauthorized = _unauthorized_pre_f2_source_files()
        except (OSError, RuntimeError, tomllib.TOMLDecodeError) as exc:
            print(f"Pre-F2 source containment configuration error: {exc}")
            return 1

        if unauthorized:
            print("Unauthorized source implementation exists while the F2 gate is closed:")
            for path in unauthorized:
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
