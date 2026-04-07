from tasks.easy import EASY_TASK_METADATA
from tasks.medium import MEDIUM_TASK_METADATA
from tasks.hard import HARD_TASK_METADATA


TASK_CATALOG = [
    EASY_TASK_METADATA,
    MEDIUM_TASK_METADATA,
    HARD_TASK_METADATA,
]


def get_task_catalog():
    return TASK_CATALOG
