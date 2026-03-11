# 🧠 Adaptive Diagnostic Engine

A **1-Dimension Adaptive Testing** system that dynamically selects GRE-style questions based on a student's real-time performance using **Item Response Theory (IRT)**, then generates a personalized AI-powered study plan via **Gemini 1.5 Flash**.

---

## 🚀 Live Demo

> Deployed on Render: `https://adaptive-engine.onrender.com`  
> Interactive API Docs: `https://adaptive-engine.onrender.com/docs`

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | MongoDB Atlas |
| Adaptive Algorithm | 1PL Item Response Theory |
| AI Study Plan | Google Gemini 1.5 Flash |
| Deployment | Render (free tier) |

---

## 📁 Project Structure

```
adaptive-engine/
├── app/
│   ├── main.py              # FastAPI app + CORS
│   ├── routes/
│   │   └── adaptive.py      # All API endpoints
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── db/
│   │   └── connection.py    # MongoDB client
│   ├── algorithm/
│   │   └── irt.py           # IRT math (pure Python, no side effects)
│   └── ai/
│       └── study_plan.py    # Gemini 1.5 Flash integration
├── seed/
│   └── seed_questions.py    # Seeds 25 GRE questions
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🛠️ Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/adaptive-engine.git
cd adaptive-engine
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env`:
```env
MONGODB_URI=mongodb+srv://user:password@cluster0.xxxxx.mongodb.net/adaptive_engine
GEMINI_API_KEY=AIzaSy...your_key_here
```

### 5. Seed the database
```bash
python seed/seed_questions.py
```

### 6. Run the server
```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## 📡 API Documentation

### `POST /api/start-session`
Creates a new student session at baseline ability 0.5.

**Response:**
```json
{
  "session_id": "uuid-here",
  "message": "Session started. Call GET /api/next-question?session_id=<id> to begin."
}
```

---

### `GET /api/next-question?session_id=<id>`
Returns the next adaptive question, selected by IRT to be closest in difficulty to the student's current ability score.

**Response:**
```json
{
  "session_id": "...",
  "question_number": 1,
  "question_id": "ALG001",
  "text": "If 2x + 4 = 10, what is x?",
  "options": {"A": "2", "B": "3", "C": "4", "D": "5"},
  "topic": "Algebra",
  "difficulty": 0.1
}
```

---

### `POST /api/submit-answer`
Submits the student's answer. Updates ability score using IRT.

**Request body:**
```json
{
  "session_id": "uuid-here",
  "question_id": "ALG001",
  "selected_answer": "B"
}
```

**Response:**
```json
{
  "is_correct": true,
  "correct_answer": "B",
  "updated_ability_score": 0.55,
  "questions_answered": 1,
  "is_complete": false,
  "message": "Correct! Next question will be slightly harder."
}
```

---

### `GET /api/study-plan?session_id=<id>`
Available after all 10 questions are answered. Calls Gemini 1.5 Flash to generate a personalized 3-step study plan.

**Response:**
```json
{
  "session_id": "...",
  "ability_score": 0.63,
  "total_questions": 10,
  "correct_count": 6,
  "weak_topics": ["Vocabulary", "Data Analysis"],
  "study_plan": "## Your 3-Step Study Plan\n\n**Step 1: ...**"
}
```

---

### `GET /api/session-status?session_id=<id>`
Debug endpoint to inspect full session state including all answers.

---

## 🧮 Adaptive Algorithm Logic

The system uses the **1-Parameter Logistic (1PL) IRT model**.

### Probability of Correct Response
```
P(correct | θ, b) = 1 / (1 + e^-(θ - b))
```
- **θ (theta)**: Student ability score `[0.1 – 1.0]`, starts at `0.5`
- **b**: Question difficulty `[0.1 – 1.0]`

### Ability Score Update
After each answer, ability is updated using gradient ascent on the log-likelihood:
```
θ_new = θ_old + α × (actual - P)
```
- **α** = `0.1` (learning rate — conservative for stability)
- **actual** = `1` if correct, `0` if incorrect

### Why This Works
- When a student answers correctly, `actual (1) > P`, so θ increases
- When incorrect, `actual (0) < P`, so θ decreases
- The magnitude of change is naturally smaller when the result is "expected" (e.g., a strong student getting an easy question right barely increases their score)
- This is mathematically superior to naive +0.1/-0.1 jumps

### Question Selection
The next question is selected whose difficulty **b** is closest to the student's current **θ**. This maximises measurement information per question.

---

## 🤖 AI Log: How AI Tools Were Used

**Claude (Anthropic):** Used extensively for:
- Architecting the clean modular project structure
- Implementing the IRT algorithm with proper mathematical grounding
- Writing the Gemini prompt to elicit structured, data-driven study plans
- Generating all 25 GRE-style seed questions with calibrated difficulty scores
- Writing the comprehensive README

**Challenges AI couldn't solve:**
- Calibrating question difficulty scores required domain judgment — AI suggested values that needed manual review to ensure they felt authentically GRE-appropriate
- MongoDB Atlas network access configuration (IP whitelisting for Render) required manual setup in the Atlas dashboard — AI could explain steps but couldn't perform them

---

## 🌐 Deployment on Render

1. Push repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables: `MONGODB_URI`, `GEMINI_API_KEY`
7. Deploy → get your `*.onrender.com` URL

> **Note:** Free tier spins down after 15 min inactivity. First request after idle has a ~30s cold start.
