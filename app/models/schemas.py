"""
models/schemas.py
Pydantic models for request/response validation and MongoDB documents.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Question ──────────────────────────────────────────────────────────────────

class Question(BaseModel):
    question_id: str
    text: str
    options: dict[str, str]          # {"A": "...", "B": "...", "C": "...", "D": "..."}
    correct_answer: str              # "A" | "B" | "C" | "D"
    difficulty: float                # 0.1 – 1.0
    topic: str                       # e.g. "Algebra", "Vocabulary"
    tags: list[str]


# ── Session ───────────────────────────────────────────────────────────────────

class AnswerRecord(BaseModel):
    question_id: str
    topic: str
    difficulty: float
    is_correct: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserSession(BaseModel):
    session_id: str
    ability_score: float = 0.5       # θ (theta) in IRT — starts at baseline
    questions_answered: int = 0
    answers: list[AnswerRecord] = []
    is_complete: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ── API Request / Response ────────────────────────────────────────────────────

class StartSessionResponse(BaseModel):
    session_id: str
    message: str


class NextQuestionResponse(BaseModel):
    session_id: str
    question_number: int
    question_id: str
    text: str
    options: dict[str, str]
    topic: str
    difficulty: float


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    selected_answer: str             # "A" | "B" | "C" | "D"


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_answer: str
    updated_ability_score: float
    questions_answered: int
    is_complete: bool
    message: str


class StudyPlanResponse(BaseModel):
    session_id: str
    ability_score: float
    total_questions: int
    correct_count: int
    weak_topics: list[str]
    study_plan: str                  # Raw LLM-generated markdown plan
