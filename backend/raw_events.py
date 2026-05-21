import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).with_name("memory.sqlite3")


CREATE_RAW_EVENTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw_events (
    id TEXT PRIMARY KEY,
    role TEXT NOT NULL CHECK (role IN ('human', 'ai', 'system', 'tool')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    session_id TEXT NOT NULL,
    metadata_json TEXT,
    modified_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def get_connection(db_path: str | Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def create_table(db_path: str | Path = DB_PATH) -> None:
    """Create the raw_events table if it does not already exist."""
    with get_connection(db_path) as conn:
        conn.execute(CREATE_RAW_EVENTS_TABLE_SQL)
        conn.commit()


def upsert_raw_event(
    *,
    id: str,
    role: str,
    content: str,
    session_id: str,
    created_at: str | None = None,
    modified_at: str | None = None,
    metadata_json: str | None = None,
    db_path: str | Path = DB_PATH,
) -> None:
    """Insert or update a raw event by id."""
    create_table(db_path)

    if modified_at is None:
        modified_at = datetime.now().isoformat()

    if created_at is None:
        sql = """
        INSERT INTO raw_events (id, role, content, session_id, metadata_json, modified_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            role = excluded.role,
            content = excluded.content,
            session_id = excluded.session_id,
            metadata_json = excluded.metadata_json,
            modified_at = excluded.modified_at;
        """
        params: tuple[Any, ...] = (
            id,
            role,
            content,
            session_id,
            metadata_json,
            modified_at,
        )
    else:
        sql = """
        INSERT INTO raw_events (id, role, content, created_at, session_id, metadata_json, modified_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            role = excluded.role,
            content = excluded.content,
            created_at = excluded.created_at,
            session_id = excluded.session_id,
            metadata_json = excluded.metadata_json,
            modified_at = excluded.modified_at;
        """
        params = (id, role, content, created_at, session_id, metadata_json, modified_at)

    with get_connection(db_path) as conn:
        conn.execute(sql, params)
        conn.commit()


def get_all_raw_events(db_path: str | Path = DB_PATH) -> list[dict[str, Any]]:
    """Return all raw events ordered by creation time."""
    create_table(db_path)

    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT id, role, content, created_at, session_id, metadata_json, modified_at "
            "FROM raw_events ORDER BY created_at ASC"
        ).fetchall()
        return [dict(row) for row in rows]

def get_all_raw_events_desc(db_path: str | Path = DB_PATH) -> list[dict[str, Any]]:
    """Return all raw events ordered by creation time."""
    create_table(db_path)

    with get_connection(db_path) as conn:
        rows = conn.execute(
            "SELECT id, role, content, created_at, session_id, metadata_json, modified_at "
            "FROM raw_events ORDER BY modified_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]