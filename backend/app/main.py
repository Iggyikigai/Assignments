from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import dashboard_routes, ingestion_routes, schema_routes
from app.dependencies import create_container
from app.errors import register_exception_handlers


def create_app() -> FastAPI:
    app = FastAPI(title="Schema-Driven Dashboard Platform")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.container = create_container()
    register_exception_handlers(app)
    app.include_router(schema_routes.router)
    app.include_router(ingestion_routes.router)
    app.include_router(dashboard_routes.router)
    return app


app = create_app()
