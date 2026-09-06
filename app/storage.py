"""SQLite-backed storage for mood notes.

Everything that touches the database lives here, so the rest of the app
(and anyone reading it) never has to think about SQL. A single connection
is opened when a MoodStore is created and kept alive for its lifetime -
that works fine both for the on-disk moodboard.db file and for an
in-memory database used in tests.
"""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timezone
from typing import Optional

_SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    mood TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def _utc_now_iso() -> str:
    """UTC timestamp in ISO 8601, e.g. 2026-09-06T09:12:03.512481+00:00."""
    return datetime.now(timezone.utc).isoformat()


class MoodStore:
    """Small wrapper around a single SQLite connection.

    This is a personal side project, not a database layer meant to scale -
    one connection guarded by a lock is plenty for one person jotting down
    a mood a few times a day.
    """

    def __init__(self, db_path: str = "moodboard.db") -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        # check_same_thread=False because FastAPI may run sync path
        # operations in a worker thread; the lock keeps access serialized.
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            self._conn.execute(_SCHEMA)
            self._conn.commit()

    def create_note(self, text: str, mood: str) -> dict:
        created_at = _utc_now_iso()
        with self._lock:
            cursor = self._conn.execute(
                "INSERT INTO notes (text, mood, created_at) VALUES (?, ?, ?)",
                (text, mood, created_at),
            )
            self._conn.commit()
            note_id = cursor.lastrowid
        return {"id": note_id, "text": text, "mood": mood, "created_at": created_at}

    def list_notes(self, mood: Optional[str] = None) -> list[dict]:
        with self._lock:
            if mood is not None:
                rows = self._conn.execute(
                    "SELECT id, text, mood, created_at FROM notes "
                    "WHERE mood = ? ORDER BY id DESC",
                    (mood,),
                ).fetchall()
            else:
                rows = self._conn.execute(
                    "SELECT id, text, mood, created_at FROM notes ORDER BY id DESC"
                ).fetchall()
        return [dict(row) for row in rows]

    def get_note(self, note_id: int) -> Optional[dict]:
        with self._lock:
            row = self._conn.execute(
                "SELECT id, text, mood, created_at FROM notes WHERE id = ?",
                (note_id,),
            ).fetchone()
        return dict(row) if row else None

    def delete_note(self, note_id: int) -> bool:
        with self._lock:
            cursor = self._conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            self._conn.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        with self._lock:
            self._conn.close()
