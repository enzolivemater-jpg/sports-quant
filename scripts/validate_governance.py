"""Mechanical checks for canonical SPORTS QUANT governance invariants.

This catches accidental drift in repository-controlled decisions.
It does not replace an independent critical review.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOUNDATION = ROOT / ".project" / "FOUNDATION_DECISIONS_v0.1.yaml"
OPEN_DECISIONS = ROOT / ".project" / "OPEN_DECISIONS.yaml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _yaml_list_after_key(text: str, key: str) -> list[str]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        match = re.match(rf"^(\s*){re.escape(key)}:\s*$", line)
        if not match:
            continue
        base_indent = len(match.group(1))
        values: list[str] = []
        for following in lines[index + 1 :]:
            if not following.strip():
                continue
            indent = len(following) - len(following.lstrip())
            item = re.match(r"^\s*-\s+([^#]+?)\s*$", following)

            # PyYAML commonly emits "indentless sequences": the list item may
            # have the same indentation as its mapping key.
            if item and indent >= base_indent:
                values.append(item.group(1).strip())
                continue

            if indent <= base_indent:
                break

        return values
    raise ValueError(f"Missing YAML list key: {key}")


def _require(text: str, needle: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(f"Missing canonical invariant: {needle}")


def main() -> int:
    if not FOUNDATION.is_file() or not OPEN_DECISIONS.is_file():
        print("Canonical governance files are missing")
        return 1

    foundation = _read(FOUNDATION)
    decisions = _read(OPEN_DECISIONS)
    errors: list[str] = []

    ids = re.findall(r"^\s*-\s+id:\s+(OD-\d{2})\s*$", decisions, flags=re.MULTILINE)
    expected = [f"OD-{number:02d}" for number in range(1, 30)]
    if ids != expected:
        errors.append(f"OPEN_DECISIONS IDs must be exactly OD-01..OD-29 in order; got {ids}")

    try:
        mandatory = _yaml_list_after_key(foundation, "mandatory_sports")
        if mandatory != ["BASKETBALL", "FOOTBALL", "MMA"]:
            errors.append(
                "mandatory_sports must be exactly BASKETBALL, FOOTBALL, MMA; "
                f"got {mandatory}"
            )
    except ValueError as exc:
        errors.append(str(exc))

    try:
        additional = _yaml_list_after_key(
            foundation,
            "approved_additional_sports_for_validation",
        )
        if additional != ["HANDBALL", "VOLLEYBALL", "TENNIS"]:
            errors.append(
                "approved additional sports must be exactly HANDBALL, VOLLEYBALL, TENNIS; "
                f"got {additional}"
            )
    except ValueError as exc:
        errors.append(str(exc))

    required_snippets = [
        "active: C2_DECISION_SUPPORT",
        "AUTOMATED_REAL_MONEY_WAGERING",
        "llm_or_human_may_directly_assign_final_p_safe: false",
        "production_p_safe_formula: DEFERRED",
        "critical_pit_rule: known_at <= decision_cutoff_at",
        "known_at_must_not_be_reconstructed_speculatively: true",
        "edge_safe: P_safe - P_market_no_vig",
        "invariant: edge_safe < 0 => not QUALIFIED",
        "composite_dynamic_market_risk_score: DEFERRED",
        "weighted_average_mr: DEFERRED",
        "predictability_evidence_gate_required: true",
        "predictability_evidence_gate_thresholds: NOT_DEFINED_DO_NOT_IMPLEMENT",
        "market_family: FOOTBALL_1X2",
        "market_family: FOOTBALL_TOTAL_GOALS_MAIN",
        "market_family: FOOTBALL_ASIAN_HANDICAP",
        "market_family: FOOTBALL_BTTS",
        "market_family: FOOTBALL_TEAM_TOTALS",
        "phase_1_market_families: NOT_DEFINED_DO_NOT_IMPLEMENT",
        "phase_2_market_families: NOT_DEFINED_DO_NOT_IMPLEMENT",
        "sport: FOOTBALL",
        "purpose: FIRST_END_TO_END_VERTICAL_VALIDATION",
    ]
    for snippet in required_snippets:
        _require(foundation, snippet, errors)

    if foundation.count("market_family: FOOTBALL_1X2") != 1:
        errors.append("FOOTBALL_1X2 must appear exactly once in Foundation market catalog")
    if foundation.count("market_family: FOOTBALL_TOTAL_GOALS_MAIN") != 1:
        errors.append(
            "FOOTBALL_TOTAL_GOALS_MAIN must appear exactly once in Foundation market catalog"
        )

    if errors:
        print("Governance validation: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Governance validation: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
