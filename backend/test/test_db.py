import pytest
from sqlalchemy import text
from app.database import get_engine

pytestmark = pytest.mark.integration

def test_db_connection() -> None:
    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar_one() == 1
