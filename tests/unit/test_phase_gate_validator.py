from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_phase_gates.py"

TEST_F1_FILES = {
    "src/sports_quant/config/settings.py": "SETTING = 1\n",
    "src/sports_quant/db/engine.py": "ENGINE = 1\n",
}


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_phase_gates", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_allowlist(
    root: Path,
    allowed: tuple[str, ...],
    scaffold_filename: str = "README.md",
) -> None:
    project = root / ".project"
    project.mkdir(parents=True, exist_ok=True)
    lines = [
        'schema_version = "1.1"',
        'project = "SPORTS_QUANT"',
        'purpose = "test allowlist"',
        "",
        "allowed_source_files = [",
    ]
    lines.extend(f'  "{path}",' for path in allowed)
    lines.extend(
        [
            "]",
            "",
            "[scaffold]",
            f'allowed_filename = "{scaffold_filename}"',
            "",
        ]
    )
    (project / "F1_SOURCE_ALLOWLIST.toml").write_text("\n".join(lines), encoding="utf-8")


def _write_pyproject(
    root: Path,
    *,
    where: str = '["src"]',
    include: str = '["sports_quant*"]',
) -> None:
    (root / "pyproject.toml").write_text(
        f"""[tool.setuptools.packages.find]
where = {where}
include = {include}
""",
        encoding="utf-8",
    )


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


def _write_source(root: Path, relative: str, content: str = "VALUE = 1\n") -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _configure_module(module: ModuleType, root: Path) -> None:
    module.ROOT = root
    module.GATE_FILE = root / ".project" / "PHASE_GATES.toml"
    module.REVIEW_DIR = root / ".project" / "reviews"
    module.F1_SOURCE_ALLOWLIST_FILE = root / ".project" / "F1_SOURCE_ALLOWLIST.toml"
    module.PYPROJECT_FILE = root / "pyproject.toml"
    module.SOURCE_ROOT = root / "src"

    for path, content in TEST_F1_FILES.items():
        _write_source(root, path, content)

    module.CANONICAL_F1_SOURCE_BLOBS = {
        path: module._git_blob_sha(root / path) for path in TEST_F1_FILES
    }

    _write_allowlist(root, tuple(TEST_F1_FILES))
    _write_pyproject(root)


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


def test_closed_pending_gate_passes_with_frozen_f1_sources_and_readme(
    tmp_path: Path,
) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    _write_source(tmp_path, "src/sports_quant/modeling/football/README.md", "# scaffold\n")

    assert module.main() == 0


def test_closed_gate_rejects_allowlist_extension(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    extra = "src/sports_quant/modeling/football/model.py"
    _write_allowlist(tmp_path, (*TEST_F1_FILES, extra))
    _write_source(tmp_path, extra)

    assert module.main() == 1


def test_closed_gate_rejects_scaffold_filename_change(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    _write_allowlist(tmp_path, tuple(TEST_F1_FILES), scaffold_filename="model.py")

    assert module.main() == 1


def test_closed_gate_rejects_changed_content_in_allowlisted_f1_file(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    _write_source(
        tmp_path,
        "src/sports_quant/config/settings.py",
        "def p_safe_override() -> float:\n    return 0.99\n",
    )

    assert module.main() == 1


def test_closed_gate_rejects_f2_contract_implementation(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    _write_source(tmp_path, "src/sports_quant/contracts/probability.py", "P_SAFE = None\n")

    assert module.main() == 1


def test_closed_gate_rejects_football_business_logic_outside_contracts(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    _write_source(tmp_path, "src/sports_quant/modeling/football/model.py")

    assert module.main() == 1


def test_closed_gate_rejects_calibration_business_logic_outside_contracts(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    _write_source(tmp_path, "src/sports_quant/calibration/platt.py")

    assert module.main() == 1


def test_closed_gate_rejects_market_business_logic_outside_contracts(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    _write_source(tmp_path, "src/sports_quant/market/no_vig/proportional.py")

    assert module.main() == 1


def test_closed_gate_rejects_probability_business_logic_outside_contracts(
    tmp_path: Path,
) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    _write_source(tmp_path, "src/sports_quant/probability/model.py")

    assert module.main() == 1


def test_closed_gate_rejects_second_package_under_src(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    _write_source(tmp_path, "src/sports_quant_f2/__init__.py")

    assert module.main() == 1


def test_closed_gate_rejects_packaging_scope_broadening(tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    _write_gate(tmp_path)
    _write_pyproject(tmp_path, include='["*"]')

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
    review.write_text(
        _valid_review_text() + "\nReviewer notes: <free text>\n",
        encoding="utf-8",
    )
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


def test_reviewed_head_scope_rejects_protected_file_drift(monkeypatch, tmp_path: Path) -> None:
    module = _load_module()
    _configure_module(module, tmp_path)
    (tmp_path / ".git").mkdir()

    responses = iter(
        [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
            subprocess.CompletedProcess(
                args=[],
                returncode=0,
                stdout=".project/OPEN_DECISIONS.yaml\n",
                stderr="",
            ),
        ]
    )
    monkeypatch.setattr(module, "_git", lambda _args: next(responses))

    errors = module._validate_reviewed_head_scope("0123456789abcdef0123456789abcdef01234567")

    assert errors
    assert "re-review is required" in errors[0]
    assert ".project/OPEN_DECISIONS.yaml" in errors[0]
