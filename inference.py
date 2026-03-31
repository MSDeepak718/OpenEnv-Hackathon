import os
import json
import re
import time
from typing import Dict, Any
from dotenv import load_dotenv

from openai import OpenAI
from env.moderation_env import ModerationEnv
from schemas import Action

load_dotenv()


# =========================
# ENV VARIABLES
# =========================
API_BASE_URL = os.getenv("API_BASE_URL")
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME")

if not API_BASE_URL or not HF_TOKEN or not MODEL_NAME:
    raise ValueError("Missing required environment variables: API_BASE_URL, HF_TOKEN, MODEL_NAME")


# =========================
# OPENAI CLIENT
# =========================
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)


TEMPERATURE = 0.2
EPISODES = 5      # small for <20min runtime
MAX_RETRIES = 3   # retry on transient API failures


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
            print(f"[WARNING] Empty response on attempt {attempt}/{MAX_RETRIES}")
        except Exception as e:
            print(f"[WARNING] Model API error on attempt {attempt}/{MAX_RETRIES}: {e}")

        if attempt < MAX_RETRIES:
            time.sleep(2 ** attempt)  # exponential backoff: 2s, 4s

    return ""


# =========================
# RUN ONE EPISODE
# =========================
def run_episode(env) -> float:
    obs = env.reset()
    done = False
    final_score = 0.0

    while not done:
        prompt = build_prompt(obs)
        response = call_model(prompt)

        if not response:
            print("[ERROR] Model failed after all retries — scoring episode as 0.0")
            return 0.0

        parsed = sanitize(parse_json(response))
        action = Action(**parsed)

        obs, reward, done, _ = env.step(action)
        final_score = reward.score

    return final_score


# =========================
# MAIN
# =========================
def run():
    env = ModerationEnv()
    scores = []
    failed = 0

    print("Running Inference...\n")

    for i in range(EPISODES):
        score = run_episode(env)
        scores.append(score)
        if score == 0.0:
            failed += 1
        print(f"Episode {i+1}: {score:.3f}")

    avg_score = sum(scores) / len(scores)

    print("\n======================")
    print(f"Final Average Score: {avg_score:.4f}")
    if failed:
        print(f"[WARNING] {failed}/{EPISODES} episodes scored 0.0 (check API key / rate limits)")
    print("======================")


if __name__ == "__main__":
    run()