"""
server/app.py — OpenEnv multi-mode deployment entry point.
Re-exports the FastAPI app from api/server.py so both
`server.app:app` and `api.server:app` module paths work.
"""
from api.server import app  # noqa: F401

__all__ = ["app"]
