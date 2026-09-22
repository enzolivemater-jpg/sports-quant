from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "research" / "run_provider_probes.py"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("run_provider_probes", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _manifest() -> dict[str, object]:
    return {
        "providers": [
            {
                "provider": "alpha",
                "auth": {"type": "header_env", "name": "X-Key", "env": "ALPHA_KEY"},
                "probes": [
                    {
                        "probe_name": "schema",
                        "url": "https://alpha.example/schema",
                        "purpose": "schema",
                    },
                    {
                        "probe_name": "coverage",
                        "url": "https://alpha.example/coverage",
                        "purpose": "coverage",
                    },
                ],
            },
            {
                "provider": "beta",
                "auth": {"type": "header_env", "name": "Authorization", "env": "BETA_KEY"},
                "probes": [
                    {
                        "probe_name": "schema",
                        "url": "https://beta.example/schema",
                        "purpose": "schema",
                    }
                ],
            },
        ]
    }


def test_build_probe_specs() -> None:
    module = _load_module()

    specs = module.build_probe_specs(_manifest())

    assert len(specs) == 3
    assert specs[0]["provider"] == "alpha"
    assert specs[0]["auth_env"] == "ALPHA_KEY"


def test_provider_filter_and_limit() -> None:
    module = _load_module()
    specs = module.build_probe_specs(_manifest())

    selected = module.select_specs(
        specs,
        providers={"alpha"},
        offset=1,
        limit=1,
        all_selected=False,
    )

    assert len(selected) == 1
    assert selected[0]["probe_name"] == "coverage"


def test_execute_requires_explicit_quota_ack(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    specs = module.build_probe_specs(_manifest())
    monkeypatch.setenv("ALPHA_KEY", "secret")

    with pytest.raises(ValueError, match="--ack-trial-quota"):
        module._validate_execution([specs[0]], False)


def test_execute_requires_provider_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    specs = module.build_probe_specs(_manifest())
    monkeypatch.delenv("ALPHA_KEY", raising=False)

    with pytest.raises(ValueError, match="ALPHA_KEY"):
        module._validate_execution([specs[0]], True)


def test_dry_run_is_default(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "load_manifest", _manifest)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT)])

    exit_code = module.main()

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "No provider request was sent." in output


def test_unknown_provider_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setattr(module, "load_manifest", _manifest)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--provider", "unknown"])

    assert module.main() == 2
