import json
import logging

from sports_quant.observability.logging import JsonFormatter


def test_json_formatter_emits_structured_fields() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="sports_quant.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    payload = json.loads(formatter.format(record))
    assert payload["level"] == "INFO"
    assert payload["logger"] == "sports_quant.test"
    assert payload["message"] == "hello"
    assert "timestamp" in payload
