import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from google.genai import errors

from app.analyzer import (
    AnalysisInput,
    AnalysisProviderError,
    AnalysisRateLimit,
    AnalysisTimeout,
)
from app.gemini_analyzer import GeminiAnalyzer


pytestmark = pytest.mark.unit


@pytest.fixture
def incident() -> AnalysisInput:
    return AnalysisInput(
        job_name="daily-import",
        log="Connection refused at db:5432",
        exit_code=1,
    )


def valid_payload() -> dict:
    return {
        "probable_cause": "PostgreSQL is unreachable.",
        "confidence": 0.8,
        "evidence": ["Connection refused at db:5432"],
        "suggested_actions": ["Check PostgreSQL availability."],
    }


def test_analyzes_with_structured_output(
    incident: AnalysisInput,
) -> None:
    client = Mock()
    client.models.generate_content.return_value = SimpleNamespace(
        text=json.dumps(valid_payload()),
    )
    analyzer = GeminiAnalyzer(client, model="test-model")

    result = analyzer.analyze(incident)

    assert result.confidence == 0.8
    assert result.evidence == [incident.log]

    arguments = client.models.generate_content.call_args.kwargs
    assert arguments["model"] == "test-model"

    supplied_data = json.loads(arguments["contents"])
    assert supplied_data["log"] == incident.log
    assert supplied_data["exit_code"] == 1

    config = arguments["config"]
    assert config.response_mime_type == "application/json"
    assert config.response_json_schema is not None
    assert "untrusted data" in config.system_instruction


@pytest.mark.parametrize(
    ("status_code", "expected_error"),
    [
        (429, AnalysisRateLimit),
        (408, AnalysisTimeout),
        (504, AnalysisTimeout),
        (403, AnalysisProviderError),
        (500, AnalysisProviderError),
    ],
)
def test_maps_provider_errors(
    incident: AnalysisInput,
    status_code: int,
    expected_error: type[AnalysisProviderError],
) -> None:
    client = Mock()
    client.models.generate_content.side_effect = errors.APIError(
        status_code,
        {
            "error": {
                "code": status_code,
                "message": "private-provider-marker",
            },
        },
    )

    with pytest.raises(expected_error) as captured:
        GeminiAnalyzer(client, "test-model").analyze(incident)

    assert "private-provider-marker" not in str(captured.value)


@pytest.mark.parametrize(
    ("failure", "expected_error"),
    [
        (
            httpx.ReadTimeout("private-network-marker"),
            AnalysisTimeout,
        ),
        (
            httpx.ConnectError("private-network-marker"),
            AnalysisProviderError,
        ),
    ],
)
def test_maps_transport_errors(
    incident: AnalysisInput,
    failure: Exception,
    expected_error: type[AnalysisProviderError],
) -> None:
    client = Mock()
    client.models.generate_content.side_effect = failure

    with pytest.raises(expected_error) as captured:
        GeminiAnalyzer(client, "test-model").analyze(incident)

    assert "private-network-marker" not in str(captured.value)


@pytest.mark.parametrize(
    "text",
    [
        None,
        "",
        "not JSON",
        "{}",
        json.dumps({**valid_payload(), "confidence": 2}),
        json.dumps({
            **valid_payload(),
            "evidence": ["An error that is not in the log"],
        }),
    ],
)
def test_rejects_unusable_output(
    incident: AnalysisInput,
    text: str | None,
) -> None:
    client = Mock()
    client.models.generate_content.return_value = SimpleNamespace(
        text=text,
    )

    with pytest.raises(AnalysisProviderError):
        GeminiAnalyzer(client, "test-model").analyze(incident)