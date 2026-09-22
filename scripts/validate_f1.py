"""Mechanical F1 repository-foundation validator.

This validates permanent repository-skeleton invariants only.
Current phase authorization is enforced separately by validate_phase_gates.py.
Neither script is an independent critical review.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "pyproject.toml",
    "uv.lock",
    ".env.example",
    "compose.yaml",
    "alembic.ini",
    "migrations/env.py",
    ".github/workflows/ci.yml",
    ".github/workflows/security.yml",
    ".project/FOUNDATION_DECISIONS_v0.1.yaml",
    ".project/OPEN_DECISIONS.yaml",
    ".project/SPORT_PREDICTABILITY_POLICY.yaml",
    ".project/PHASE_GATES.toml",
    "src/sports_quant/config/settings.py",
    "src/sports_quant/db/engine.py",
    "src/sports_quant/observability/logging.py",
]


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        print("Missing F1 required paths:")
        for path in missing:
            print(f"  - {path}")
        return 1

    print("F1 repository-foundation validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
