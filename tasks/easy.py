import random


EASY_TASK_ID = "easy_moderation"
EASY_GRADER = "tasks.grader.grade_easy"

EASY_TASKS = [
    {
        "content": "Someone should shut you up permanently",
        "history": ["previous toxic behavior"],
        "expected": {"label": "hate", "severity": "high", "decision": "ban"},
        "grader": EASY_GRADER,
    },
    {
        "content": "I'll find out where you live and make you regret this",
        "history": ["previous warning"],
        "expected": {"label": "hate", "severity": "high", "decision": "ban"},
        "grader": EASY_GRADER,
    },
    {
        "content": "Buy cheap followers now! Click here for 10,000 fake fans!!!",
        "history": [],
        "expected": {"label": "spam", "severity": "medium", "decision": "remove"},
        "grader": EASY_GRADER,
    },
    {
        "content": "You are absolutely worthless and should disappear",
        "history": ["previous ban lifted"],
        "expected": {"label": "toxic", "severity": "high", "decision": "ban"},
        "grader": EASY_GRADER,
    },
]


EASY_TASK_METADATA = {
    "id": EASY_TASK_ID,
    "name": "Easy Moderation",
    "difficulty": "easy",
    "description": "Classify explicit threats, clear toxicity, and obvious spam.",
    "grader": EASY_GRADER,
    "num_variants": len(EASY_TASKS),
}


def get_easy_task():
    return random.choice(EASY_TASKS)
