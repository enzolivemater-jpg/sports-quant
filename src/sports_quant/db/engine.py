"""SQLAlchemy engine construction for local/test infrastructure."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine


def build_engine(database_url: str) -> Engine:
    """Build an engine without introducing domain schema or side effects."""

    if not database_url:
        raise ValueError("database_url must be non-empty")
    return create_engine(database_url, pool_pre_ping=True)
