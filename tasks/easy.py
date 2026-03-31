import random


EASY_TASKS = [
    {
        "content": "Someone should shut you up permanently",
        "history": ["previous toxic behavior"],
        "expected": {"label": "hate", "severity": "high", "decision": "ban"},
    },
    {
        "content": "I'll find out where you live and make you regret this",
        "history": ["previous warning"],
        "expected": {"label": "hate", "severity": "high", "decision": "ban"},
    },
    {
        "content": "Buy cheap followers now! Click here for 10,000 fake fans!!!",
        "history": [],
        "expected": {"label": "spam", "severity": "medium", "decision": "remove"},
    },
    {
        "content": "You are absolutely worthless and should disappear",
        "history": ["previous ban lifted"],
        "expected": {"label": "toxic", "severity": "high", "decision": "ban"},
    },
]


def get_easy_task():
    return random.choice(EASY_TASKS)