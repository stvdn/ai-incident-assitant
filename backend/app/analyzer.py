import os
from collections.abc import Generator
from dataclasses import dataclass
from typing import Protocol

from app.analysis import AnalysisResult


@dataclass(frozen=True)
class AnalysisInput:
    job_name: str
    log: str
    exit_code: int | None


class IncidentAnalyzer(Protocol):
    model: str

    def analyze(self, incident: AnalysisInput) -> AnalysisResult:
        ...


class AnalysisProviderError(Exception):
    """The provider could not return a usable analysis."""


class AnalysisTimeout(AnalysisProviderError):
    pass


class AnalysisRateLimit(AnalysisProviderError):
    pass


def get_analyzer() -> Generator[IncidentAnalyzer, None, None]:
    from fastapi import HTTPException
    from google import genai
    from google.genai import types

    from app.gemini_analyzer import GeminiAnalyzer

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    model = os.environ.get(
        "GEMINI_MODEL",
        "gemini-2.5-flash-lite",
    ).strip()

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="Analysis provider is not configured",
        )

    if not model or len(model) > 200:
        raise HTTPException(
            status_code=503,
            detail="Analysis model configuration is invalid",
        )

    with genai.Client(
        api_key=api_key,
        vertexai=False,
        http_options=types.HttpOptions(
            timeout=30_000,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    ) as client:
        yield GeminiAnalyzer(client=client, model=model)
