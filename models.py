"""
Data models for the Incident Response Triage Environment.

Integrates with OpenEnv core types for framework compliance.
The environment simulates SRE incident response where agents must
triage, diagnose, and remediate production incidents.
"""

from typing import Dict, List, Optional

from openenv.core.env_server.types import Action, Observation
from pydantic import BaseModel, Field


# --- Observation & Action (inherit from OpenEnv core) ---

class LogEntry(BaseModel):
    timestamp: str
    level: str  # INFO, WARN, ERROR, FATAL
    service: str
    message: str


class Alert(BaseModel):
    name: str
    severity: str  # critical, warning, info
    source: str
    message: str
    fired_at: str


class TimelineEvent(BaseModel):
    timestamp: str
    event: str
    source: str


class IncidentTriageObservation(Observation):
    """Observation from the Incident Triage environment."""

    incident_id: str = Field(..., description="Unique incident identifier")
    timestamp: str = Field(..., description="When the incident was detected")
    severity_indicator: str = Field(..., description="Initial severity level (P1-P4)")
    title: str = Field(..., description="Incident title/summary")
    description: str = Field(..., description="Detailed incident description")
    affected_services: List[str] = Field(default_factory=list, description="Services impacted")
    metrics: Dict[str, List[float]] = Field(default_factory=dict, description="Time-series metrics (oldest → newest)")
    logs: List[LogEntry] = Field(default_factory=list, description="Structured log entries")
    alerts: List[Alert] = Field(default_factory=list, description="Fired monitoring alerts")
    timeline: List[TimelineEvent] = Field(default_factory=list, description="Chronological events")
    available_actions: List[str] = Field(default_factory=list, description="Valid remediation actions")
    step_number: int = Field(default=0, description="Current step in the episode")
    max_steps: int = Field(default=3, description="Maximum steps allowed")


class IncidentTriageAction(Action):
    """Action for the Incident Triage environment — the agent's triage response."""

    triage_priority: str = Field(..., description="Priority level: P1 (critical), P2 (high), P3 (medium), P4 (low)")
    root_cause_category: str = Field(..., description="Root cause: infrastructure, application, network, security, configuration, external")
    diagnosis: str = Field(default="", description="Free-text reasoning about the root cause")
    remediation: str = Field(..., description="Action: restart_service, scale_up, rollback_deploy, block_ip, update_config, failover, escalate, monitor")
    escalate_to: Optional[str] = Field(default=None, description="Optional team name to escalate to")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Agent's confidence in diagnosis (0.0-1.0)")


# --- Reward & State (standalone Pydantic models) ---

class Reward(BaseModel):
    score: float
    breakdown: Dict[str, float] = Field(default_factory=dict)
    feedback: str = ""
    penalties: List[str] = Field(default_factory=list)


class StepResult(BaseModel):
    observation: IncidentTriageObservation
    reward: Reward
    done: bool
    info: dict