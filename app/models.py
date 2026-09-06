"""Pydantic models used by the moodboard API.

Kept intentionally small: one model for what a client sends when creating
a note, and one for what the API returns.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    """Payload for POST /notes."""

    text: str = Field(..., min_length=1, max_length=280, description="오늘의 한 줄")
    mood: str = Field(..., min_length=1, max_length=32, description="자유 형식 기분 태그, 예: calm, excited")


class Note(BaseModel):
    """A stored mood note, as returned to clients."""

    id: int
    text: str
    mood: str
    created_at: str  # ISO 8601 UTC timestamp, set by the server
