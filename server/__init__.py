"""
server — OpenEnv multi-mode deployment entry point.
Re-exports the FastAPI app from server.app so both
`server.app:app` and direct imports work.
"""
from server.app import app  # noqa: F401

__all__ = ["app"]
