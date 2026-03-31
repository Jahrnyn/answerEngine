from fastapi import FastAPI

from answer_engine_backend.api.routes import health_router


def create_app() -> FastAPI:
    app = FastAPI(title="Answer Engine Backend")
    app.include_router(health_router)
    return app


app = create_app()
