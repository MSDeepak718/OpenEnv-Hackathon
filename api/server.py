from fastapi import FastAPI, HTTPException
from env.moderation_env import ModerationEnv
from models import Action
from tasks.catalog import get_task_catalog

app = FastAPI(title="OpenEnv Moderation API", version="1.0.0")
env = ModerationEnv()


@app.post("/reset")
def reset():
    obs = env.reset()
    return obs.model_dump()


@app.post("/step")
def step(action: Action):
    try:
        obs, reward, done, info = env.step(action)
        return {
            "observation": obs.model_dump(),
            "reward": reward.model_dump(),
            "done": done,
            "info": info,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state")
def state():
    return {"status": "running"}


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
