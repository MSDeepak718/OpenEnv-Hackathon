def grade_easy(task, action):
    expected = task["expected"]
    score = 0.0

    # Easy mode grading: Grade based ONLY on matching the label
    if action.label == expected["label"]:
        score = 0.99
    else:
        score = 0.01

    feedback = (
        f"[EASY GRADER] Expected label={expected['label']} | "
        f"Got label={action.label} | Score={score:.2f}"
    )
    return score, feedback

def grade_medium(task, action):
    expected = task["expected"]
    score = 0.0

    # Medium mode grading: Grade based on severity and decision
    if action.severity == expected["severity"]:
        score += 0.4
    if action.decision == expected["decision"]:
        score += 0.59
        
    score = max(0.01, min(0.99, score))
    feedback = (
        f"[MEDIUM GRADER] Expected severity={expected['severity']}, decision={expected['decision']} | "
        f"Got severity={action.severity}, decision={action.decision} | Score={score:.2f}"
    )
    return score, feedback

def grade_hard(task, action):
    expected = task["expected"]
    
    # Hard mode grading: Strict all-or-nothing matching
    if (action.label == expected["label"] and 
        action.severity == expected["severity"] and 
        action.decision == expected["decision"]):
        score = 0.99
    else:
        score = 0.01

    feedback = (
        f"[HARD GRADER] Must match all fields. Expected={expected} | "
        f"Got label={action.label}, severity={action.severity}, decision={action.decision} | Score={score:.2f}"
    )
    return score, feedback