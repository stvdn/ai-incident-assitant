from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException
import logging

logger = logging.getLogger("incident_assistant")

async def handle_unexpected_error(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = request.state.request_id

    logger.error(
        "request_failed",
        extra={
            "request_id": request_id,
            "error_type": type(exc).__name__,
        },
    )
    return JSONResponse(
        headers={"X-Request-ID": request_id},
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "Internal server error",
            }
        },
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, handle_unexpected_error)

    @app.exception_handler(HTTPException)
    async def handle_http_error(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            headers=exc.headers,
            content={
                "error": {
                    "code": "not_found" if exc.status_code == 404 else "http_error",
                    "message": exc.detail,
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Invalid request",
                    "details": [
                        {
                            "location": list(error["loc"]),
                            "type": error["type"],
                        }
                        for error in exc.errors()
                    ],
                }
            },
        )
