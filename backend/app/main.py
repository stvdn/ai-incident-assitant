from fastapi import Depends, FastAPI, status, HTTPException, Query, Request, Response
from uuid import UUID, uuid4
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from app.database import get_session, get_engine
from app.incident import IncidentCreate, IncidentResponse, IncidentListResponse
from app.incident_service import create_incident, get_incident, list_incidents
from app.errors import register_error_handlers, handle_unexpected_error
from app.logging_config import configure_logging

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    engine = get_engine()
    try:
        yield
    finally:
        engine.dispose()

def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Incident Assistant",
        version="0.1.0",
        lifespan=lifespan,
    )

    register_error_handlers(app)

    @app.middleware("http")
    async def add_request_id(request: Request, call_next) -> Response:
        request.state.request_id = str(uuid4())

        try:
            response = await call_next(request)
        except Exception as exc:
            response = await handle_unexpected_error(request, exc)

        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.post(
        "/incidents",
        response_model=IncidentResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["incidents"],
    )
    def post_incident(
        payload: IncidentCreate,
        session: Session = Depends(get_session),
    )-> IncidentResponse:
        incident = create_incident(session, payload)
        return IncidentResponse.model_validate(incident)


    @app.get(
        "/incidents/{incident_id}",
        response_model=IncidentResponse,
        tags=["incidents"],
    )
    def read_incident(
        incident_id: UUID,
        session: Session = Depends(get_session),
    ) -> IncidentResponse:
        incident = get_incident(session, incident_id)

        if incident is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Incident not found",
            )

        return IncidentResponse.model_validate(incident)

    @app.get(
        "/incidents",
        response_model=IncidentListResponse,
        tags=["incidents"],
    )
    def read_incidents(
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        session: Session = Depends(get_session),
    ) -> IncidentListResponse:
        incidents = list_incidents(session, limit, offset)
        return IncidentListResponse(
            items=[
                IncidentResponse.model_validate(incident)
                for incident in incidents
            ],
            limit=limit,
            offset=offset,
        )

    return app

app = create_app()
