"""
Incident Response Triage Environment Implementation.

Integrates with OpenEnv core framework. Simulates production incident
investigation where an SRE agent must triage, diagnose, and remediate.
Multi-step episodes with progressive evidence revelation.
"""

import random
from typing import Optional
from uuid import uuid4

from openenv.core.env_server.interfaces import Environment
from openenv.core.env_server.types import State

try:
    from models import IncidentTriageAction, IncidentTriageObservation
except ImportError:
    from ..models import IncidentTriageAction, IncidentTriageObservation

from env.evidence import get_evidence_for_step, get_available_actions
from tasks.easy import get_easy_task
from tasks.medium import get_medium_task
from tasks.hard import get_hard_task
from tasks.grader import grade_easy, grade_medium, grade_hard


class IncidentTriageEnvironment(Environment):
    """
    Incident Response Triage environment for multi-step incident diagnosis.

    Each episode presents a production incident. The agent analyzes logs,
    metrics, alerts, and timelines to triage priority, identify root cause,
    and choose remediation. Evidence is progressively revealed across steps.

    Design:
    - Multi-step episodes (1-3 steps): progressive evidence revelation
    - 3 difficulty tiers: easy (8 variants), medium (8), hard (8)
    - 5-component grading: priority, root cause, remediation, confidence, diagnosis
    - Penalty system: harmful actions and overconfident wrong answers penalized
    - Clean reset: each episode is fully independent

    Example:
        >>> env = IncidentTriageEnvironment()
        >>> obs = env.reset()
        >>> print(obs.title)  # "API Gateway — 100% 5xx After Deploy"
        >>> action = IncidentTriageAction(
        ...     triage_priority="P1",
        ...     root_cause_category="application",
        ...     remediation="rollback_deploy",
        ...     confidence=0.9
        ... )
        >>> obs = env.step(action)
        >>> print(obs.reward)  # 0.95
    """

    SUPPORTS_CONCURRENT_SESSIONS: bool = True

    def __init__(self):
        """Initialize the incident triage environment."""
        self._state = State(episode_id=str(uuid4()), step_count=0)
        self.current_task = None
        self.step_count = 0
        self.max_steps = 3
        self.history = []
        self.best_score = 0.0
        self._difficulty = None

    def reset(
        self,
        difficulty: Optional[str] = None,
        episode_id: Optional[str] = None,
    ) -> IncidentTriageObservation:
        """
        Reset the environment and start a new incident episode.

        Args:
            difficulty: Optional difficulty level (easy, medium, hard).
                       If None, randomly sampled.
            episode_id: Optional episode identifier.

        Returns:
            IncidentTriageObservation with initial incident data and evidence.
        """
        self.step_count = 0
        self.history = []
        self.best_score = 0.0

        self._difficulty = difficulty or random.choice(["easy", "medium", "hard"])

        if self._difficulty == "easy":
            self.current_task = get_easy_task()
        elif self._difficulty == "medium":
            self.current_task = get_medium_task()
        else:
            self.current_task = get_hard_task()

        self._state = State(
            episode_id=episode_id or str(uuid4()),
            step_count=0,
        )

        return self._build_observation(step=1, reward=0.0, done=False)

    def _build_observation(self, step: int, reward: float, done: bool) -> IncidentTriageObservation:
        """Build observation with evidence revealed up to the current step."""
        evidence = get_evidence_for_step(self.current_task, step)
        available = get_available_actions(step, self.max_steps)

        return IncidentTriageObservation(
            incident_id=self.current_task["incident_id"],
            timestamp=self.current_task["timestamp"],
            severity_indicator=self.current_task["severity_indicator"],
            title=self.current_task["title"],
            description=self.current_task["description"],
            affected_services=self.current_task["affected_services"],
            metrics=evidence["metrics"],
            logs=evidence["logs"],
            alerts=evidence["alerts"],
            timeline=evidence["timeline"],
            available_actions=available,
            step_number=step,
            max_steps=self.max_steps,
            done=done,
            reward=reward,
        )

    def step(self, action: IncidentTriageAction) -> IncidentTriageObservation:
        """
        Execute an action and return the next observation.

        The agent's triage response is graded against the expected answer.
        Additional evidence may be revealed in the next observation.

        Args:
            action: IncidentTriageAction with the agent's triage response.

        Returns:
            IncidentTriageObservation with updated evidence, reward, and done flag.
        """
        self.step_count += 1
        self._state.step_count = self.step_count
        next_evidence_step = min(self.step_count + 1, self.max_steps)

        # Grade the action based on difficulty
        if self._difficulty == "easy":
            score, feedback = grade_easy(self.current_task, action)
        elif self._difficulty == "medium":
            score, feedback = grade_medium(self.current_task, action)
        else:
            score, feedback = grade_hard(self.current_task, action)

        self.best_score = max(self.best_score, score)

        # Determine if episode is done
        done = score > 0.9 or self.step_count >= self.max_steps

        # Track action in history
        action_record = action.model_dump()
        action_record["step"] = self.step_count
        action_record["score"] = score
        action_record["feedback"] = feedback
        self.history.append(action_record)

        return self._build_observation(
            step=next_evidence_step,
            reward=score,
            done=done,
        )

    @property
    def state(self) -> State:
        """
        Get the current environment state.

        Returns:
            Current State with episode_id and step_count.
        """
        return self._state
