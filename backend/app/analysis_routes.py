from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.analysis import AnalysisResponse
from app.analysis_service import (
    IncidentNotFound,
    create_analysis,
    list_analyses,
)
from app.analyzer import (
    AnalysisProviderError,
    AnalysisRateLimit,
    AnalysisTimeout,
    IncidentAnalyzer,
    get_analyzer,
)
from app.database import get_session
import logging

logger = logging.getLogger("incident_assistant")


router = APIRouter(
    prefix="/incidents/{incident_id}/analyses",
    tags=["analyses"],
)


@router.post("", response_model=AnalysisResponse, status_code=201)
def post_analysis(
    incident_id: UUID,
    session: Session = Depends(get_session),
    analyzer: IncidentAnalyzer = Depends(get_analyzer),
) -> AnalysisResponse:
    try:
        return create_analysis(session, incident_id, analyzer)
    except IncidentNotFound:
        raise HTTPException(404, "Incident not found") from None
    except AnalysisTimeout:
        raise HTTPException(504, "Analysis provider timed out") from None
    except AnalysisRateLimit:
        raise HTTPException(
            503,
            "Analysis provider is temporarily unavailable",
        ) from None
    except AnalysisProviderError as exc:
        logger.warning(
            "Analysis failed: %s",
            str(exc),
            extra={"incident_id": str(incident_id)},
        )
        raise HTTPException(
            502,
            "Analysis provider returned an unusable result",
        ) from None


@router.get("", response_model=list[AnalysisResponse])
def read_analyses(
    incident_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> list[AnalysisResponse]:
    try:
        return list_analyses(session, incident_id, limit, offset)
    except IncidentNotFound:
        raise HTTPException(404, "Incident not found") from None