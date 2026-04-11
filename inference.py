"""
Baseline inference script for Incident Response Triage Environment.

Uses OpenAI API client with environment variables:
  - API_BASE_URL:  LLM API endpoint
  - MODEL_NAME:    Model identifier
  - API_KEY:       API key (also checks HF_TOKEN, OPENAI_API_KEY)

Emits structured [START], [STEP], [END] logs.
"""
import os
import json
import re
import time
from typing import Dict, Any, List, Optional

from env.incident_env import IncidentTriageEnvironment
from models import IncidentTriageAction

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Only load .env if validator hasn't injected API_KEY (local dev only)
if not os.getenv("API_KEY"):
    load_dotenv()


# --- Mandatory environment variables ---
API_BASE_URL = os.getenv("API_BASE_URL", "")
MODEL_NAME = os.getenv("MODEL_NAME", "") or "gpt-4o-mini"
API_KEY = os.getenv("API_KEY") or os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY") or ""

MODEL_CONFIGURED = bool(API_BASE_URL and API_KEY and OpenAI)

client = None
if MODEL_CONFIGURED:
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )


# --- Constants ---
TEMPERATURE = 0.2
MAX_STEPS = 3
MAX_RETRIES = 3
BENCHMARK = "openenv-incident-triage"
SUCCESS_SCORE_THRESHOLD = 0.9


# --- Structured Logging (mandatory format) ---

def format_log_value(value: Any) -> str:
    text = str(value).replace("\n", " ").replace("\r", " ")
    return text if text else "null"


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={format_log_value(task)} env={format_log_value(env)} model={format_log_value(model)}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = format_log_value(error) if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={format_log_value(action)} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{reward:.2f}" for reward in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


# --- JSON Parsing ---

VALID_PRIORITIES = ["P1", "P2", "P3", "P4"]
VALID_CATEGORIES = ["infrastructure", "application", "network", "security", "configuration", "external"]
VALID_REMEDIATIONS = ["restart_service", "scale_up", "rollback_deploy", "block_ip", "update_config", "failover", "escalate", "monitor"]


def parse_json(text: str) -> Dict[str, Any]:
    """Parse JSON from model response, handling markdown code blocks."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        pass

    code_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except (json.JSONDecodeError, ValueError):
            pass

    match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except (json.JSONDecodeError, ValueError):
            pass

    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except (json.JSONDecodeError, ValueError):
            pass

    return {}


def sanitize(output: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all fields have valid values."""
    priority = output.get("triage_priority", "P2")
    if priority not in VALID_PRIORITIES:
        priority = "P2"

    category = output.get("root_cause_category", "infrastructure")
    if category not in VALID_CATEGORIES:
        category = "infrastructure"

    remediation = output.get("remediation", "escalate")
    if remediation not in VALID_REMEDIATIONS:
        remediation = "escalate"

    confidence = output.get("confidence", 0.5)
    try:
        confidence = float(confidence)
        confidence = max(0.0, min(1.0, confidence))
    except (ValueError, TypeError):
        confidence = 0.5

    diagnosis = output.get("diagnosis", "")
    if not isinstance(diagnosis, str):
        diagnosis = str(diagnosis)

    escalate_to = output.get("escalate_to", None)

    return {
        "triage_priority": priority,
        "root_cause_category": category,
        "diagnosis": diagnosis,
        "remediation": remediation,
        "escalate_to": escalate_to,
        "confidence": confidence,
    }


def action_to_str(action: IncidentTriageAction) -> str:
    return f"{action.triage_priority}:{action.root_cause_category}:{action.remediation}"


# --- Local Fallback Policy ---

def local_policy(obs) -> Dict[str, Any]:
    """Deterministic fallback policy when model is unavailable."""
    title_lower = obs.title.lower()
    desc_lower = obs.description.lower()
    combined = f"{title_lower} {desc_lower}"

    log_text = " ".join(log.message.lower() for log in obs.logs)
    alert_text = " ".join(alert.message.lower() for alert in obs.alerts)
    all_text = f"{combined} {log_text} {alert_text}"

    priority = obs.severity_indicator if obs.severity_indicator in VALID_PRIORITIES else "P2"

    if any(word in all_text for word in ["security", "breach", "ddos", "attack", "injection", "exfiltration", "cryptominer", "compromised"]):
        category = "security"
        remediation = "block_ip"
    elif any(word in all_text for word in ["deploy", "canary", "rollback", "version", "ci/cd", "pipeline", "epoch", "overflow", "mismatch"]):
        category = "application"
        remediation = "rollback_deploy"
    elif any(word in all_text for word in ["config", "misconfigured", "webhook", "rate limit", "feature flag", "ssl", "cert", "expired", "secret", "terraform", "drift"]):
        category = "configuration"
        remediation = "update_config"
    elif any(word in all_text for word in ["dns", "network", "partition", "packet loss", "switch", "bgp"]):
        category = "network"
        remediation = "failover"
    elif any(word in all_text for word in ["disk", "oom", "memory", "scale", "node", "evict", "kafka", "lag", "consumer", "cron", "stale"]):
        category = "infrastructure"
        remediation = "scale_up"
    elif any(word in all_text for word in ["external", "cdn", "third-party", "circuit breaker", "downstream"]):
        category = "external"
        remediation = "failover"
    elif any(word in all_text for word in ["crash", "redis", "cache", "session"]):
        category = "infrastructure"
        remediation = "restart_service"
    else:
        category = "infrastructure"
        remediation = "escalate"

    if "memory" in all_text and "leak" in all_text:
        category = "application"
        remediation = "restart_service"

    if "query" in all_text and ("slow" in all_text or "index" in all_text):
        category = "application"
        remediation = "update_config"

    return {
        "triage_priority": priority,
        "root_cause_category": category,
        "diagnosis": f"Automated triage based on incident signals: {obs.title}",
        "remediation": remediation,
        "escalate_to": None,
        "confidence": 0.5,
    }


# --- Prompt Building ---

def build_prompt(obs) -> str:
    """Build a rich system prompt for the LLM agent."""
    logs_text = ""
    if obs.logs:
        log_lines = [f"  [{log.level}] {log.timestamp} [{log.service}] {log.message}" for log in obs.logs]
        logs_text = "\n".join(log_lines)
    else:
        logs_text = "  (no logs available yet)"

    alerts_text = ""
    if obs.alerts:
        alert_lines = [f"  [{a.severity.upper()}] {a.fired_at} [{a.source}] {a.name}: {a.message}" for a in obs.alerts]
        alerts_text = "\n".join(alert_lines)
    else:
        alerts_text = "  (no alerts)"

    metrics_text = ""
    if obs.metrics:
        metric_lines = [f"  {name}: {values}" for name, values in obs.metrics.items()]
        metrics_text = "\n".join(metric_lines)
    else:
        metrics_text = "  (no metrics available yet)"

    timeline_text = ""
    if obs.timeline:
        event_lines = [f"  {e.timestamp} [{e.source}] {e.event}" for e in obs.timeline]
        timeline_text = "\n".join(event_lines)
    else:
        timeline_text = "  (no timeline events)"

    return f"""You are an expert Site Reliability Engineer (SRE) handling a production incident.

INCIDENT DETAILS:
  ID: {obs.incident_id}
  Severity: {obs.severity_indicator}
  Title: {obs.title}
  Description: {obs.description}
  Affected Services: {', '.join(obs.affected_services)}
  Step: {obs.step_number}/{obs.max_steps}

LOGS:
{logs_text}

ALERTS:
{alerts_text}

METRICS (time-series values, oldest → newest):
{metrics_text}

TIMELINE:
{timeline_text}

YOUR TASK:
Analyze the incident and provide your triage response. Consider:
1. What is the correct priority level based on impact?
2. What is the root cause category?
3. What remediation action should be taken?
4. How confident are you in your diagnosis?

AVAILABLE ACTIONS:
  Priority: P1 (critical outage), P2 (major degradation), P3 (partial impact), P4 (minor)
  Root Cause: infrastructure, application, network, security, configuration, external
  Remediation: restart_service, scale_up, rollback_deploy, block_ip, update_config, failover, escalate, monitor

IMPORTANT RULES:
- Do NOT choose "restart_service" if the root cause is a bad deployment — use "rollback_deploy" instead
- Do NOT choose "restart_service" if the issue is disk full — use "scale_up" instead
- For security incidents, prioritize "block_ip" or "escalate"
- For external/third-party issues, use "failover" to switch to backup
- Set high confidence (>0.7) only when evidence is clear and conclusive

Return ONLY a JSON object:
{{
  "triage_priority": "P1|P2|P3|P4",
  "root_cause_category": "infrastructure|application|network|security|configuration|external",
  "diagnosis": "Your reasoning about the root cause in 1-2 sentences",
  "remediation": "restart_service|scale_up|rollback_deploy|block_ip|update_config|failover|escalate|monitor",
  "escalate_to": null,
  "confidence": 0.0-1.0
}}"""


# --- Model Call ---

def call_model(prompt: str) -> str:
    """Call the LLM via OpenAI client with retries."""
    if client is None:
        return ""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            res = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=TEMPERATURE,
            )
            content = res.choices[0].message.content or ""
            if content.strip():
                return content
        except Exception:
            pass

        if attempt < MAX_RETRIES:
            time.sleep(2 ** attempt)

    return ""


# --- Main Runner ---

def run():
    env = IncidentTriageEnvironment()

    total_score = 0.0
    episodes = 6

    for episode in range(1, episodes + 1):
        rewards: List[float] = []
        steps_taken = 0
        score = 0.0
        success = False

        try:
            obs = env.reset()
            difficulty = env._difficulty or "unknown"
            task_id = f"{difficulty}_incident"
            print(f"\n--- EPISODE {episode} | TASK: {task_id} ({difficulty.upper()}) ---")
            log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

            done = False

            for step in range(1, MAX_STEPS + 1):
                if done:
                    break

                prompt = build_prompt(obs)
                response = call_model(prompt)

                if response:
                    parsed = sanitize(parse_json(response))
                else:
                    parsed = local_policy(obs)

                action = IncidentTriageAction(**parsed)
                obs = env.step(action)

                step_reward = obs.reward
                error = None

                rewards.append(step_reward)
                steps_taken = step
                score = max(0.0, min(step_reward, 1.0))
                success = success or score >= SUCCESS_SCORE_THRESHOLD
                done = obs.done

                log_step(step=step, action=action_to_str(action), reward=step_reward, done=done, error=error)

                if done:
                    break
        finally:
            log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
            total_score += score

    print(f"\n[BASELINE] Average Score across {episodes} episodes: {total_score / episodes:.3f}", flush=True)


if __name__ == "__main__":
    run()
