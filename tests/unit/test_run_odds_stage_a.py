from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "research" / "run_odds_stage_a.py"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("run_odds_stage_a", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_probe_specs_has_69_secret_free_requests() -> None:
    module = _load_module()
    data = module.load_manifest()

    specs = module.build_probe_specs(data)

    assert len(specs) == 69
    assert len({(item["group_id"], item["cutoff"]) for item in specs}) == 69
    assert all("apiKey=" not in item["url"] for item in specs)
    assert all("markets=h2h,totals" in item["url"] for item in specs)
    assert all("regions=eu" in item["url"] for item in specs)
    assert all("date=" in item["url"] for item in specs)


def test_manifest_credit_estimate_matches_stage_a_plan() -> None:
    module = _load_module()
    data = module.load_manifest()

    assert module.estimate_credits(data, 1) == 20
    assert module.estimate_credits(data, 5) == 100
    assert module.estimate_credits(data, 69) == 1380


def test_default_selection_is_one_request() -> None:
    module = _load_module()
    specs = module.build_probe_specs(module.load_manifest())

    selected = module.select_specs(specs, offset=0, limit=1, all_stage_a=False)

    assert len(selected) == 1
    assert selected[0] == specs[0]


def test_all_stage_a_selects_every_request() -> None:
    module = _load_module()
    specs = module.build_probe_specs(module.load_manifest())

    selected = module.select_specs(specs, offset=12, limit=2, all_stage_a=True)

    assert len(selected) == 69


def test_full_execution_requires_exact_request_count_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    monkeypatch.setenv(module.KEY_ENV, "secret")

    with pytest.raises(ValueError, match="confirm-request-count 69"):
        module._validate_execution_ack(
            execute=True,
            ack_paid_provider_access=True,
            all_stage_a=True,
            confirm_request_count=None,
            selected_count=69,
            estimated_credits=1380,
            max_credits=1380,
        )


def test_execution_requires_paid_access_ack() -> None:
    module = _load_module()

    with pytest.raises(ValueError, match="ack-paid-provider-access"):
        module._validate_execution_ack(
            execute=True,
            ack_paid_provider_access=False,
            all_stage_a=False,
            confirm_request_count=None,
            selected_count=1,
            estimated_credits=20,
            max_credits=20,
        )


def test_execution_requires_max_credit_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.KEY_ENV, "secret")

    with pytest.raises(ValueError, match="--max-credits"):
        module._validate_execution_ack(
            execute=True,
            ack_paid_provider_access=True,
            all_stage_a=False,
            confirm_request_count=None,
            selected_count=1,
            estimated_credits=20,
            max_credits=None,
        )


def test_execution_rejects_estimate_above_credit_cap(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    monkeypatch.setenv(module.KEY_ENV, "secret")

    with pytest.raises(ValueError, match="exceeds --max-credits"):
        module._validate_execution_ack(
            execute=True,
            ack_paid_provider_access=True,
            all_stage_a=False,
            confirm_request_count=None,
            selected_count=5,
            estimated_credits=100,
            max_credits=99,
        )


def test_execution_accepts_exact_credit_cap(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setenv(module.KEY_ENV, "secret")

    module._validate_execution_ack(
        execute=True,
        ack_paid_provider_access=True,
        all_stage_a=False,
        confirm_request_count=None,
        selected_count=5,
        estimated_credits=100,
        max_credits=100,
    )


def test_dry_run_needs_no_api_key(
    monkeypatch: pytest.MonkeyPatch,
    capsys: Any,
) -> None:
    module = _load_module()
    monkeypatch.delenv(module.KEY_ENV, raising=False)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT)])

    exit_code = module.main()

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "Selected probes: 1" in output
    assert "Estimated credits under current manifest assumption: 20" in output
    assert "No API request was sent." in output
