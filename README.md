---
title: OpenEnv Incident Triage
emoji: 🚨
colorFrom: red
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
---

# OpenEnv — Incident Response Triage Environment

An **OpenEnv-compatible** reinforcement learning environment where an LLM agent acts as a **Site Reliability Engineer (SRE)**, triaging production incidents by analyzing logs, metrics, alerts, and timelines to diagnose root causes and choose appropriate remediation actions.

Built using the `openenv-core` framework — inherits from `Environment`, uses `create_app()`, supports HTTP + WebSocket.

> Built for the OpenEnv Hackathon

---

## Environment Description & Motivation

**Incident response triage** is one of the most critical, high-stakes tasks in modern software operations. When production systems fail, SRE teams must rapidly:

1. **Assess severity** — Is this a P1 total outage or a P4 minor issue?
2. **Identify root cause** — Infrastructure failure? Security breach? Bad deploy?
3. **Choose remediation** — Rollback, restart, scale up, or block the attacker?
4. **Calibrate confidence** — Is the evidence conclusive or misleading?

This environment simulates that workflow with **multi-step episodes** where new evidence is progressively revealed, forcing the agent to update its diagnosis as more information becomes available. Incidents feature realistic scenarios including cascading Redis failures, DDoS attacks masking data breaches, cryptominer deployments via compromised CI/CD pipelines, and epoch timestamp overflow bugs.

**Why this domain?**
- Every tech company runs 24/7 incident response — this is a real, unsolved problem
- Requires multi-step reasoning, not just classification
- Natural reward shaping — partial credit for correct triage even with wrong remediation
- Hard tasks genuinely challenge frontier models with misleading signals

---

## Observation Space

Each observation provides the agent with progressive evidence about an incident:

| Field | Type | Description |
|---|---|---|
| `incident_id` | `string` | Unique incident identifier |
| `timestamp` | `string` | When the incident was detected |
| `severity_indicator` | `string` | Initial severity (P1–P4) |
| `title` | `string` | Incident title/summary |
| `description` | `string` | Detailed incident description |
| `affected_services` | `list[string]` | Services impacted |
| `metrics` | `dict[string, list[float]]` | Time-series metrics (oldest → newest) |
| `logs` | `list[LogEntry]` | Structured log entries with timestamps |
| `alerts` | `list[Alert]` | Fired monitoring alerts |
| `timeline` | `list[TimelineEvent]` | Chronological incident events |
| `available_actions` | `list[string]` | Valid remediation actions |
| `step_number` | `int` | Current step in the episode |
| `max_steps` | `int` | Maximum steps allowed |
| `done` | `bool` | Whether the episode is complete |
| `reward` | `float` | Score for the last action (0.0–1.0) |

**Example (step 1):**
```json
{
  "incident_id": "INC-1001",
  "severity_indicator": "P1",
  "title": "API Gateway — 100% 5xx After Deploy",
  "affected_services": ["api-gateway", "web-frontend"],
  "metrics": {"error_rate_pct": [2.0, 5.0, 98.0, 100.0]},
  "logs": [
    {"level": "FATAL", "service": "api-gateway", "message": "CrashLoopBackOff: 12 restarts"}
  ],
  "alerts": [
    {"name": "HighErrorRate", "severity": "critical", "message": "error rate > 95%"}
  ],
  "done": false,
  "reward": 0.0
}
```

---

## Action Space

The agent must return a structured triage response:

| Field | Type | Values |
|---|---|---|
| `triage_priority` | `string` | `P1` (critical) · `P2` (high) · `P3` (medium) · `P4` (low) |
| `root_cause_category` | `string` | `infrastructure` · `application` · `network` · `security` · `configuration` · `external` |
| `diagnosis` | `string` | Free-text reasoning about the root cause |
| `remediation` | `string` | `restart_service` · `scale_up` · `rollback_deploy` · `block_ip` · `update_config` · `failover` · `escalate` · `monitor` |
| `escalate_to` | `string?` | Optional team name to escalate to |
| `confidence` | `float` | Agent's confidence (0.0–1.0) |

**Example:**
```json
{
  "triage_priority": "P1",
  "root_cause_category": "application",
  "diagnosis": "CrashLoopBackOff caused by bad deploy v2.14",
  "remediation": "rollback_deploy",
  "escalate_to": null,
  "confidence": 0.9
}
```

---

## Task Descriptions

| Difficulty | # Variants | Incident Types | Steps | Expected Challenge |
|---|---|---|---|---|
| **Easy** | 8 | Bad deploys, disk full, SSL expired, OOM, CDN outage, Redis crash, webhook misconfig, DNS failure | 1 | Clear signals — unambiguous root cause |
| **Medium** | 8 | Slow DB queries, memory leaks, rate limiter misconfig, Kafka lag, cron failures, circuit breaker cascades, feature flag bugs, image pull failures | 1–2 | Requires correlating 2–3 signals |
| **Hard** | 8 | DDoS masking breach, cascading Redis, network partition, cryptominer via CI/CD, replication drift, canary poisoning, epoch overflow, Terraform state corruption | 2–3 | Misleading initial signals, progressive evidence revelation |

### Scoring (5-component grading)

| Component | Weight | Scoring |
|---|---|---|
| Triage Priority | 15–25% | Exact = 100%, off-by-1 = 50%, off-by-2+ = 0% |
| Root Cause Category | 25–30% | Exact = 100%, related = 40%, wrong = 0% |
| Remediation | 25–30% | Exact = 100%, partial = 50%, harmful = **−15% penalty** |
| Confidence Calibration | 10% | Rewards accurate self-assessment |
| Diagnosis Quality | 15% | Keyword matching against expected reasoning |

**Penalties:** `−0.15` harmful remediation, `−0.05` overconfident wrong answer

Score range: `0.01` → `0.99`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/reset` | Reset episode, returns initial `Observation` |
| `POST` | `/step` | Submit `Action`, returns `Observation + reward + done` |
| `GET` | `/state` | Episode state (episode_id, step_count) |
| `GET` | `/schema` | JSON schemas for action/observation/state |
| `GET` | `/metadata` | Environment metadata and README |
| `GET` | `/health` | Health check |
| `WS` | `/ws` | WebSocket for persistent sessions |

---

## Setup & Usage

### Local

```bash
pip install uv && uv sync
cp .env.example .env  # Edit with your API credentials
uvicorn server.app:app --host 0.0.0.0 --port 7860
python inference.py
```

### Docker

```bash
docker build -t openenv-incident-triage .
docker run -p 7860:7860 \
  -e API_BASE_URL=https://api.openai.com/v1 \
  -e MODEL_NAME=gpt-4o \
  -e HF_TOKEN=your_token_here \
  openenv-incident-triage
```

### Environment Variables

| Key | Description |
|---|---|
| `API_BASE_URL` | LLM API endpoint |
| `MODEL_NAME` | Model identifier |
| `HF_TOKEN` | API key |

---

## Baseline Scores

Local fallback policy (deterministic, no LLM):

| Difficulty | Avg Score |
|---|---|
| Easy | ~0.70 |
| Medium | ~0.45 |
| Hard | ~0.25 |
| **Overall** | **~0.47** |

With LLM (via API): **~0.90** average

---

## Project Structure

```
.
├── server/
│   ├── __init__.py        # Module re-export
│   └── app.py             # FastAPI app via OpenEnv create_app()
├── env/
│   ├── incident_env.py    # Environment (inherits from openenv Environment)
│   └── evidence.py        # Progressive evidence revelation engine
├── tasks/
│   ├── easy.py            # 8 easy incident variants
│   ├── medium.py          # 8 medium incident variants
│   ├── hard.py            # 8 hard incident variants
│   ├── grader.py          # 5-component continuous grading system
│   └── catalog.py         # Task catalog registry
├── api/
│   └── server.py          # Fallback API server
├── models.py              # Pydantic models (extends openenv Action/Observation)
├── client.py              # EnvClient for WebSocket connections
├── __init__.py            # Package exports
├── inference.py           # LLM agent runner (OpenAI Client)
├── openenv.yaml           # OpenEnv spec manifest (spec_version: 1)
├── Dockerfile             # Container with HEALTHCHECK
├── pyproject.toml         # Dependencies & build config
└── validate.sh            # Pre-submission validator
```

---

## OpenEnv Config (`openenv.yaml`)

```yaml
spec_version: 1
name: incident_triage
type: space
runtime: fastapi
app: server.app:app
port: 7860
```
