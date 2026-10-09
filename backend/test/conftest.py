import logging
import pytest
import os
from collections.abc import Generator
from io import StringIO

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

@pytest.fixture(autouse=True)
def require_test_database(request: pytest.FixtureRequest) -> None:
    if request.node.get_closest_marker("integration") is None:
        return

    if os.environ.get("POSTGRES_DB") != "incidents_test":
        pytest.fail(
            "Integration requires POSTGRES_DB=incidents_test. "
            "Run with --env-file ../.env.test."
        )