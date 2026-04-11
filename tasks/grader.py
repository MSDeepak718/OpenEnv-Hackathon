"""
Granular grading system for incident response triage.

Scoring components (0.0 – 1.0 continuous):
  - triage_priority:        20% weight (exact match, off-by-1, off-by-2+)
  - root_cause_category:    25% weight (exact match, related category)
  - remediation:            30% weight (exact, partial, harmful → penalty)
  - confidence_calibration: 10% weight (high on correct, low on wrong)
  - diagnosis_quality:      15% weight (keyword match against expected terms)

Penalties applied separately (clamped to 0.0 floor):
  - Harmful remediation:    −0.15
  - Confidence miscalibration: −0.05
"""

PRIORITY_ORDER = ["P1", "P2", "P3", "P4"]

RELATED_CATEGORIES = {
    "infrastructure": ["application"],
    "application": ["infrastructure", "configuration"],
    "network": ["infrastructure"],
    "security": ["network"],
    "configuration": ["application", "infrastructure"],
    "external": ["network"],
}

PARTIALLY_EFFECTIVE_REMEDIATIONS = {
    "restart_service": ["scale_up", "failover"],
    "scale_up": ["restart_service"],
    "rollback_deploy": ["update_config"],
    "block_ip": ["escalate"],
    "update_config": ["rollback_deploy"],
    "failover": ["restart_service", "scale_up"],
    "escalate": ["monitor"],
    "monitor": ["escalate"],
}


def _priority_score(expected: str, actual: str) -> float:
    """Score triage priority: exact=1.0, off-by-1=0.5, off-by-2+=0.0."""
    if actual == expected:
        return 1.0
    try:
        diff = abs(PRIORITY_ORDER.index(expected) - PRIORITY_ORDER.index(actual))
    except ValueError:
        return 0.0
    if diff == 1:
        return 0.5
    return 0.0


def _category_score(expected: str, actual: str) -> float:
    """Score root cause category: exact=1.0, related=0.4, wrong=0.0."""
    if actual == expected:
        return 1.0
    related = RELATED_CATEGORIES.get(expected, [])
    if actual in related:
        return 0.4
    return 0.0


def _remediation_score(expected: str, actual: str, harmful_list: list) -> tuple:
    """Score remediation: exact=1.0, partial=0.5, harmful=penalty, wrong=0.0."""
    penalties = []
    if actual == expected:
        return 1.0, penalties
    if actual in harmful_list:
        penalties.append(f"Harmful remediation '{actual}' applied (−0.15)")
        return 0.0, penalties
    partially = PARTIALLY_EFFECTIVE_REMEDIATIONS.get(expected, [])
    if actual in partially:
        return 0.5, penalties
    return 0.0, penalties


def _confidence_score(confidence: float, overall_accuracy: float) -> tuple:
    """
    Reward well-calibrated confidence.
    High confidence on correct answers → bonus.
    High confidence on wrong answers → penalty.
    """
    penalties = []
    if overall_accuracy >= 0.7:
        # Agent got it mostly right
        if confidence >= 0.7:
            return 1.0, penalties  # confident and correct
        elif confidence >= 0.4:
            return 0.6, penalties  # underconfident
        else:
            return 0.3, penalties  # way underconfident
    else:
        # Agent got it mostly wrong
        if confidence >= 0.8:
            penalties.append(f"Over-confident ({confidence:.1f}) on incorrect answer (−0.05)")
            return 0.0, penalties  # confidently wrong → penalty
        elif confidence <= 0.3:
            return 0.8, penalties  # at least knew it was uncertain
        else:
            return 0.4, penalties


def _diagnosis_score(diagnosis: str, key_terms: list) -> float:
    """Score diagnosis quality by keyword matching against expected terms."""
    if not diagnosis or not key_terms:
        return 0.0
    diagnosis_lower = diagnosis.lower()
    matches = sum(1 for term in key_terms if term.lower() in diagnosis_lower)
    ratio = matches / len(key_terms)
    # More generous scoring curve
    if ratio >= 0.5:
        return 1.0
    elif ratio >= 0.3:
        return 0.7
    elif ratio >= 0.15:
        return 0.4
    elif matches >= 1:
        return 0.2
    return 0.0


def _compute_score(task: dict, action, weights: dict) -> tuple:
    """
    Compute composite score with weights and penalties.
    Returns (score, breakdown, feedback, penalties).
    """
    expected = task["expected"]

    # Compute component scores
    priority_s = _priority_score(expected["triage_priority"], action.triage_priority)
    category_s = _category_score(expected["root_cause_category"], action.root_cause_category)
    remediation_s, rem_penalties = _remediation_score(
        expected["remediation"], action.remediation,
        expected.get("harmful_remediations", [])
    )

    # Calculate overall accuracy for confidence calibration
    core_accuracy = (priority_s * 0.3 + category_s * 0.35 + remediation_s * 0.35)
    confidence_s, conf_penalties = _confidence_score(action.confidence, core_accuracy)

    diagnosis_s = _diagnosis_score(action.diagnosis, expected.get("key_diagnosis_terms", []))

    # Weighted sum
    raw_score = (
        priority_s * weights["priority"]
        + category_s * weights["category"]
        + remediation_s * weights["remediation"]
        + confidence_s * weights["confidence"]
        + diagnosis_s * weights["diagnosis"]
    )

    # Apply penalties
    all_penalties = rem_penalties + conf_penalties
    penalty_total = 0.0
    for p in all_penalties:
        if "−0.15" in p or "-0.15" in p:
            penalty_total += 0.15
        elif "−0.05" in p or "-0.05" in p:
            penalty_total += 0.05

    final_score = max(0.01, min(0.99, raw_score - penalty_total))

    breakdown = {
        "triage_priority": round(priority_s, 3),
        "root_cause_category": round(category_s, 3),
        "remediation": round(remediation_s, 3),
        "confidence_calibration": round(confidence_s, 3),
        "diagnosis_quality": round(diagnosis_s, 3),
    }

    # Build feedback string
    parts = []
    parts.append(f"Priority: {'✓' if priority_s == 1.0 else '△' if priority_s > 0 else '✗'} (expected={expected['triage_priority']}, got={action.triage_priority})")
    parts.append(f"RootCause: {'✓' if category_s == 1.0 else '△' if category_s > 0 else '✗'} (expected={expected['root_cause_category']}, got={action.root_cause_category})")
    parts.append(f"Remediation: {'✓' if remediation_s == 1.0 else '△' if remediation_s > 0 else '✗'} (expected={expected['remediation']}, got={action.remediation})")
    parts.append(f"Diagnosis: {diagnosis_s:.0%} keyword match")
    parts.append(f"Confidence: {action.confidence:.1f} ({'well-calibrated' if confidence_s >= 0.7 else 'miscalibrated'})")
    if all_penalties:
        parts.append(f"Penalties: {', '.join(all_penalties)}")

    feedback = " | ".join(parts)

    return final_score, breakdown, feedback, all_penalties


def grade_easy(task: dict, action) -> tuple:
    """
    Easy grader — more lenient weights, priority and category matter most.
    """
    weights = {
        "priority": 0.25,
        "category": 0.25,
        "remediation": 0.25,
        "confidence": 0.10,
        "diagnosis": 0.15,
    }
    score, breakdown, feedback, penalties = _compute_score(task, action, weights)
    return score, f"[EASY] {feedback}"


def grade_medium(task: dict, action) -> tuple:
    """
    Medium grader — balanced weights, all components matter.
    """
    weights = {
        "priority": 0.20,
        "category": 0.25,
        "remediation": 0.30,
        "confidence": 0.10,
        "diagnosis": 0.15,
    }
    score, breakdown, feedback, penalties = _compute_score(task, action, weights)
    return score, f"[MEDIUM] {feedback}"


def grade_hard(task: dict, action) -> tuple:
    """
    Hard grader — stricter weights, remediation and category are critical.
    """
    weights = {
        "priority": 0.15,
        "category": 0.30,
        "remediation": 0.30,
        "confidence": 0.10,
        "diagnosis": 0.15,
    }
    score, breakdown, feedback, penalties = _compute_score(task, action, weights)
    return score, f"[HARD] {feedback}"