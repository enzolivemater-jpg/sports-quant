from sports_quant.config.settings import load_settings


def test_settings_have_safe_non_secret_defaults(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.delenv("SPORTS_QUANT_DATABASE_URL", raising=False)
    monkeypatch.delenv("SPORTS_QUANT_ENV", raising=False)
    settings = load_settings()
    assert settings.environment == "local"
    assert settings.database_url is None
