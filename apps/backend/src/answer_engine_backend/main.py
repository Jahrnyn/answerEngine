from fastapi import FastAPI

from answer_engine_backend.api.routes import cfhee_router, health_router, runs_router


def create_app() -> FastAPI:
    app = FastAPI(title="Answer Engine Backend")
    app.include_router(health_router)
    app.include_router(cfhee_router)
    app.include_router(runs_router)
    return app


app = create_app()
