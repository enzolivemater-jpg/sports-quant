import pytest

from sports_quant.db.engine import build_engine


def test_build_engine_rejects_empty_url() -> None:
    with pytest.raises(ValueError, match="database_url"):
        build_engine("")
