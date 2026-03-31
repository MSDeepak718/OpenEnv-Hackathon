from pydantic import BaseModel
from typing import List

class Observation(BaseModel):
    content: str
    user_history: List[str]
    previous_actions: List[str]

class Action(BaseModel):
    label: str        # safe | toxic | hate | spam
    severity: str     # low | medium | high
    decision: str     # allow | warn | remove | ban

class Reward(BaseModel):
    score: float
    feedback: str

class StepResult(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: dict