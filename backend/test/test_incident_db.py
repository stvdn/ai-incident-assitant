from datetime import timedelta
from uuid import uuid4
import pytest

from sqlalchemy import insert, select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.incident import IncidentCreate
from app.incident_service import create_incident
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

def test_create_incident_is_visible_from_another_session() -> None:
    job_name = f"test-{uuid4()}"
    try:
        with Session(get_engine()) as writer:
            created = create_incident(
                writer,
                IncidentCreate(job_name=job_name, log="log"),
            )
            incident_id = created.id
            assert created.created_at.utcoffset() == timedelta(0)

        with Session(get_engine()) as reader:
            saved = reader.get(Incident, incident_id)
            assert saved is not None
            assert saved.job_name == job_name
            assert saved.exit_code is None
    finally:
        with Session(get_engine()) as cleanup:
            cleanup.execute(delete(Incident).where(Incident.job_name == job_name))
            cleanup.commit()
