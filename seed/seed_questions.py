"""
seed/seed_questions.py

Seeds the MongoDB `questions` collection with 25 GRE-style questions
spanning Algebra, Vocabulary, Geometry, Data Analysis, and Reading Comprehension.

Run: python seed/seed_questions.py
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.db.connection import get_questions_collection

QUESTIONS = [
    # ── Algebra (difficulty: 0.1 – 0.9) ───────────────────────────────────────
    {
        "question_id": "ALG001",
        "text": "If 2x + 4 = 10, what is the value of x?",
        "options": {"A": "2", "B": "3", "C": "4", "D": "5"},
        "correct_answer": "B",
        "difficulty": 0.1,
        "topic": "Algebra",
        "tags": ["linear equations", "basic"],
    },
    {
        "question_id": "ALG002",
        "text": "If f(x) = 3x² - 2x + 1, what is f(2)?",
        "options": {"A": "7", "B": "9", "C": "11", "D": "13"},
        "correct_answer": "B",
        "difficulty": 0.3,
        "topic": "Algebra",
        "tags": ["functions", "quadratic"],
    },
    {
        "question_id": "ALG003",
        "text": "Solve for x: |2x - 6| = 10",
        "options": {"A": "x = 8 or x = -2", "B": "x = 8 only", "C": "x = -2 only", "D": "x = 4 or x = -8"},
        "correct_answer": "A",
        "difficulty": 0.5,
        "topic": "Algebra",
        "tags": ["absolute value", "equations"],
    },
    {
        "question_id": "ALG004",
        "text": "If x² - 5x + 6 = 0, what are the values of x?",
        "options": {"A": "1 and 6", "B": "2 and 3", "C": "-2 and -3", "D": "3 and 6"},
        "correct_answer": "B",
        "difficulty": 0.4,
        "topic": "Algebra",
        "tags": ["quadratic", "factoring"],
    },
    {
        "question_id": "ALG005",
        "text": "For which value of k does the system 2x + ky = 4 and 4x + 2y = 8 have infinitely many solutions?",
        "options": {"A": "k = 1", "B": "k = 2", "C": "k = 4", "D": "k = 0"},
        "correct_answer": "A",
        "difficulty": 0.75,
        "topic": "Algebra",
        "tags": ["systems of equations", "advanced"],
    },
    {
        "question_id": "ALG006",
        "text": "If log₂(x) = 5, what is x?",
        "options": {"A": "10", "B": "25", "C": "32", "D": "64"},
        "correct_answer": "C",
        "difficulty": 0.6,
        "topic": "Algebra",
        "tags": ["logarithms"],
    },
    # ── Vocabulary (difficulty: 0.2 – 0.9) ────────────────────────────────────
    {
        "question_id": "VOC001",
        "text": "Choose the word most similar in meaning to BENEVOLENT.",
        "options": {"A": "Hostile", "B": "Kind", "C": "Indifferent", "D": "Greedy"},
        "correct_answer": "B",
        "difficulty": 0.2,
        "topic": "Vocabulary",
        "tags": ["synonyms", "basic"],
    },
    {
        "question_id": "VOC002",
        "text": "EPHEMERAL most nearly means:",
        "options": {"A": "Eternal", "B": "Bright", "C": "Short-lived", "D": "Heavy"},
        "correct_answer": "C",
        "difficulty": 0.4,
        "topic": "Vocabulary",
        "tags": ["synonyms", "GRE word list"],
    },
    {
        "question_id": "VOC003",
        "text": "The word OBFUSCATE most nearly means:",
        "options": {"A": "Clarify", "B": "Confuse", "C": "Brighten", "D": "Simplify"},
        "correct_answer": "B",
        "difficulty": 0.65,
        "topic": "Vocabulary",
        "tags": ["synonyms", "advanced"],
    },
    {
        "question_id": "VOC004",
        "text": "LOQUACIOUS is the opposite of:",
        "options": {"A": "Verbose", "B": "Talkative", "C": "Taciturn", "D": "Eloquent"},
        "correct_answer": "C",
        "difficulty": 0.7,
        "topic": "Vocabulary",
        "tags": ["antonyms", "advanced"],
    },
    {
        "question_id": "VOC005",
        "text": "SYCOPHANT most nearly means:",
        "options": {"A": "Critic", "B": "Flatterer", "C": "Leader", "D": "Philosopher"},
        "correct_answer": "B",
        "difficulty": 0.8,
        "topic": "Vocabulary",
        "tags": ["synonyms", "GRE word list"],
    },
    {
        "question_id": "VOC006",
        "text": "PELLUCID most nearly means:",
        "options": {"A": "Opaque", "B": "Translucent", "C": "Turbid", "D": "Iridescent"},
        "correct_answer": "B",
        "difficulty": 0.9,
        "topic": "Vocabulary",
        "tags": ["synonyms", "rare words"],
    },
    # ── Geometry (difficulty: 0.2 – 0.85) ─────────────────────────────────────
    {
        "question_id": "GEO001",
        "text": "What is the area of a circle with radius 7? (Use π ≈ 3.14)",
        "options": {"A": "43.96", "B": "153.86", "C": "44", "D": "49"},
        "correct_answer": "B",
        "difficulty": 0.2,
        "topic": "Geometry",
        "tags": ["circles", "area"],
    },
    {
        "question_id": "GEO002",
        "text": "In a right triangle, the legs are 5 and 12. What is the hypotenuse?",
        "options": {"A": "11", "B": "13", "C": "15", "D": "17"},
        "correct_answer": "B",
        "difficulty": 0.3,
        "topic": "Geometry",
        "tags": ["Pythagorean theorem", "triangles"],
    },
    {
        "question_id": "GEO003",
        "text": "A rectangle has perimeter 40 and length 12. What is its area?",
        "options": {"A": "72", "B": "80", "C": "96", "D": "112"},
        "correct_answer": "C",
        "difficulty": 0.45,
        "topic": "Geometry",
        "tags": ["rectangles", "perimeter", "area"],
    },
    {
        "question_id": "GEO004",
        "text": "Two parallel lines are cut by a transversal. If one interior angle is 65°, what is the co-interior angle?",
        "options": {"A": "65°", "B": "115°", "C": "25°", "D": "90°"},
        "correct_answer": "B",
        "difficulty": 0.55,
        "topic": "Geometry",
        "tags": ["parallel lines", "angles"],
    },
    {
        "question_id": "GEO005",
        "text": "The volume of a cylinder with radius 3 and height 10 is approximately:",
        "options": {"A": "90π", "B": "60π", "C": "30π", "D": "120π"},
        "correct_answer": "A",
        "difficulty": 0.65,
        "topic": "Geometry",
        "tags": ["cylinders", "volume"],
    },
    {
        "question_id": "GEO006",
        "text": "In triangle ABC, angle A = 50° and angle B = 70°. What is the exterior angle at C?",
        "options": {"A": "60°", "B": "120°", "C": "130°", "D": "80°"},
        "correct_answer": "B",
        "difficulty": 0.85,
        "topic": "Geometry",
        "tags": ["triangles", "exterior angles"],
    },
    # ── Data Analysis (difficulty: 0.3 – 0.9) ─────────────────────────────────
    {
        "question_id": "DAT001",
        "text": "What is the median of the dataset: 3, 7, 1, 9, 4?",
        "options": {"A": "3", "B": "4", "C": "5", "D": "7"},
        "correct_answer": "B",
        "difficulty": 0.25,
        "topic": "Data Analysis",
        "tags": ["median", "descriptive statistics"],
    },
    {
        "question_id": "DAT002",
        "text": "A bag has 5 red and 3 blue marbles. What is the probability of drawing a red marble?",
        "options": {"A": "3/8", "B": "5/8", "C": "5/3", "D": "1/2"},
        "correct_answer": "B",
        "difficulty": 0.3,
        "topic": "Data Analysis",
        "tags": ["probability", "basic"],
    },
    {
        "question_id": "DAT003",
        "text": "The mean of 5 numbers is 14. If four of the numbers are 10, 12, 16, and 18, what is the fifth?",
        "options": {"A": "12", "B": "14", "C": "16", "D": "10"},
        "correct_answer": "B",
        "difficulty": 0.5,
        "topic": "Data Analysis",
        "tags": ["mean", "arithmetic"],
    },
    {
        "question_id": "DAT004",
        "text": "In a set of 100 values, the 75th percentile is 82. What does this mean?",
        "options": {
            "A": "75 values are above 82",
            "B": "75 values are below or equal to 82",
            "C": "The mean is 82",
            "D": "82% of data are below 75",
        },
        "correct_answer": "B",
        "difficulty": 0.6,
        "topic": "Data Analysis",
        "tags": ["percentiles", "interpretation"],
    },
    {
        "question_id": "DAT005",
        "text": "If two events A and B are independent and P(A) = 0.4, P(B) = 0.5, what is P(A ∩ B)?",
        "options": {"A": "0.9", "B": "0.2", "C": "0.45", "D": "0.1"},
        "correct_answer": "B",
        "difficulty": 0.7,
        "topic": "Data Analysis",
        "tags": ["probability", "independence"],
    },
    # ── Reading Comprehension (difficulty: 0.4 – 0.9) ─────────────────────────
    {
        "question_id": "RC001",
        "text": (
            "Passage: 'The theory of evolution posits that species change over time through "
            "natural selection, adapting to environmental pressures.'\n\n"
            "Which best describes the main idea?"
        ),
        "options": {
            "A": "Species are created perfectly adapted",
            "B": "Evolution is driven by environmental adaptation via natural selection",
            "C": "All species remain constant over time",
            "D": "Natural selection eliminates all weak species",
        },
        "correct_answer": "B",
        "difficulty": 0.4,
        "topic": "Reading Comprehension",
        "tags": ["main idea", "science passage"],
    },
    {
        "question_id": "RC002",
        "text": (
            "Passage: 'While proponents of austerity argue that reducing government spending "
            "stabilizes economies, critics contend that it exacerbates inequality and "
            "suppresses growth during recessions.'\n\n"
            "The author's tone is best described as:"
        ),
        "options": {"A": "Strongly pro-austerity", "B": "Strongly anti-austerity", "C": "Balanced and analytical", "D": "Indifferent"},
        "correct_answer": "C",
        "difficulty": 0.75,
        "topic": "Reading Comprehension",
        "tags": ["author tone", "economics passage"],
    },
]


def seed():
    col = get_questions_collection()

    # Drop existing to avoid duplicates on re-run
    col.delete_many({})
    result = col.insert_many(QUESTIONS)
    print(f"✅ Seeded {len(result.inserted_ids)} questions into 'questions' collection.")

    # Create indexes for performance
    col.create_index("question_id", unique=True)
    col.create_index("difficulty")
    col.create_index("topic")
    print("✅ Indexes created on question_id, difficulty, topic.")


if __name__ == "__main__":
    seed()
