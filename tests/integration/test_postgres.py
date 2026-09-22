import os

import pytest
from sqlalchemy import text

from sports_quant.db.engine import build_engine


@pytest.mark.integration
def test_postgres_connectivity() -> None:
    database_url = os.environ.get("SPORTS_QUANT_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("SPORTS_QUANT_TEST_DATABASE_URL is not configured")
    engine = build_engine(database_url)
    with engine.connect() as connection:
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
    engine.dispose()
