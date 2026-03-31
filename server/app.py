"""
server/app.py — OpenEnv multi-mode deployment entry point.
Re-exports the FastAPI app from api/server.py so the validator
can find the app at the expected `server.app:app` path.
"""
import os
import uvicorn
from api.server import app  # noqa: F401

def main():
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run("server.app:app", host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

__all__ = ["app", "main"]
