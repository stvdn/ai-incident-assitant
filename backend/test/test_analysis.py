from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.analysis import AnalysisResponse, AnalysisResult
from app.models import IncidentAnalysis


pytestmark = pytest.mark.unit


def valid_result() -> dict:
    return {
        "probable_cause": "The database connection was refused.",
        "confidence": 0.85,
        "evidence": ["Connection refused at db:5432"],
        "suggested_actions": [
            "Check whether PostgreSQL is running.",
        ],
    }


def test_accepts_valid_analysis() -> None:
    result = AnalysisResult.model_validate(valid_result())

    assert result.confidence == 0.85
    assert result.evidence == ["Connection refused at db:5432"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("probable_cause", " \n "),
        ("confidence", -0.1),
        ("confidence", 1.1),
        ("confidence", float("nan")),
        ("confidence", float("inf")),
        ("evidence", []),
        ("evidence", [" "]),
        ("evidence", ["item"] * 11),
        ("suggested_actions", []),
        ("suggested_actions", [""]),
        ("suggested_actions", ["item"] * 11),
    ],
)
def test_rejects_invalid_analysis(field: str, value: object) -> None:
    payload = valid_result()
    payload[field] = value

    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(payload)


def test_rejects_unexpected_provider_fields() -> None:
    payload = valid_result()
    payload["execute_command"] = "restart database"

    with pytest.raises(ValidationError):
        AnalysisResult.model_validate(payload)


def test_response_reads_stored_analysis() -> None:
    analysis_id = uuid4()
    incident_id = uuid4()
    created_at = datetime.now(timezone.utc)

    stored = IncidentAnalysis(
        id=analysis_id,
        incident_id=incident_id,
        **valid_result(),
        status="completed",
        model="fake-model",
        latency_ms=125,
        created_at=created_at,
    )

    response = AnalysisResponse.model_validate(stored)

    assert response.id == analysis_id
    assert response.incident_id == incident_id
    assert response.status == "completed"
    assert response.model == "fake-model"
    assert response.latency_ms == 125
    assert response.created_at == created_at