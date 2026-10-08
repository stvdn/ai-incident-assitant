from sqlalchemy.orm import Session
from sqlalchemy import select
from app.incident import IncidentCreate
from app.models import Incident
from uuid import UUID

def create_incident(session: Session, data: IncidentCreate) -> Incident:
    incident = Incident(
        job_name = data.job_name,
        log = data.log,
        exit_code = data.exit_code
    )
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return incident
