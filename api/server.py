"""
Fallback API server for the Incident Response Triage Environment.

Used when the OpenEnv core create_app is not available or for direct
endpoint testing. The primary server is in server/app.py.
"""
from fastapi import FastAPI, HTTPException
from env.incident_env import IncidentTriageEnvironment
from models import IncidentTriageAction
from tasks.catalog import get_task_catalog

app = FastAPI(title="OpenEnv Incident Response Triage API", version="1.0.0")
env = IncidentTriageEnvironment()


@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.model_dump()


@app.post("/step")
def step(action: IncidentTriageAction):
    try:
        obs = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": obs.reward,
            "done": obs.done,
            "info": {},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state")
def state():
    s = env.state
    return {"episode_id": s.episode_id, "step_count": s.step_count}


@app.get("/tasks")
def tasks():
    return {"tasks": get_task_catalog()}


@app.get("/grader")
def grader():
    return {
        "graders": [
            {"task_id": task["id"], "grader": task["grader"]}
            for task in get_task_catalog()
        ]
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
