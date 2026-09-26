from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from app.database import get_engine

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

def test_db_connection() -> None:
    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar_one() == 1