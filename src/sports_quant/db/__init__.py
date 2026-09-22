"""Database infrastructure skeleton. Domain tables start in later phases."""

from sqlalchemy import MetaData

metadata = MetaData()

__all__ = ["metadata"]
