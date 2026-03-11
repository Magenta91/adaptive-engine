"""
algorithm/irt.py

1-Parameter Logistic (1PL) Item Response Theory implementation.

Core formula:
    P(correct | θ, b) = 1 / (1 + e^-(θ - b))

Where:
    θ (theta)  = student ability score  [range: 0.0 – 1.0, baseline: 0.5]
    b          = question difficulty     [range: 0.1 – 1.0]
    P          = probability of correct response

Ability update rule (gradient ascent on log-likelihood):
    θ_new = θ_old + α × (actual - P)

Where:
    α     = learning rate (0.1 — conservative, stable updates)
    actual = 1 if correct, 0 if incorrect
"""

import math

# ── Constants ──────────────────────────────────────────────────────────────────

BASELINE_ABILITY: float = 0.5
LEARNING_RATE: float = 0.1
MIN_ABILITY: float = 0.1
MAX_ABILITY: float = 1.0

MAX_QUESTIONS: int = 10

# Difficulty selection window — how close the next question's difficulty
# should be to the current ability score
DIFFICULTY_WINDOW: float = 0.15


# ── Core IRT Functions ─────────────────────────────────────────────────────────

def probability_correct(ability: float, difficulty: float) -> float:
    """
    1PL IRT: probability that a student with `ability` answers a question
    of `difficulty` correctly.
    """
    exponent = -(ability - difficulty)
    return 1.0 / (1.0 + math.exp(exponent))


def update_ability(
    current_ability: float,
    difficulty: float,
    is_correct: bool,
    learning_rate: float = LEARNING_RATE,
) -> float:
    """
    Update the student's ability score after answering a question.
    Uses gradient ascent on the log-likelihood of the IRT model.

    Returns the new ability score clamped to [MIN_ABILITY, MAX_ABILITY].
    """
    actual = 1.0 if is_correct else 0.0
    p = probability_correct(current_ability, difficulty)
    new_ability = current_ability + learning_rate * (actual - p)
    return round(float(max(MIN_ABILITY, min(MAX_ABILITY, new_ability))), 4)


def target_difficulty(ability: float) -> float:
    """
    The ideal next question difficulty is equal to the student's current
    ability — this maximises measurement information in IRT.
    Returns clamped value in [0.1, 1.0].
    """
    return round(float(max(0.1, min(1.0, ability))), 2)


def select_question(
    ability: float,
    questions: list[dict],
    answered_ids: set[str],
) -> dict | None:
    """
    Select the best unanswered question whose difficulty is closest
    to the student's current ability score.

    Args:
        ability:      current ability θ
        questions:    list of question dicts from MongoDB
        answered_ids: set of already-used question_ids

    Returns:
        The best matching question dict, or None if none remain.
    """
    candidates = [
        q for q in questions
        if q["question_id"] not in answered_ids
    ]
    if not candidates:
        return None

    ideal = target_difficulty(ability)

    # Sort by absolute distance from ideal difficulty, then pick closest
    candidates.sort(key=lambda q: abs(q["difficulty"] - ideal))
    return candidates[0]
