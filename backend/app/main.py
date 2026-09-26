from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Incident Assistant",
        version="0.1.0",
    )

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app

app = create_app()
