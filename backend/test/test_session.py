from uuid import uuid4
import pytest
from app.database import get_session, get_engine
from app.models import Incident
from sqlalchemy.orm import Session
from sqlalchemy import select



def test_session_rolls_back() -> None:
    incident_id = uuid4()
    session_generator = get_session()
    session = next(session_generator)

    session.add(Incident(id=incident_id, job_name="job", log="error"))
    session.flush()

    with pytest.raises(RuntimeError):
        session_generator.throw(RuntimeError("operation error"))


    with Session(get_engine()) as next_session:
        assert next_session.get(Incident, incident_id) is None
        assert next_session.execute(select(1)).scalar_one() == 1
