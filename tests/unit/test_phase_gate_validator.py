from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_phase_gates.py"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_phase_gates", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_gate(
    root: Path,
    *,
    status: str = "PENDING",
    authorized: bool = False,
    reviewer: str = "",
    artifact: str = "",
    p0: int = 0,
    p1: int = 0,
    cleared: bool = False,
    basis: str = "PENDING_INDEPENDENT_F0_REVIEW",
) -> None:
    project = root / ".project"
    project.mkdir(parents=True, exist_ok=True)
    (project / "PHASE_GATES.toml").write_text(
        f"""schema_version = "1.0"
project = "SPORTS_QUANT"
current_phase = "F1_REPOSITORY_SKELETON"

[foundation_review]
status = "{status}"
independent_reviewer = "{reviewer}"
review_artifact = "{artifact}"
p0_open = {p0}
p1_open = {p1}
blocking_findings_cleared = {str(cleared).lower()}
issue = 1

[f2]
authorized = {str(authorized).lower()}
authorization_basis = "{basis}"
implementation_issue = 2
spec = "docs/contracts/F2_READY_TO_IMPLEMENT_SPEC.md"
""",
        encoding="utf-8",
    )


def _configure_module(module: ModuleType, root: Path) -> None:
    module.ROOT = root
    module.GATE_FILE = root / ".project" / "PHASE_GATES.toml"
    module.REVIEW_DIR = root / ".project" / "reviews"


def _valid_review_text() -> str:
    return """# F0 Independent Review Record

Review date: 2026-09-22
Reviewer/context: separate-gpt-codex-review
Reviewed repository: enzolivemater-jpg/sports-quant
Reviewed HEAD: 0123456789abcdef0123456789abcdef01234567
Review type: INDEPENDENT_CRITICAL_REVIEW

## P0 findings
- None

## P1 findings
- None

## P2 findings
- None

## Blocking findings state

P0 open: 0
P1 open: 0
Blocking findings cleared: true

## Final status

GO

## F2 authorization statement

F2 MAY BEGIN. No unresolved P0/P1 remains.
"""


def test_closed_pending_gate_passes_without_f2_files(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)

    assert module.main() == 0


def test_closed_gate_rejects_f2_implementation_files(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    contracts = tmp_path / "src" / "sports_quant" / "contracts"
    contracts.mkdir(parents=True)
    (contracts / "probability.py").write_text("P_SAFE = None\n", encoding="utf-8")

    assert module.main() == 1


def test_pass_review_cannot_leave_f2_half_closed(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path, status="PASS", authorized=False)

    assert module.main() == 1


def test_authorized_gate_requires_review_under_project_reviews(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    rogue = tmp_path / "review.md"
    rogue.write_text(_valid_review_text(), encoding="utf-8")
    _write_gate(
        tmp_path,
        status="PASS",
        authorized=True,
        reviewer="separate-reviewer",
        artifact="review.md",
        cleared=True,
        basis="F0 independent review",
    )

    assert module.main() == 1


def test_authorized_gate_rejects_template_as_review(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    reviews = tmp_path / ".project" / "reviews"
    reviews.mkdir(parents=True, exist_ok=True)
    template = reviews / "F0_REVIEW_RECORD_TEMPLATE.md"
    template.write_text(_valid_review_text(), encoding="utf-8")
    _write_gate(
        tmp_path,
        status="PASS",
        authorized=True,
        reviewer="separate-reviewer",
        artifact=".project/reviews/F0_REVIEW_RECORD_TEMPLATE.md",
        cleared=True,
        basis="F0 independent review",
    )

    assert module.main() == 1


def test_authorized_gate_rejects_unresolved_template_placeholders(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    reviews = tmp_path / ".project" / "reviews"
    reviews.mkdir(parents=True, exist_ok=True)
    review = reviews / "F0_INDEPENDENT_REVIEW_2026-09-22.md"
    review.write_text(_valid_review_text() + "\nReviewer notes: <free text>\n", encoding="utf-8")
    _write_gate(
        tmp_path,
        status="PASS",
        authorized=True,
        reviewer="separate-reviewer",
        artifact=".project/reviews/F0_INDEPENDENT_REVIEW_2026-09-22.md",
        cleared=True,
        basis="F0 independent review",
    )

    assert module.main() == 1


def test_fully_supported_authorized_gate_passes(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    reviews = tmp_path / ".project" / "reviews"
    reviews.mkdir(parents=True, exist_ok=True)
    review = reviews / "F0_INDEPENDENT_REVIEW_2026-09-22.md"
    review.write_text(_valid_review_text(), encoding="utf-8")
    _write_gate(
        tmp_path,
        status="PASS",
        authorized=True,
        reviewer="separate-reviewer",
        artifact=".project/reviews/F0_INDEPENDENT_REVIEW_2026-09-22.md",
        cleared=True,
        basis="F0 independent review 2026-09-22",
    )

    assert module.main() == 0
