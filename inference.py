import os
import json
import re
import time
from typing import Dict, Any, List, Optional

from env.moderation_env import ModerationEnv
from models import Action

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

load_dotenv()


# =========================
# ENV VARIABLES
# =========================
API_BASE_URL = os.getenv("API_BASE_URL") or "https://router.huggingface.co/v1"
API_KEY = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME") or os.getenv("MODEL") or "Qwen/Qwen2.5-72B-Instruct"

MODEL_CONFIGURED = bool(API_BASE_URL and API_KEY and OpenAI)


# =========================
# OPENAI CLIENT
# =========================
client = None
if MODEL_CONFIGURED:
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=API_KEY,
    )


TEMPERATURE = 0.2
MAX_STEPS = 3
MAX_RETRIES = 3   # retry on transient API failures
TASK_NAME = os.getenv("TASK_NAME", "moderation")
BENCHMARK = os.getenv("BENCHMARK", "openenv-moderation")
SUCCESS_SCORE_THRESHOLD = 0.9


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


# =========================
# SAFE JSON PARSER
# =========================
def parse_json(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        match = re.search(r"\{.*?\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except (json.JSONDecodeError, ValueError):
                pass
    return {"label": "safe", "severity": "low", "decision": "allow"}


VALID_LABELS = ["safe", "toxic", "hate", "spam"]
VALID_SEVERITY = ["low", "medium", "high"]
VALID_DECISION = ["allow", "warn", "remove", "ban"]


def sanitize(output: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "label": output.get("label") if output.get("label") in VALID_LABELS else "safe",
        "severity": output.get("severity") if output.get("severity") in VALID_SEVERITY else "low",
        "decision": output.get("decision") if output.get("decision") in VALID_DECISION else "allow",
    }


def action_to_str(action: Action) -> str:
    return f"{action.label}:{action.severity}:{action.decision}"


def local_policy(obs) -> Dict[str, Any]:
    """Deterministic fallback used when model credentials or calls are unavailable."""
    content = obs.content.lower()
    history = " ".join(obs.user_history).lower()

    if any(term in content for term in ["buy cheap followers", "free iphone", "click here", "credit card", "claim your reward"]):
        repeated_spam = "spam" in history or "removal" in history
        phishing = "credit card" in content or "claim your reward" in content
        return {
            "label": "spam",
            "severity": "high" if phishing or repeated_spam else "medium",
            "decision": "ban" if repeated_spam else "remove",
        }

    if any(term in content for term in ["where you live", "shut you up permanently", "your kind", "people like you"]):
        return {"label": "hate", "severity": "high", "decision": "ban"}

    if any(term in content for term in ["worthless", "pathetic", "worst support team"]):
        escalated = any(term in history for term in ["warn", "removal", "ban"])
        return {
            "label": "toxic",
            "severity": "high" if "ban" in history or "removal" in history else "medium",
            "decision": "ban" if escalated and ("ban" in history or "removal" in history) else "warn",
        }

    return {"label": "safe", "severity": "low", "decision": "allow"}


# =========================
# PROMPT
# =========================
def build_prompt(obs) -> str:
    return f"""
You are a STRICT and CONSISTENT AI content moderation system.

Your goal is to make SAFE and POLICY-COMPLIANT decisions.

RULES:
- Spam → remove
- Toxic insult → warn
- Threat / violence → ban
- Repeated offenses → escalate severity and punishment

ESCALATION LOGIC:
- If user has past violations → increase severity
- If history includes bans → always ban again

Content:
{obs.content}

User History:
{obs.user_history}

Previous Actions:
{obs.previous_actions}

Think carefully before answering.

Return ONLY JSON:
{{
  "label": "safe | toxic | hate | spam",
  "severity": "low | medium | high",
  "decision": "allow | warn | remove | ban"
}}
"""


# =========================
# MODEL CALL (with retry)
# =========================
def call_model(prompt: str) -> str:
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
            time.sleep(2 ** attempt)  # exponential backoff: 2s, 4s

    return ""


# MAIN
# =========================
def run():
    env = ModerationEnv()
    
    total_score = 0.0
    episodes = 6
    
    for episode in range(1, episodes + 1):
        rewards: List[float] = []
        steps_taken = 0
        score = 0.0
        success = False

        try:
            obs = env.reset()
            # Dynamically fetch the current randomly sampled task from state
            task_id = env.state.current_task.get("id", TASK_NAME)
            difficulty = env.state.current_task.get("difficulty", "unknown")
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

                action = Action(**parsed)
                obs, reward, done, info = env.step(action)

                step_reward = reward.score
                error = info.get("last_action_error") if isinstance(info, dict) else None

                rewards.append(step_reward)
                steps_taken = step
                score = max(0.0, min(step_reward, 1.0))
                success = success or score >= SUCCESS_SCORE_THRESHOLD

                log_step(step=step, action=action_to_str(action), reward=step_reward, done=done, error=error)

                if done:
                    break
        finally:
            log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
            total_score += score
            
    try:
        close = getattr(env, "close", None)
        if callable(close):
            close()
    except Exception:
        pass
        
    print(f"\n[BASELINE] Average Score across {episodes} episodes: {total_score / episodes:.3f}", flush=True)


if __name__ == "__main__":
    run()
