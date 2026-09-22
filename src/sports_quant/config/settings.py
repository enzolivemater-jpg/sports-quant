"""Minimal environment-backed settings for F1 infrastructure only."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    """Non-domain runtime settings.

    F1 intentionally avoids model, market, probability, or decision configuration.
    """

    environment: str
    database_url: str | None
    log_level: str
    otel_service_name: str


def load_settings() -> Settings:
    """Load infrastructure settings from environment variables."""

    return Settings(
        environment=os.getenv("SPORTS_QUANT_ENV", "local"),
        database_url=os.getenv("SPORTS_QUANT_DATABASE_URL"),
        log_level=os.getenv("SPORTS_QUANT_LOG_LEVEL", "INFO").upper(),
        otel_service_name=os.getenv("SPORTS_QUANT_OTEL_SERVICE_NAME", "sports-quant"),
    )
