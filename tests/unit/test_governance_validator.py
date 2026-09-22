"""Regression tests for repository governance validators."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load_validator() -> ModuleType:
    path = Path(__file__).resolve().parents[2] / "scripts" / "validate_governance.py"
    spec = importlib.util.spec_from_file_location("validate_governance", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_yaml_list_parser_accepts_indentless_sequence() -> None:
    module = _load_validator()
    payload = """root:
  sports_scope:
    mandatory_sports:
    - BASKETBALL
    - FOOTBALL
    - MMA
    next_key: value
"""
    assert module._yaml_list_after_key(payload, "mandatory_sports") == [
        "BASKETBALL",
        "FOOTBALL",
        "MMA",
    ]


def test_yaml_list_parser_accepts_indented_sequence() -> None:
    module = _load_validator()
    payload = """root:
  values:
    - A
    - B
  next_key: value
"""
    assert module._yaml_list_after_key(payload, "values") == ["A", "B"]
