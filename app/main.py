"""moodboard-api: 오늘의 기분 한 줄을 기록하는 아주 작은 API.

Four routes, backed by app/storage.py. See the README for the "why" -
this file is just the "how".
"""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Response

from app.models import Note, NoteCreate
from app.storage import MoodStore

app = FastAPI(
    title="Moodboard API | 오늘의 기분 노트 API",
    description="Record one short mood note per day. | 하루 한 줄의 기분을 기록하세요.",
    version="0.1.0",
)

# A single, lazily-created store backed by a local moodboard.db file.
# It's only instantiated the first time get_store() actually runs, so
# just importing this module (e.g. from tests) never touches a real
# file. Tests replace get_store entirely via app.dependency_overrides.
_store: Optional[MoodStore] = None


def get_store() -> MoodStore:
    global _store
    if _store is None:
        _store = MoodStore("moodboard.db")
    return _store


@app.post("/notes", response_model=Note, status_code=201)
def create_note(payload: NoteCreate, store: MoodStore = Depends(get_store)) -> dict:
    return store.create_note(text=payload.text, mood=payload.mood)


@app.get("/notes", response_model=list[Note])
def list_notes(
    mood: Optional[str] = None, store: MoodStore = Depends(get_store)
) -> list[dict]:
    return store.list_notes(mood=mood)


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int, store: MoodStore = Depends(get_store)) -> dict:
    note = store.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found. | 노트를 찾을 수 없습니다.")
    return note


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, store: MoodStore = Depends(get_store)) -> Response:
    deleted = store.delete_note(note_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Note not found. | 노트를 찾을 수 없습니다.")
    return Response(status_code=204)
