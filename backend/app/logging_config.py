import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        event = {
            "timestamp": datetime.fromtimestamp(
                record.created, timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
        }

        for field in ("incident_id", "request_id", "error_type"):
            value = getattr(record, field, None)
            if value is not None:
                event[field] = str(value)

        return json.dumps(event, ensure_ascii=False)


def configure_logging() -> None:
    logger = logging.getLogger("incident_assistant")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
