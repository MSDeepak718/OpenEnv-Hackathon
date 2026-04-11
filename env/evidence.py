"""
Evidence revelation engine — controls what information is available at each step.
Progressively reveals more evidence as the agent takes actions.
"""
from typing import List
from models import LogEntry, Alert, TimelineEvent


def get_evidence_for_step(task: dict, step: int) -> dict:
    """
    Return the evidence available up to (and including) the given step.
    Accumulates logs, alerts, timeline events, and metrics from all
    steps up to the current one.
    """
    metrics = {}
    logs = []
    alerts = []
    timeline = []

    metrics_by_step = task.get("metrics_by_step", {})
    logs_by_step = task.get("logs_by_step", {})
    alerts_by_step = task.get("alerts_by_step", {})
    timeline_by_step = task.get("timeline_by_step", {})

    for s in range(1, step + 1):
        # Merge metrics (latest step values override)
        if s in metrics_by_step:
            for key, values in metrics_by_step[s].items():
                metrics[key] = values

        # Accumulate logs
        if s in logs_by_step:
            for log_data in logs_by_step[s]:
                logs.append(LogEntry(**log_data))

        # Accumulate alerts
        if s in alerts_by_step:
            for alert_data in alerts_by_step[s]:
                alerts.append(Alert(**alert_data))

        # Accumulate timeline
        if s in timeline_by_step:
            for event_data in timeline_by_step[s]:
                timeline.append(TimelineEvent(**event_data))

    return {
        "metrics": metrics,
        "logs": logs,
        "alerts": alerts,
        "timeline": timeline,
    }


def get_available_actions(step: int, max_steps: int) -> List[str]:
    """Return the list of actions available to the agent at this step."""
    actions = [
        "restart_service",
        "scale_up",
        "rollback_deploy",
        "block_ip",
        "update_config",
        "failover",
        "escalate",
        "monitor",
    ]
    return actions
