import random
from typing import Tuple
from models import Observation, Action, Reward, State

from tasks.easy import get_easy_task
from tasks.medium import get_medium_task
from tasks.hard import get_hard_task
from tasks.grader import grade_easy, grade_medium, grade_hard


class ModerationEnv:
    def __init__(self):
        self.current_task = None
        self.step_count = 0
        self.max_steps = 3
        self.history = []
        self.state = State()

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

        self.state.current_task = {"difficulty": difficulty, **self.current_task}
        self.state.step_count = 0
        self.state.history = []

        return self._get_observation()

    def _get_observation(self) -> Observation:
        return Observation(
            content=self.current_task["content"],
            user_history=self.current_task["history"],
            previous_actions=[]
        )

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, dict]:
        self.step_count += 1
        self.state.step_count = self.step_count

        # Evaluate action dynamically based on state
        difficulty = self.state.current_task.get("difficulty")
        if difficulty == "easy":
            score, feedback = grade_easy(self.current_task, action)
        elif difficulty == "medium":
            score, feedback = grade_medium(self.current_task, action)
        else:
            score, feedback = grade_hard(self.current_task, action)

        reward = Reward(score=score, feedback=feedback)

        done = score > 0.9 or self.step_count >= self.max_steps

        action_dict = action.model_dump()
        action_dict["score"] = score
        action_dict["feedback"] = feedback
        self.history.append(action_dict)
        self.state.history = self.history
        
        obs = Observation(
            content=self.current_task["content"],
            user_history=self.current_task["history"],
            previous_actions=[str(a) for a in self.history]
        )

        return obs, reward, done, {}