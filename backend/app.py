"""FastAPI application factory for DiffGuard.

This module will later include router registration and dependency wiring.
"""

from __future__ import annotations

from fastapi import FastAPI

from backend.routes import webhook as webhook_routes


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        FastAPI: Configured FastAPI app.
    """
    app = FastAPI(title="DiffGuard API", version="0.1.0")

    app.include_router(webhook_routes.router)

    @app.get("/health")
    def health() -> dict[str, str]:  # pragma: no cover - trivial
        return {"status": "ok"}

    @app.get("/")
    def root() -> dict[str, str]:  # pragma: no cover - trivial
        return {"service": "diffguard", "status": "ok"}

    return app


app = create_app()
