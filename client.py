"""Incident Response Triage Environment Client."""

from typing import Dict

from openenv.core import EnvClient
from openenv.core.client_types import StepResult
from openenv.core.env_server.types import State

from .models import IncidentTriageAction, IncidentTriageObservation


class IncidentTriageEnv(EnvClient[IncidentTriageAction, IncidentTriageObservation, State]):
    """
    Client for the Incident Response Triage Environment.

    Maintains a persistent WebSocket connection to the environment server
    for efficient multi-step interactions with lower latency.

    Example:
        >>> from client import IncidentTriageEnv, IncidentTriageAction
        >>>
        >>> env = IncidentTriageEnv(base_url="http://localhost:7860")
        >>> result = env.reset()
        >>> print(f"Incident: {result.observation.title}")
        >>>
        >>> action = IncidentTriageAction(
        ...     triage_priority="P1",
        ...     root_cause_category="application",
        ...     diagnosis="Bad deploy causing crash loop",
        ...     remediation="rollback_deploy",
        ...     confidence=0.9
        ... )
        >>> result = env.step(action)
        >>> print(f"Score: {result.observation.reward}")
        >>> env.close()
    """

    def _step_payload(self, action: IncidentTriageAction) -> Dict:
        """Convert action to JSON payload for step message."""
        return action.model_dump()

    def _parse_result(self, payload: Dict) -> StepResult[IncidentTriageObservation]:
        """Parse server response into StepResult."""
        obs_data = payload.get("observation", {})
        observation = IncidentTriageObservation(**obs_data)

        return StepResult(
            observation=observation,
            reward=payload.get("reward"),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict) -> State:
        """Parse server response into State object."""
        return State(
            episode_id=payload.get("episode_id"),
            step_count=payload.get("step_count", 0),
        )
