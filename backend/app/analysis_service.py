import logging
from time import perf_counter
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.analysis import AnalysisResponse, AnalysisResult
from app.analyzer import (
    AnalysisInput,
    AnalysisProviderError,
    IncidentAnalyzer,
)
from app.models import Incident, IncidentAnalysis


logger = logging.getLogger("incident_assistant")


class IncidentNotFound(Exception):
    pass


def create_analysis(
    session: Session,
    incident_id: UUID,
    analyzer: IncidentAnalyzer,
) -> AnalysisResponse:
    incident = session.get(Incident, incident_id)

    if incident is None:
        raise IncidentNotFound

    # Copy values before releasing the read transaction.
    data = AnalysisInput(
        job_name=incident.job_name,
        log=incident.log,
        exit_code=incident.exit_code,
    )

    # This service owns its request session. There are no pending writes.
    # Release the database connection before waiting for the provider.
    session.rollback()

    started = perf_counter()

    try:
        result = AnalysisResult.model_validate(analyzer.analyze(data))
        model = analyzer.model.strip()

        if not model or len(model) > 200:
            raise AnalysisProviderError("Invalid model metadata")
    except ValidationError as exc:
        raise AnalysisProviderError("Invalid analysis output") from exc

    elapsed_ms = int((perf_counter() - started) * 1000)

    stored = IncidentAnalysis(
        incident_id=incident_id,
        **result.model_dump(),
        status="completed",
        model=model,
        latency_ms=elapsed_ms,
    )
    session.add(stored)
    session.commit()
    session.refresh(stored)

    logger.info(
        "analysis_created",
        extra={"incident_id": str(incident_id)},
    )

    return AnalysisResponse.model_validate(stored)


def list_analyses(
    session: Session,
    incident_id: UUID,
    limit: int,
    offset: int,
) -> list[AnalysisResponse]:
    if session.get(Incident, incident_id) is None:
        raise IncidentNotFound

    statement = (
        select(IncidentAnalysis)
        .where(IncidentAnalysis.incident_id == incident_id)
        .order_by(
            IncidentAnalysis.created_at.desc(),
            IncidentAnalysis.id.desc(),
        )
        .limit(limit)
        .offset(offset)
    )

    return [
        AnalysisResponse.model_validate(row)
        for row in session.scalars(statement)
    ]