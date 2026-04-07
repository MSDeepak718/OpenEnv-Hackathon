import os
import json
import re
import time
from typing import Dict, Any

from env.moderation_env import ModerationEnv
from schemas import Action

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
API_BASE_URL = os.getenv("API_BASE_URL")
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME")

MODEL_CONFIGURED = bool(API_BASE_URL and HF_TOKEN and MODEL_NAME and OpenAI)


# =========================
# OPENAI CLIENT
# =========================
client = None
if MODEL_CONFIGURED:
    client = OpenAI(
        base_url=API_BASE_URL,
        api_key=HF_TOKEN,
    )


TEMPERATURE = 0.2
EPISODES = 5      # small for <20min runtime
MAX_RETRIES = 3   # retry on transient API failures


def emit_log(event: str, payload: Dict[str, Any]) -> None:
    print(f"[{event}] {json.dumps(payload, separators=(',', ':'))}", flush=True)


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


# =========================
# RUN ONE EPISODE
# =========================
def run_episode(env, episode: int) -> float:
    obs = env.reset()
    done = False
    final_score = 0.0
    step = 0

    while not done:
        step += 1
        prompt = build_prompt(obs)
        response = call_model(prompt)
        source = "llm" if response else "fallback"

        if response:
            parsed = sanitize(parse_json(response))
        else:
            parsed = local_policy(obs)

        action = Action(**parsed)

        obs, reward, done, _ = env.step(action)
        final_score = reward.score
        emit_log("STEP", {
            "episode": episode,
            "step": step,
            "label": action.label,
            "severity": action.severity,
            "decision": action.decision,
            "score": round(final_score, 4),
            "done": done,
            "source": source,
        })

    return final_score


# =========================
# MAIN
# =========================
def run():
    env = ModerationEnv()
    scores = []
    failed = 0

    emit_log("START", {
        "episodes": EPISODES,
        "model_name": MODEL_NAME or "",
        "api_base_url": API_BASE_URL or "",
        "model_configured": MODEL_CONFIGURED,
    })

    for i in range(EPISODES):
        score = run_episode(env, i + 1)
        scores.append(score)
        if score == 0.0:
            failed += 1

    avg_score = sum(scores) / len(scores)

    emit_log("END", {
        "episodes": EPISODES,
        "average_score": round(avg_score, 4),
        "failed": failed,
    })


if __name__ == "__main__":
    run()
