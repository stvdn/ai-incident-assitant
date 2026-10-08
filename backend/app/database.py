from app.config import required_env, postgres_port
from functools import lru_cache
from sqlalchemy import create_engine, URL, Engine
from sqlalchemy.orm import Session
from collections.abc import Generator


@lru_cache
def get_engine() -> Engine:
    url = URL.create(
        drivername="postgresql+psycopg",
        username=required_env("POSTGRES_USER"),
        password=required_env("POSTGRES_PASSWORD"),
        host=required_env("POSTGRES_HOST"),
        port=postgres_port(),
        database=required_env("POSTGRES_DB"),
    )

    return create_engine(
        url,
        connect_args={"connect_timeout": 5},
        pool_pre_ping=True,
    )

def get_session() -> Generator[Session, None, None]:
    session = Session(get_engine())
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
