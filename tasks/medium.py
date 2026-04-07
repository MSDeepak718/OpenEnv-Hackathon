import random


MEDIUM_TASK_ID = "medium_moderation"
MEDIUM_GRADER = "tasks.grader.grade_medium"

MEDIUM_TASKS = [
    {
        "content": "I hate this game, it's stupid",
        "history": [],
        "expected": {"label": "safe", "severity": "low", "decision": "allow"},
        "grader": MEDIUM_GRADER,
    },
    {
        "content": "This product is total garbage, never buying again",
        "history": [],
        "expected": {"label": "safe", "severity": "low", "decision": "allow"},
        "grader": MEDIUM_GRADER,
    },
    {
        "content": "Ugh, you guys are the worst support team ever",
        "history": ["one previous warn"],
        "expected": {"label": "toxic", "severity": "medium", "decision": "warn"},
        "grader": MEDIUM_GRADER,
    },
    {
        "content": "Win a free iPhone! Just DM us your credit card number!",
        "history": [],
        "expected": {"label": "spam", "severity": "high", "decision": "remove"},
        "grader": MEDIUM_GRADER,
    },
]


MEDIUM_TASK_METADATA = {
    "id": MEDIUM_TASK_ID,
    "name": "Medium Moderation",
    "difficulty": "medium",
    "description": "Distinguish venting and criticism from moderate toxicity and phishing-like spam.",
    "grader": MEDIUM_GRADER,
    "num_variants": len(MEDIUM_TASKS),
}


def get_medium_task():
    return random.choice(MEDIUM_TASKS)
