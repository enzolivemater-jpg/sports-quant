"""Mechanical F1 repository-scope validator.

This validates repository skeleton invariants only; it is not a critical independent review.
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
    "src/sports_quant/config/settings.py",
    "src/sports_quant/db/engine.py",
    "src/sports_quant/observability/logging.py",
]

FORBIDDEN_F1_IMPLEMENTATIONS = [
    "src/sports_quant/contracts/common.py",
    "src/sports_quant/contracts/time.py",
    "src/sports_quant/contracts/prediction.py",
    "src/sports_quant/data/point_in_time/kernel.py",
    "src/sports_quant/modeling/basketball/model.py",
    "src/sports_quant/modeling/football/model.py",
    "src/sports_quant/modeling/handball/model.py",
    "src/sports_quant/modeling/mma/model.py",
    "src/sports_quant/modeling/tennis/model.py",
    "src/sports_quant/modeling/volleyball/model.py",
    "src/sports_quant/optimizer/optimizer.py",
]


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    leaked = [path for path in FORBIDDEN_F1_IMPLEMENTATIONS if (ROOT / path).exists()]
    if missing:
        print("Missing F1 required paths:")
        for path in missing:
            print(f"  - {path}")
    if leaked:
        print("F2+ implementation leaked into F1:")
        for path in leaked:
            print(f"  - {path}")
    if missing or leaked:
        return 1
    print("F1 repository-scope validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
