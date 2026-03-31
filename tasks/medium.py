import random


MEDIUM_TASKS = [
    {
        "content": "I hate this game, it's stupid",
        "history": [],
        "expected": {"label": "safe", "severity": "low", "decision": "allow"},
    },
    {
        "content": "This product is total garbage, never buying again",
        "history": [],
        "expected": {"label": "safe", "severity": "low", "decision": "allow"},
    },
    {
        "content": "Ugh, you guys are the worst support team ever",
        "history": ["one previous warn"],
        "expected": {"label": "toxic", "severity": "medium", "decision": "warn"},
    },
    {
        "content": "Win a free iPhone! Just DM us your credit card number!",
        "history": [],
        "expected": {"label": "spam", "severity": "high", "decision": "remove"},
    },
]


def get_medium_task():
    return random.choice(MEDIUM_TASKS)