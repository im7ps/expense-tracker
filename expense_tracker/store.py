"""Salvataggio dei movimenti in SQLite (libreria standard)."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path

from expense_tracker.normalize import Movement

SCHEMA = """
CREATE TABLE IF NOT EXISTS movements (
    id INTEGER PRIMARY KEY,
    source_file TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    amount_cents INTEGER NOT NULL,
    category TEXT NOT NULL
)
"""


def connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA)
    return conn


def replace_source(conn: sqlite3.Connection, source_file: str, movements: Iterable[Movement]) -> int:
    """Sostituisce i movimenti già salvati per quel file: reimportare non duplica."""
    rows = [
        (source_file, m.date, m.description, m.amount_cents, m.category) for m in movements
    ]
    with conn:
        conn.execute("DELETE FROM movements WHERE source_file = ?", (source_file,))
        conn.executemany(
            "INSERT INTO movements (source_file, date, description, amount_cents, category) "
            "VALUES (?, ?, ?, ?, ?)",
            rows,
        )
    return len(rows)


def load_movements(conn: sqlite3.Connection) -> list[Movement]:
    rows = conn.execute(
        "SELECT date, description, amount_cents, category FROM movements ORDER BY date, id"
    )
    return [
        Movement(date=date, description=description, amount_cents=amount, category=category)
        for date, description, amount, category in rows
    ]
