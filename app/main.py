"""
app/main.py
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="Adaptive Diagnostic Engine",
    description=(
        "A 1-Dimension Adaptive Testing system using Item Response Theory (IRT). "
        "Dynamically selects GRE-style questions based on student ability, "
        "then generates an AI-powered personalized study plan via Gemini 1.5 Flash."
    ),
    version="1.0.0",
)

# Allow all origins (open for demo/intern evaluation purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "message": "Adaptive Diagnostic Engine is running.",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
