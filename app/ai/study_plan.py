"""
ai/study_plan.py
Generates a personalized 3-step study plan using Gemini 1.5 Flash
based on the student's test performance data.
"""

import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini client once at module load
_api_key = os.getenv("GEMINI_API_KEY")


def _build_prompt(
    ability_score: float,
    total_questions: int,
    correct_count: int,
    weak_topics: list[str],
    topic_breakdown: dict[str, dict],
) -> str:
    """Construct a detailed, structured prompt for Gemini."""

    accuracy = round((correct_count / total_questions) * 100, 1) if total_questions else 0
    difficulty_label = (
        "Beginner" if ability_score < 0.4
        else "Intermediate" if ability_score < 0.7
        else "Advanced"
    )

    topic_lines = "\n".join(
        f"  - {topic}: {data['correct']}/{data['total']} correct"
        for topic, data in topic_breakdown.items()
    )

    weak_str = ", ".join(weak_topics) if weak_topics else "None identified"

    prompt = f"""
You are an expert GRE tutor. A student just completed an adaptive diagnostic test.
Analyze their performance and create a precise, actionable 3-step study plan.

## Student Performance Summary
- Final Ability Score: {ability_score:.2f} / 1.00 ({difficulty_label} level)
- Overall Accuracy: {accuracy}% ({correct_count}/{total_questions} questions correct)
- Weak Topics: {weak_str}

## Topic-by-Topic Breakdown
{topic_lines}

## Your Task
Write a **3-Step Personalized Study Plan** for this student. Each step must:
1. Target a specific weak area from the data above
2. Include 2-3 concrete study actions (not generic advice)
3. Suggest a realistic time commitment

Format your response in clean markdown with clear headers for each step.
Be specific, encouraging, and data-driven. Keep total response under 400 words.
""".strip()

    return prompt


def generate_study_plan(
    ability_score: float,
    total_questions: int,
    correct_count: int,
    weak_topics: list[str],
    topic_breakdown: dict[str, dict],
) -> str:
    """
    Call Gemini 1.5 Flash and return a personalized study plan as markdown string.
    Falls back to a generic plan if the API call fails.
    """
    if not _api_key:
        return _fallback_plan(weak_topics)

    try:
        client = genai.Client(api_key=_api_key)
        prompt = _build_prompt(
            ability_score, total_questions, correct_count, weak_topics, topic_breakdown
        )
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text

    except Exception as e:
        print(f"[Gemini Error] {e}")
        return _fallback_plan(weak_topics)


def _fallback_plan(weak_topics: list[str]) -> str:
    """Returned when Gemini is unavailable — ensures endpoint never crashes."""
    topics_str = ", ".join(weak_topics) if weak_topics else "general GRE content"
    return f"""
## Your 3-Step Study Plan

**Step 1: Focus on Weak Areas**
Review core concepts in: {topics_str}. Spend 30 minutes per topic.

**Step 2: Practice with Targeted Questions**
Complete 20 practice questions per weak topic using official GRE materials.

**Step 3: Review & Consolidate**
After each practice session, review all incorrect answers and note patterns.
Aim for 85%+ accuracy before moving on.

*(Note: AI-generated plan unavailable — using default plan.)*
""".strip()
