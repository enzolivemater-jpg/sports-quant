from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "research" / "capture_provider_json.py"


def _load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("capture_provider_json", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_redact_url_hides_sensitive_query_values() -> None:
    module = _load_module()

    url = (
        "https://provider.example/v1/odds?"
        "api_key=super-secret&api_token=sportmonks-secret&token=another-secret&market=h2h"
    )
    redacted = module._redact_url(url)

    assert "super-secret" not in redacted
    assert "another-secret" not in redacted
    assert "sportmonks-secret" not in redacted
    assert "%2A%2A%2AREDACTED%2A%2A%2A" in redacted
    assert "market=h2h" in redacted


def test_header_env_requires_existing_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.delenv("SPORTS_QUANT_TEST_PROVIDER_KEY", raising=False)

    with pytest.raises(ValueError, match="Missing required environment variable"):
        module._parse_header_env(["X-Api-Key=SPORTS_QUANT_TEST_PROVIDER_KEY"])


def test_header_env_reads_secret_without_transform(monkeypatch: pytest.MonkeyPatch) -> None:
    module = _load_module()
    monkeypatch.setenv("SPORTS_QUANT_TEST_PROVIDER_KEY", "secret-value")

    headers = module._parse_header_env(["X-Api-Key=SPORTS_QUANT_TEST_PROVIDER_KEY"])

    assert headers == {"X-Api-Key": "secret-value"}


def test_query_env_injects_secret_without_putting_it_in_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()
    monkeypatch.setenv("SPORTS_QUANT_TEST_PROVIDER_KEY", "query-secret")

    request_url, injected = module._build_request_url(
        "https://provider.example/v1/fixtures?league=39",
        ["api_key=SPORTS_QUANT_TEST_PROVIDER_KEY"],
    )

    assert "api_key=query-secret" in request_url
    assert injected == {"api_key"}
    assert "query-secret" not in module._redact_url(request_url, injected)


def test_sensitive_query_value_in_url_is_rejected() -> None:
    module = _load_module()

    with pytest.raises(ValueError, match="must use --query-env"):
        module._build_request_url(
            "https://provider.example/v1/fixtures?api_key=plain-secret",
            [],
        )


def test_credentials_embedded_in_url_are_rejected() -> None:
    module = _load_module()

    with pytest.raises(ValueError, match="Credentials embedded"):
        module._build_request_url(
            "https://user:password@provider.example/v1/fixtures",
            [],
        )


def test_output_path_is_confined_to_research_probe_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_module()
    root = (tmp_path / "research-probes").resolve()
    monkeypatch.setattr(module, "OUTPUT_ROOT", root)

    output = module._safe_output_dir("../provider", "../../probe")

    output.relative_to(root)
    assert output == root / "provider" / "probe"


def test_main_rejects_plain_http(monkeypatch: pytest.MonkeyPatch, capsys: Any) -> None:
    module = _load_module()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT),
            "--research-only",
            "--provider",
            "example",
            "--probe-name",
            "schema",
            "--url",
            "http://provider.example/v1/data",
        ],
    )

    exit_code = module.main()

    assert exit_code == 2
    assert "Only HTTPS provider URLs are allowed." in capsys.readouterr().err


class _FakeHeaders(dict[str, str]):
    def items(self) -> Any:
        return super().items()


class _FakeResponse:
    status = 200

    def __init__(self) -> None:
        self.headers = _FakeHeaders(
            {
                "Content-Type": "application/json",
                "X-RateLimit-Remaining": "99",
                "Set-Cookie": "must-not-be-recorded",
            }
        )

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return b'{"fixture_id": 123, "lineup": null}'


def test_successful_capture_is_research_only_and_does_not_assign_known_at(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = _load_module()
    root = (tmp_path / "research-probes").resolve()
    monkeypatch.setattr(module, "OUTPUT_ROOT", root)
    monkeypatch.setenv("SPORTS_QUANT_TEST_PROVIDER_KEY", "query-secret")

    requested_urls: list[str] = []

    def fake_urlopen(request: Any, **_kwargs: Any) -> _FakeResponse:
        requested_urls.append(request.full_url)
        return _FakeResponse()

    monkeypatch.setattr(module.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(SCRIPT),
            "--research-only",
            "--provider",
            "example-provider",
            "--probe-name",
            "fixtures",
            "--url",
            "https://provider.example/v1/fixtures?league=39",
            "--query-env",
            "api_key=SPORTS_QUANT_TEST_PROVIDER_KEY",
        ],
    )

    exit_code = module.main()

    assert exit_code == 0
    assert len(requested_urls) == 1
    assert "api_key=query-secret" in requested_urls[0]

    metadata_files = list(root.rglob("*.metadata.json"))
    assert len(metadata_files) == 1

    metadata_text = metadata_files[0].read_text(encoding="utf-8")
    metadata = json.loads(metadata_text)

    assert metadata["research_only"] is True
    assert metadata["canonical_known_at_assigned"] is False
    assert "known_at" not in metadata
    assert "received_at" in metadata
    assert "query-secret" not in metadata_text
    assert "Set-Cookie" not in metadata["selected_response_headers"]
    assert metadata["selected_response_headers"]["X-RateLimit-Remaining"] == "99"
    assert metadata["payload_sha256"]
    assert metadata["payload_bytes"] > 0

    payload_path = metadata_files[0].with_name(metadata["payload_file"])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    assert payload == {"fixture_id": 123, "lineup": None}
