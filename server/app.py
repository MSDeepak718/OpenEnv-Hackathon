"""
FastAPI application for the Incident Response Triage Environment.

Uses OpenEnv core's create_app() for framework-compliant HTTP + WebSocket endpoints.

Endpoints:
    - POST /reset: Reset the environment
    - POST /step: Execute an action
    - GET /state: Get current environment state
    - GET /schema: Get action/observation schemas
    - WS /ws: WebSocket endpoint for persistent sessions
    - GET /health: Health check

Usage:
    # Development:
    uvicorn server.app:app --reload --host 0.0.0.0 --port 7860

    # Production:
    uvicorn server.app:app --host 0.0.0.0 --port 7860
"""

try:
    from openenv.core.env_server.http_server import create_app
except ImportError as e:
    raise ImportError(
        "openenv-core is required. Install with: pip install openenv-core>=0.2.2"
    ) from e

try:
    from models import IncidentTriageAction, IncidentTriageObservation
except ImportError:
    from ..models import IncidentTriageAction, IncidentTriageObservation

from env.incident_env import IncidentTriageEnvironment


# Create app using OpenEnv core's create_app for full spec compliance
app = create_app(
    IncidentTriageEnvironment,
    IncidentTriageAction,
    IncidentTriageObservation,
    env_name="incident_triage",
    max_concurrent_envs=1,
)


def main(host: str = "0.0.0.0", port: int = 7860):
    """Entry point for running the server directly."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
