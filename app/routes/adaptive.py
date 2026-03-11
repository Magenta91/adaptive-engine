"""
routes/adaptive.py
All API endpoints for the adaptive testing engine.
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.db import get_questions_collection, get_sessions_collection
from app.models import (
    StartSessionResponse, NextQuestionResponse,
    SubmitAnswerRequest, SubmitAnswerResponse, StudyPlanResponse,
)
from app.algorithm import (
    update_ability, select_question, BASELINE_ABILITY, MAX_QUESTIONS
)
from app.ai import generate_study_plan

router = APIRouter(prefix="/api", tags=["Adaptive Engine"])


# ── POST /start-session ────────────────────────────────────────────────────────

@router.post("/start-session", response_model=StartSessionResponse)
def start_session():
    """
    Create a new user session. Returns a session_id to use in subsequent calls.
    """
    sessions = get_sessions_collection()

    session_id = str(uuid.uuid4())
    session_doc = {
        "session_id": session_id,
        "ability_score": BASELINE_ABILITY,
        "questions_answered": 0,
        "answers": [],
        "is_complete": False,
        "created_at": datetime.utcnow(),
    }
    sessions.insert_one(session_doc)

    return StartSessionResponse(
        session_id=session_id,
        message="Session started. Call GET /api/next-question?session_id=<id> to begin."
    )


# ── GET /next-question ─────────────────────────────────────────────────────────

@router.get("/next-question", response_model=NextQuestionResponse)
def next_question(session_id: str):
    """
    Return the next adaptive question for the given session.
    Question difficulty is selected based on the student's current ability score (IRT).
    """
    sessions = get_sessions_collection()
    questions_col = get_questions_collection()

    # Fetch session
    session = sessions.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session["is_complete"]:
        raise HTTPException(status_code=400, detail="Session is complete. Fetch your study plan.")

    # Check question limit
    if session["questions_answered"] >= MAX_QUESTIONS:
        sessions.update_one(
            {"session_id": session_id},
            {"$set": {"is_complete": True}}
        )
        raise HTTPException(
            status_code=400,
            detail=f"You have answered {MAX_QUESTIONS} questions. Session complete — fetch your study plan."
        )

    # Load all questions and pick best one via IRT
    all_questions = list(questions_col.find({}, {"_id": 0}))
    answered_ids = {a["question_id"] for a in session.get("answers", [])}

    selected = select_question(
        ability=session["ability_score"],
        questions=all_questions,
        answered_ids=answered_ids,
    )
    if not selected:
        raise HTTPException(status_code=404, detail="No more questions available.")

    return NextQuestionResponse(
        session_id=session_id,
        question_number=session["questions_answered"] + 1,
        question_id=selected["question_id"],
        text=selected["text"],
        options=selected["options"],
        topic=selected["topic"],
        difficulty=selected["difficulty"],
    )


# ── POST /submit-answer ────────────────────────────────────────────────────────

@router.post("/submit-answer", response_model=SubmitAnswerResponse)
def submit_answer(payload: SubmitAnswerRequest):
    """
    Submit the student's answer for a question.
    Updates ability score using 1PL IRT and records the result.
    """
    sessions = get_sessions_collection()
    questions_col = get_questions_collection()

    # Validate session
    session = sessions.find_one({"session_id": payload.session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session["is_complete"]:
        raise HTTPException(status_code=400, detail="Session already complete.")

    # Validate question
    question = questions_col.find_one({"question_id": payload.question_id}, {"_id": 0})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    # Check for duplicate submission
    already_answered = {a["question_id"] for a in session.get("answers", [])}
    if payload.question_id in already_answered:
        raise HTTPException(status_code=400, detail="Question already answered in this session.")

    # Evaluate answer
    is_correct = payload.selected_answer.upper() == question["correct_answer"].upper()

    # Update ability score using IRT
    new_ability = update_ability(
        current_ability=session["ability_score"],
        difficulty=question["difficulty"],
        is_correct=is_correct,
    )

    # Build answer record
    answer_record = {
        "question_id": payload.question_id,
        "topic": question["topic"],
        "difficulty": question["difficulty"],
        "is_correct": is_correct,
        "timestamp": datetime.utcnow(),
    }

    new_count = session["questions_answered"] + 1
    is_complete = new_count >= MAX_QUESTIONS

    # Persist update
    sessions.update_one(
        {"session_id": payload.session_id},
        {
            "$set": {
                "ability_score": new_ability,
                "questions_answered": new_count,
                "is_complete": is_complete,
            },
            "$push": {"answers": answer_record},
        }
    )

    message = (
        "Correct! Next question will be slightly harder."
        if is_correct
        else "Incorrect. Next question will be slightly easier."
    )
    if is_complete:
        message = "Test complete! Call GET /api/study-plan?session_id=<id> for your personalized plan."

    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_answer=question["correct_answer"],
        updated_ability_score=new_ability,
        questions_answered=new_count,
        is_complete=is_complete,
        message=message,
    )


# ── GET /study-plan ────────────────────────────────────────────────────────────

@router.get("/study-plan", response_model=StudyPlanResponse)
def study_plan(session_id: str):
    """
    After the session is complete, returns an AI-generated personalized study plan
    using Gemini 1.5 Flash based on the student's performance data.
    """
    sessions = get_sessions_collection()

    session = sessions.find_one({"session_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    if not session["is_complete"]:
        raise HTTPException(
            status_code=400,
            detail=f"Session not complete yet. Answer all {MAX_QUESTIONS} questions first."
        )

    answers = session.get("answers", [])
    correct_count = sum(1 for a in answers if a["is_correct"])

    # Build topic breakdown
    topic_breakdown: dict[str, dict] = {}
    for a in answers:
        topic = a["topic"]
        if topic not in topic_breakdown:
            topic_breakdown[topic] = {"total": 0, "correct": 0}
        topic_breakdown[topic]["total"] += 1
        if a["is_correct"]:
            topic_breakdown[topic]["correct"] += 1

    # Identify weak topics (accuracy < 60%)
    weak_topics = [
        topic for topic, data in topic_breakdown.items()
        if (data["correct"] / data["total"]) < 0.6
    ]

    # Generate study plan via Gemini
    plan = generate_study_plan(
        ability_score=session["ability_score"],
        total_questions=len(answers),
        correct_count=correct_count,
        weak_topics=weak_topics,
        topic_breakdown=topic_breakdown,
    )

    return StudyPlanResponse(
        session_id=session_id,
        ability_score=session["ability_score"],
        total_questions=len(answers),
        correct_count=correct_count,
        weak_topics=weak_topics,
        study_plan=plan,
    )


# ── GET /session-status ────────────────────────────────────────────────────────

@router.get("/session-status")
def session_status(session_id: str):
    """Debug endpoint: view full session state."""
    sessions = get_sessions_collection()
    session = sessions.find_one({"session_id": session_id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    # Convert datetime objects to strings for JSON
    session["created_at"] = str(session.get("created_at", ""))
    for a in session.get("answers", []):
        a["timestamp"] = str(a.get("timestamp", ""))
    return session
