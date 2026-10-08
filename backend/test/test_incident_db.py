import pytest

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from app.database import get_engine
from app.models import Incident

@pytest.mark.parametrize(
    ("job_name", "log"),
    [
        (" ", "error"),
        ("daily-import", " \n"),
        ("daily-import", "a" * 65537),
    ],
    ids=["blank-job-name", "blank-log", "oversized-log"],
)
def test_database_rejects_invalid_incident(job_name: str, log: str):
    with pytest.raises(IntegrityError):
        with get_engine().begin() as connection:
            connection.execute(
                insert(Incident).values(job_name=job_name, log=log)
            )

    with get_engine().begin() as connection:
        assert connection.execute(select(1)).scalar_one() == 1
