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

def get_incident(session: Session, incident_id: UUID) -> Incident | None:
    return session.get(Incident, incident_id)


def list_incidents(
    session: Session,
    limit: int,
    offset: int,
) -> list[Incident]:
    statement = (
        select(Incident)
        .order_by(Incident.created_at.desc(), Incident.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(session.scalars(statement).all())
