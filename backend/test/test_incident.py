from app.incident import IncidentCreate, IncidentResponse
from app.models import Incident
import pytest
from pydantic import ValidationError
from uuid import uuid4
from datetime import datetime, timezone

pytestmark = pytest.mark.unit

def test_create_rejects_blank_job_name() -> None:
    name = " \t"

    with pytest.raises(ValidationError):
        IncidentCreate(job_name=name, log="error")


def test_create_preserves_log_line_breaks() -> None:
    log = "error on line 1\ntrace on line 2\n"

    incident = IncidentCreate(job_name="daily-import", log=log)

    assert incident.log == log


def test_create_rejects_blank_log() -> None:
    log = " \n\t"

    with pytest.raises(ValidationError):
        IncidentCreate(job_name="daily-import", log=log)


def test_create_rejects_log_over_64_kib() -> None:
    log = "🙂" * 16385

    with pytest.raises(ValidationError):
        IncidentCreate(job_name="daily-import", log=log)

def test_create_rejects_job_name_over_200_chars() -> None:
    name = "a" * 201

    with pytest.raises(ValidationError):
        IncidentCreate(job_name=name, log="error")

def test_create_accepts_log_at_64_kib() -> None:
    log = "🙂" * 16384

    incident = IncidentCreate(job_name="daily-import", log=log)

    assert len(log.encode("utf-8")) == 64 * 1024
    assert incident.log == log

def test_create_allows_missing_exit_code() -> None:
    incident = IncidentCreate(job_name="daily-import", log="test log")

    assert incident.exit_code is None

def test_create_accepts_exit_code() -> None:
    incident = IncidentCreate(job_name="daily-import", log="test log", exit_code=0)

    assert incident.exit_code == 0

def test_response_reads_orm_incident() -> None:
    incident_id = uuid4()
    created_at = datetime.now(timezone.utc)
    incident = Incident(
        id=incident_id,
        job_name="daily-import",
        log="error",
        exit_code=0,
        created_at=created_at,
    )

    response = IncidentResponse.model_validate(incident)

    assert response.id == incident_id
    assert response.exit_code == 0
    assert response.created_at == created_at

@pytest.mark.parametrize("exit_code", [-(2**31) - 1, 2**31])
def test_create_rejects_exit_code_outside_database_range(exit_code: int) -> None:
    with pytest.raises(ValidationError):
        IncidentCreate(job_name="daily-import", log="error", exit_code=exit_code)
