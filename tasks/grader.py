def grade_action(task, action):
    expected = task["expected"]

    score = 0.0

    if action.label == expected["label"]:
        score += 0.3

    if action.severity == expected["severity"]:
        score += 0.3

    if action.decision == expected["decision"]:
        score += 0.4

    if expected["decision"] == "ban" and action.decision == "allow":
        score -= 0.5

    score = max(0.0, min(1.0, score))

    feedback = (
        f"Expected label={expected['label']}, severity={expected['severity']}, decision={expected['decision']} | "
        f"Got label={action.label}, severity={action.severity}, decision={action.decision} | "
        f"Score={score:.2f}"
    )

    return score, feedback