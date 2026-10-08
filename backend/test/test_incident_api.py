from uuid import uuid4
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.database import get_engine
from app.main import create_app
from app.models import Incident


def test_create_and_read_incident() -> None:
    payload = {
        "job_name": f"test-{uuid4()}",
        "log": "Connection timeout",
        "exit_code": 1,
    }

    try:
        with TestClient(create_app()) as client:
            created = client.post("/incidents", json=payload)

            assert created.status_code == 201
            body = created.json()
            assert body["job_name"] == payload["job_name"]
            assert body["log"] == payload["log"]
            assert body["exit_code"] == 1

            fetched = client.get(f"/incidents/{body['id']}")

            assert fetched.status_code == 200
            assert fetched.json() == body

    finally:
        with Session(get_engine()) as cleanup:
            cleanup.execute(
                delete(Incident).where(
                    Incident.job_name == payload["job_name"]
                )
            )
            cleanup.commit()

@pytest.mark.parametrize(
    ("path", "expected_status"),
    [
        (f"/incidents/{uuid4()}", 404),
        ("/incidents/abc", 422),
        ("/incidents?limit=0", 422),
        ("/incidents?limit=101", 422),
        ("/incidents?offset=-1", 422),
    ],
    ids=[
        "not-found",
        "invalid-uuid",
        "limit-too-small",
        "limit-too-large",
        "negative-offset",
    ],
)

def test_incident_http_errors(path: str, expected_status: int) -> None:
    with TestClient(create_app()) as client:
        response = client.get(path)

    assert response.status_code == expected_status

def test_list_incidents_pagination() -> None:
    job_name = f"pagination-{uuid4()}"
    ids = [uuid4() for _ in range(3)]
    expected_ids = [str(value) for value in sorted(ids, reverse=True)]
    created_at = datetime(2026, 1, 1, tzinfo=timezone.utc)

    try:
        with Session(get_engine()) as session:
            count = session.scalar(
                select(func.count()).select_from(Incident)
            )
            assert count == 0, "Esta prueba requiere la base de tests vacía"

            session.add_all([
                Incident(
                    id=incident_id,
                    job_name=job_name,
                    log="pagination test",
                    created_at=created_at,
                )
                for incident_id in ids
            ])
            session.commit()

        with TestClient(create_app()) as client:
            first = client.get("/incidents?limit=2&offset=0")
            second = client.get("/incidents?limit=2&offset=2")
            exhausted = client.get("/incidents?limit=2&offset=3")

        assert first.status_code == 200
        assert second.status_code == 200
        assert exhausted.status_code == 200

        first_page = first.json()
        second_page = second.json()

        assert [item["id"] for item in first_page["items"]] == expected_ids[:2]
        assert [item["id"] for item in second_page["items"]] == expected_ids[2:]
        assert first_page["limit"] == second_page["limit"] == 2
        assert first_page["offset"] == 0
        assert second_page["offset"] == 2
        assert exhausted.json() == {"items": [], "limit": 2, "offset": 3}
    finally:
        with Session(get_engine()) as cleanup:
            cleanup.execute(
                delete(Incident).where(Incident.job_name == job_name)
            )
            cleanup.commit()
