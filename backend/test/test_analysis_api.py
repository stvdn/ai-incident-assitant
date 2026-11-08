from collections.abc import Generator
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.analysis import AnalysisResult
from app.analyzer import (
    AnalysisInput,
    AnalysisProviderError,
    AnalysisRateLimit,
    AnalysisTimeout,
    get_analyzer,
)
from app.database import get_engine
from app.main import create_app
from app.models import Incident, IncidentAnalysis


pytestmark = pytest.mark.integration


class FakeAnalyzer:
    model = "fake-model"

    def analyze(self, incident: AnalysisInput) -> AnalysisResult:
        assert incident.log == "Connection refused at db:5432"

        return AnalysisResult(
            probable_cause="PostgreSQL is unreachable.",
            confidence=0.85,
            evidence=["Connection refused at db:5432"],
            suggested_actions=["Check PostgreSQL availability."],
        )


@pytest.fixture
def incident_id() -> Generator[UUID, None, None]:
    value = uuid4()

    try:
        with Session(get_engine()) as session:
            session.add(
                Incident(
                    id=value,
                    job_name=f"analysis-test-{value}",
                    log="Connection refused at db:5432",
                    exit_code=1,
                )
            )
            session.commit()

        yield value
    finally:
        with Session(get_engine()) as session:
            session.execute(
                delete(IncidentAnalysis).where(
                    IncidentAnalysis.incident_id == value
                )
            )
            session.execute(
                delete(Incident).where(Incident.id == value)
            )
            session.commit()


def test_analysis_is_persisted_and_retrievable(
    incident_id: UUID,
) -> None:
    app = create_app()
    app.dependency_overrides[get_analyzer] = lambda: FakeAnalyzer()

    with TestClient(app) as client:
        created = client.post(f"/incidents/{incident_id}/analyses")

        assert created.status_code == 201
        body = created.json()
        assert body["incident_id"] == str(incident_id)
        assert body["model"] == "fake-model"
        assert body["status"] == "completed"
        assert body["latency_ms"] >= 0

        fetched = client.get(f"/incidents/{incident_id}/analyses")

        assert fetched.status_code == 200
        assert fetched.json() == [body]

    # A separate session proves that the write was committed.
    with Session(get_engine()) as session:
        stored = session.get(IncidentAnalysis, UUID(body["id"]))

        assert stored is not None
        assert stored.incident_id == incident_id
        assert stored.evidence == ["Connection refused at db:5432"]


@pytest.mark.parametrize(
    ("failure", "expected_status"),
    [
        (AnalysisTimeout, 504),
        (AnalysisRateLimit, 503),
        (AnalysisProviderError, 502),
    ],
)
def test_provider_failure_does_not_persist_analysis(
    incident_id: UUID,
    failure: type[AnalysisProviderError],
    expected_status: int,
) -> None:
    class FailingAnalyzer:
        model = "fake-model"

        def analyze(self, incident: AnalysisInput) -> AnalysisResult:
            raise failure("private-provider-marker")

    app = create_app()
    app.dependency_overrides[get_analyzer] = lambda: FailingAnalyzer()

    with TestClient(app) as client:
        response = client.post(f"/incidents/{incident_id}/analyses")

    assert response.status_code == expected_status
    assert "private-provider-marker" not in response.text

    with Session(get_engine()) as session:
        assert session.scalar(
            select(IncidentAnalysis.id).where(
                IncidentAnalysis.incident_id == incident_id
            )
        ) is None
        assert session.get(Incident, incident_id) is not None


def test_invalid_provider_output_does_not_persist(
    incident_id: UUID,
) -> None:
    class InvalidAnalyzer:
        model = "fake-model"

        def analyze(self, incident: AnalysisInput):
            return {
                "probable_cause": "private-provider-marker",
                "confidence": 2,
                "evidence": [],
                "suggested_actions": [],
            }

    app = create_app()
    app.dependency_overrides[get_analyzer] = lambda: InvalidAnalyzer()

    with TestClient(app) as client:
        response = client.post(f"/incidents/{incident_id}/analyses")
        fetched = client.get(f"/incidents/{incident_id}/analyses")

    assert response.status_code == 502
    assert "private-provider-marker" not in response.text
    assert fetched.status_code == 200
    assert fetched.json() == []


@pytest.mark.parametrize("method", ["post", "get"])
def test_analysis_for_missing_incident(method: str) -> None:
    app = create_app()
    app.dependency_overrides[get_analyzer] = lambda: FakeAnalyzer()

    with TestClient(app) as client:
        response = getattr(client, method)(
            f"/incidents/{uuid4()}/analyses"
        )

    assert response.status_code == 404


def test_analysis_requires_configured_provider(
    incident_id: UUID,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with TestClient(create_app()) as client:
        response = client.post(f"/incidents/{incident_id}/analyses")

    assert response.status_code == 503
