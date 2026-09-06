"""Tests for the moodboard API.

Each test gets its own throw-away SQLite file (via pytest's tmp_path),
wired in through FastAPI's dependency override system, so nothing here
ever touches a real moodboard.db.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_store
from app.storage import MoodStore


@pytest.fixture()
def client(tmp_path):
    db_path = tmp_path / "test_moodboard.db"
    test_store = MoodStore(str(db_path))
    app.dependency_overrides[get_store] = lambda: test_store
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    test_store.close()


def test_create_note(client):
    resp = client.post("/notes", json={"text": "커피 한 잔, 딱 좋은 아침", "mood": "calm"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["text"] == "커피 한 잔, 딱 좋은 아침"
    assert body["mood"] == "calm"
    assert isinstance(body["id"], int)
    assert "created_at" in body


def test_list_notes_newest_first(client):
    client.post("/notes", json={"text": "첫 번째 기록", "mood": "calm"})
    client.post("/notes", json={"text": "두 번째 기록", "mood": "excited"})

    resp = client.get("/notes")
    assert resp.status_code == 200
    notes = resp.json()
    assert len(notes) == 2
    # newest first
    assert notes[0]["text"] == "두 번째 기록"
    assert notes[1]["text"] == "첫 번째 기록"


def test_list_notes_empty(client):
    resp = client.get("/notes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_note(client):
    created = client.post("/notes", json={"text": "메모 하나", "mood": "tired"}).json()

    resp = client.get(f"/notes/{created['id']}")
    assert resp.status_code == 200
    assert resp.json() == created


def test_get_note_404(client):
    resp = client.get("/notes/999")
    assert resp.status_code == 404


def test_delete_note(client):
    created = client.post("/notes", json={"text": "지울 메모", "mood": "calm"}).json()

    delete_resp = client.delete(f"/notes/{created['id']}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/notes/{created['id']}")
    assert get_resp.status_code == 404


def test_delete_note_404(client):
    resp = client.delete("/notes/999")
    assert resp.status_code == 404


def test_filter_by_mood(client):
    client.post("/notes", json={"text": "차분한 하루", "mood": "calm"})
    client.post("/notes", json={"text": "신나는 하루", "mood": "excited"})
    client.post("/notes", json={"text": "또 차분한 하루", "mood": "calm"})

    resp = client.get("/notes", params={"mood": "calm"})
    assert resp.status_code == 200
    notes = resp.json()
    assert len(notes) == 2
    assert all(note["mood"] == "calm" for note in notes)


def test_create_note_requires_text_and_mood(client):
    resp = client.post("/notes", json={"text": "", "mood": "calm"})
    assert resp.status_code == 422
