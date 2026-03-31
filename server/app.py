"""
server/app.py — OpenEnv multi-mode deployment entry point.
Re-exports the FastAPI app from api/server.py so the validator
can find the app at the expected `server.app:app` path.
"""
from api.server import app  # noqa: F401

__all__ = ["app"]
