import random


HARD_TASK_ID = "hard_moderation"
HARD_GRADER = "tasks.grader.grade_hard"

HARD_TASKS = [
    {
        "content": "People like you are the reason everything is broken",
        "history": [
            "previous warning",
            "2 removals",
            "temporary suspension",
            "returned again",
        ],
        "expected": {"label": "hate", "severity": "high", "decision": "ban"},
        "grader": HARD_GRADER,
    },
    {
        "content": "I'm just speaking the truth that nobody dares say about your kind",
        "history": ["removed post", "temporary ban"],
        "expected": {"label": "hate", "severity": "high", "decision": "ban"},
        "grader": HARD_GRADER,
    },
    {
        "content": "You think you're so smart don't you, everyone agrees you're pathetic",
        "history": ["warned twice", "1 removal"],
        "expected": {"label": "toxic", "severity": "high", "decision": "ban"},
        "grader": HARD_GRADER,
    },
    {
        "content": "Click here to claim your reward - act now before it expires!!!",
        "history": ["spam warning", "previous removal for spam"],
        "expected": {"label": "spam", "severity": "high", "decision": "ban"},
        "grader": HARD_GRADER,
    },
]


HARD_TASK_METADATA = {
    "id": HARD_TASK_ID,
    "name": "Hard Moderation",
    "difficulty": "hard",
    "description": "Apply context-aware escalation to coded hate, harassment, and repeat spam.",
    "grader": HARD_GRADER,
    "num_variants": len(HARD_TASKS),
}


def get_hard_task():
    return random.choice(HARD_TASKS)
