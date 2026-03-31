import random
from typing import Tuple
from schemas import Observation, Action, Reward

from tasks.easy import get_easy_task
from tasks.medium import get_medium_task
from tasks.hard import get_hard_task
from tasks.grader import grade_action


class ModerationEnv:
    def __init__(self):
        self.current_task = None
        self.step_count = 0
        self.max_steps = 3
        self.history = []

    def reset(self) -> Observation:
        self.step_count = 0
        self.history = []

        # Random task difficulty
        difficulty = random.choice(["easy", "medium", "hard"])

        if difficulty == "easy":
            self.current_task = get_easy_task()
        elif difficulty == "medium":
            self.current_task = get_medium_task()
        else:
            self.current_task = get_hard_task()

        return self._get_observation()

    def _get_observation(self) -> Observation:
        return Observation(
            content=self.current_task["content"],
            user_history=self.current_task["history"],
            previous_actions=[]
        )

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, dict]:
        self.step_count += 1

        # Evaluate action
        score, feedback = grade_action(self.current_task, action)

        reward = Reward(score=score, feedback=feedback)

        done = score > 0.9 or self.step_count >= self.max_steps

        self.history.append(action.model_dump())
        
        obs = Observation(
            content=self.current_task["content"],
            user_history=self.current_task["history"],
            previous_actions=[str(a) for a in self.history]
        )

        return obs, reward, done, {}