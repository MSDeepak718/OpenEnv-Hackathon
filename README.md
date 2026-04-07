---
title: OpenEnv Moderation
emoji: 🛡️
colorFrom: red
colorTo: yellow
sdk: docker
pinned: false
tags:
  - openenv
---

# OpenEnv — AI Content Moderation Environment

An **OpenEnv-compatible** reinforcement learning environment where an LLM agent acts as an AI content moderator, classifying user-generated content and deciding on the appropriate enforcement action.

> Built for the OpenEnv Hackathon 

---

## Environment Description & Motivation

Content moderation at scale is one of the hardest problems in platform safety. Human moderators are expensive and prone to fatigue; rule-based filters miss nuance. This environment challenges an LLM agent to **reason about context, user history, and intent** to make consistent, policy-aligned moderation decisions — mimicking real-world trust & safety workflows.

---

## Observation Space

Each observation is a JSON object with three fields:

| Field | Type | Description |
|---|---|---|
| `content` | `string` | The user-generated message/post to be moderated |
| `user_history` | `list[string]` | Previous violations or infractions by this user |
| `previous_actions` | `list[string]` | Actions taken in prior steps of the current episode |

**Example:**
```json
{
  "content": "I'll find out where you live and make you regret this",
  "user_history": ["previous warning"],
  "previous_actions": []
}
```

---

## Action Space

The agent must return a JSON object with three fields:

| Field | Type | Values |
|---|---|---|
| `label` | `string` | `safe` · `toxic` · `hate` · `spam` |
| `severity` | `string` | `low` · `medium` · `high` |
| `decision` | `string` | `allow` · `warn` · `remove` · `ban` |

**Example:**
```json
{
  "label": "hate",
  "severity": "high",
  "decision": "ban"
}
```

---

## Task Descriptions

| Difficulty | Content Type | History | Expected Challenge |
|---|---|---|---|
| **Easy** | Explicit threats, hate speech, clear spam | Prior violations (1+) | Direct policy violation — unambiguous |
| **Medium** | Frustration expressions, mild toxicity, subtle spam | None or minimal | Distinguish venting vs. genuine toxicity |
| **Hard** | Borderline hate speech, coded threats | Multiple strikes (3+) | Escalation logic + context-aware severity |

Each difficulty has **4 randomized task variants** sampled per episode.

### Scoring (per episode)

| Match | Points |
|---|---|
| Correct `label` | **+0.3** |
| Correct `severity` | **+0.3** |
| Correct `decision` | **+0.4** |
| `ban` required but `allow` given | **−0.5** (clamped to 0) |

Score range: `0.0` (complete miss) → `1.0` (perfect match)

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/reset` | Reset episode, returns first `Observation` |
| `POST` | `/step` | Submit `Action`, returns `Observation + Reward + done` |
| `GET` | `/state` | Environment status |
| `GET` | `/health` | Health check (returns 200) |

---

## Setup & Usage

### Local (via `.venv`)

```bash
# Install dependencies
pip install uv
uv sync

# Set environment variables
cp .env.example .env
# Edit .env with your API key

# Run the API server
uvicorn api.server:app --host 0.0.0.0 --port 7860

# Run inference agent
python inference.py
```

### Docker

```bash
# Build
docker build -t openenv-moderation .

# Run (inject env vars)
docker run -p 7860:7860 \
  -e API_BASE_URL=https://api.groq.com/openai/v1 \
  -e MODEL_NAME=llama-3.3-70b-versatile \
  -e API_KEY=your_token_here \
  openenv-moderation
```

### HF Space Secrets

Set the following **Secrets** in your HF Space settings:

| Key | Value |
|---|---|
| `API_BASE_URL` | `https://api.groq.com/openai/v1` |
| `MODEL_NAME` | `llama-3.3-70b-versatile` |
| `API_KEY` | Your Groq API key |

---

## Baseline Scores

Tested with `llama-3.3-70b-versatile` via Groq API (5 episodes):

| Run | Ep 1 | Ep 2 | Ep 3 | Ep 4 | Ep 5 | **Avg** |
|---|---|---|---|---|---|---|
| Run 1 | 1.000 | 0.700 | 0.700 | 1.000 | 1.000 | **0.880** |
| Run 2 | 0.700 | 0.700 | 0.700 | 1.000 | 1.000 | **0.820** |
| Run 3 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | **1.000** |

> Typical baseline: **0.82 – 1.00** depending on Groq API rate limits.

---

## Project Structure

```
.
├── api/
│   └── server.py          # FastAPI server (OpenEnv endpoints)
├── env/
│   └── moderation_env.py  # RL environment (reset / step)
├── tasks/
│   ├── easy.py            # 4 easy task variants
│   ├── medium.py          # 4 medium task variants
│   ├── hard.py            # 4 hard task variants
│   └── grader.py          # Reward / scoring logic
├── schemas.py             # Pydantic models: Observation, Action, Reward
├── inference.py           # LLM agent runner
├── openenv.yaml           # OpenEnv spec config
├── Dockerfile             # Container definition
└── pyproject.toml         # Python project & dependencies
```

---

## OpenEnv Config (`openenv.yaml`)

```yaml
name: moderation-env
description: AI Content Moderation Environment
version: 1.0
endpoints:
  reset: /reset
  step: /step
  state: /state
models:
  observation: Observation
  action: Action
  reward: Reward
```
