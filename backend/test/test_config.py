import pytest
from fastapi.testclient import TestClient

from app.database import get_engine
from app.main import create_app

from app.config import postgres_port



def test_startup_rejects_missing_database_user(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    get_engine.cache_clear()

    try:
        with pytest.raises(
            RuntimeError,
            match="Missing required environment variable: POSTGRES_USER",
        ):
            with TestClient(create_app()):
                pytest.fail("La aplicación arrancó sin POSTGRES_USER")
    finally:
        get_engine.cache_clear()

@pytest.mark.parametrize("value", ["0", "65536", "abc"])
def test_rejects_invalid_port(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv("POSTGRES_PORT", value)

    with pytest.raises(
        RuntimeError,
        match="POSTGRES_PORT must be an integer between 1 and 65535",
    ):
        postgres_port()


@pytest.mark.parametrize("value", ["1", "65535"])
def test_accepts_port_boundaries(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv("POSTGRES_PORT", value)

    assert postgres_port() == int(value)
