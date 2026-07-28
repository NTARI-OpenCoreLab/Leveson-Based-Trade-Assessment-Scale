#!/usr/bin/env python3
"""
LBTAS API — event store
========================

Persists individual rating events to a local SQLite file (stdlib sqlite3,
no external dependency), per CLAUDE.md's data model: the store keeps
individual rating events, not running tallies, and reads compute
distributions on the fly. Persistence stays local (no third-party data
store), matching CLAUDE.md's "Storing ratings locally" requirement.

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import sqlite3
from typing import Optional

DEFAULT_DB_PATH = "lbtas_events.db"


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _init_db(conn)
    return conn


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS rating_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exchange_id TEXT NOT NULL,
            rater TEXT NOT NULL,
            rated_party TEXT NOT NULL,
            category TEXT,
            value INTEGER NOT NULL,
            comment TEXT,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()


def insert_event(
    conn: sqlite3.Connection,
    exchange_id: str,
    rater: str,
    rated_party: str,
    category: Optional[str],
    value: int,
    comment: Optional[str],
    timestamp: str,
) -> None:
    conn.execute(
        """
        INSERT INTO rating_events (exchange_id, rater, rated_party, category, value, comment, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (exchange_id, rater, rated_party, category, value, comment, timestamp),
    )
    conn.commit()


def get_events_for_party(conn: sqlite3.Connection, rated_party: str) -> list[sqlite3.Row]:
    cursor = conn.execute(
        "SELECT * FROM rating_events WHERE rated_party = ? ORDER BY timestamp",
        (rated_party,),
    )
    return cursor.fetchall()
