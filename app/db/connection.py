"""
db/connection.py
Handles MongoDB client creation and collection access.
"""

import os
from pymongo import MongoClient
from pymongo.collection import Collection
from dotenv import load_dotenv

load_dotenv()

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise RuntimeError("MONGODB_URI is not set in environment variables.")
        _client = MongoClient(uri)
    return _client


def get_db():
    return get_client()["adaptive_engine"]


def get_questions_collection() -> Collection:
    return get_db()["questions"]


def get_sessions_collection() -> Collection:
    return get_db()["user_sessions"]
