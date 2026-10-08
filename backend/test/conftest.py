import logging
from collections.abc import Generator
from io import StringIO

import pytest

from app.logging_config import JsonFormatter


@pytest.fixture
def application_logs() -> Generator[StringIO, None, None]:
    output = StringIO()
    handler = logging.StreamHandler(output)
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("incident_assistant")
    logger.addHandler(handler)
    try:
        yield output
    finally:
        logger.removeHandler(handler)
        handler.close()
