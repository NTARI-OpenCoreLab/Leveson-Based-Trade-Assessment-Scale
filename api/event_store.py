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

import os
import sqlite3
from typing import Optional

# CWD-relative paths make the DB location depend on where uvicorn is started
# from; an absolute default removes that ambiguity. Still overridable via env.
DEFAULT_DB_PATH = os.environ.get(
    "LBTAS_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "lbtas_events.db")
)


class DuplicateRatingError(Exception):
    """Raised when (exchange_id, rater, rated_party) has already been submitted.

    One rating per direction per exchange (CLAUDE.md's data model treats the
    count itself as a trust signal, so repeat submissions must not inflate it).
    """


class EventNotFoundError(Exception):
    """Raised when a dismissal targets a rating event id that doesn't exist."""


class AlreadyDismissedError(Exception):
    """Raised on a second dismissal attempt, or an uphold/contest against an
    already-dismissed event — an adjudicator has already ruled.

    SPEC.md §6: a dismissal is a one-time adjudication, recorded as a new
    annotation — never an edit, and never repeatable against the same event.
    """


class AlreadyContestedError(Exception):
    """Raised on a second contest attempt against the same event (SPEC.md §5:
    one open contest per event)."""


class ContestNotFoundError(Exception):
    """Raised when an uphold references an event with no contest on record."""


class AlreadyUpheldError(Exception):
    """Raised on a second uphold attempt against the same contest."""


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
            role TEXT NOT NULL,
            category TEXT,
            value INTEGER NOT NULL CHECK (value BETWEEN -1 AND 4),
            comment TEXT,
            timestamp TEXT NOT NULL,
            UNIQUE (exchange_id, rater, rated_party)
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_rating_events_party_role ON rating_events (rated_party, role)"
    )
    # SPEC.md §4/§6: a dismissal annotates, never erases. It is its own
    # append-only record referencing the original event, never an edit or
    # delete against rating_events. One dismissal per event (UNIQUE).
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS dismissals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL REFERENCES rating_events(id),
            dismissed_by TEXT NOT NULL,
            reason TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            UNIQUE (event_id)
        )
        """
    )
    # SPEC.md §5: symmetric, contestable both ways — any rated party may
    # contest a rating made against them. One open contest per event.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS contests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL REFERENCES rating_events(id),
            contested_by TEXT NOT NULL,
            reason TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            UNIQUE (event_id)
        )
        """
    )
    # SPEC.md §6: an adjudicator may uphold a contested rating instead of
    # dismissing it — the rating stands, but reads must surface that it was
    # contested-and-upheld. Its own append-only table, same shape as dismissals.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS upholds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER NOT NULL REFERENCES rating_events(id),
            upheld_by TEXT NOT NULL,
            reason TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            UNIQUE (event_id)
        )
        """
    )
    conn.commit()


def insert_event(
    conn: sqlite3.Connection,
    exchange_id: str,
    rater: str,
    rated_party: str,
    role: str,
    category: Optional[str],
    value: int,
    comment: Optional[str],
    timestamp: str,
) -> None:
    try:
        conn.execute(
            """
            INSERT INTO rating_events (exchange_id, rater, rated_party, role, category, value, comment, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (exchange_id, rater, rated_party, role, category, value, comment, timestamp),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise DuplicateRatingError(
                f"A rating from '{rater}' for '{rated_party}' on exchange '{exchange_id}' already exists."
            ) from e
        raise


def get_events_for_party_role(conn: sqlite3.Connection, rated_party: str, role: str) -> list[sqlite3.Row]:
    """Active (non-dismissed) events for a rated party, scoped to a single role.
    Each row carries contest/uphold columns (NULL when not contested), so a
    contested-but-upheld rating can be surfaced as such (SPEC.md §6) without a
    second query.

    Role-scoped per SPEC.md §3: a -1 earned in one role must never contaminate
    the distribution of another role. Excludes dismissed events per SPEC.md §6
    ("a read computes the active distribution excluding dismissed events");
    use get_dismissed_events_for_party_role to surface those separately.
    """
    cursor = conn.execute(
        """
        SELECT re.*,
               c.contested_by AS contested_by, c.reason AS contest_reason, c.timestamp AS contested_at,
               u.upheld_by AS upheld_by, u.reason AS uphold_reason, u.timestamp AS upheld_at
        FROM rating_events re
        LEFT JOIN dismissals d ON d.event_id = re.id
        LEFT JOIN contests c ON c.event_id = re.id
        LEFT JOIN upholds u ON u.event_id = re.id
        WHERE re.rated_party = ? AND re.role = ? AND d.event_id IS NULL
        ORDER BY re.timestamp
        """,
        (rated_party, role),
    )
    return cursor.fetchall()


def get_dismissed_events_for_party_role(
    conn: sqlite3.Connection, rated_party: str, role: str
) -> list[sqlite3.Row]:
    """Dismissed events for a rated party/role, each row carrying its dismissal
    annotation (dismissed_by, dismissal_reason, dismissed_at). SPEC.md §4/§6:
    a dismissal MUST NOT hide the event — it stays visible downstream, just
    excluded from the active distribution above.
    """
    cursor = conn.execute(
        """
        SELECT re.*, d.dismissed_by AS dismissed_by, d.reason AS dismissal_reason,
               d.timestamp AS dismissed_at
        FROM rating_events re
        JOIN dismissals d ON d.event_id = re.id
        WHERE re.rated_party = ? AND re.role = ?
        ORDER BY re.timestamp
        """,
        (rated_party, role),
    )
    return cursor.fetchall()


def dismiss_event(
    conn: sqlite3.Connection,
    event_id: int,
    dismissed_by: str,
    reason: str,
    timestamp: str,
) -> None:
    """Record a dismissal against an existing rating event. Never edits or
    deletes the original event (SPEC.md §4/§6) — only adds an annotation
    that excludes it from the active distribution on read.

    Deliberately independent of contest/uphold state: dismissal was designed
    (and remains usable) as a standalone adjudicator action that doesn't
    require a prior contest, so an already-upheld event can still later be
    dismissed. Not locking that combination is an intentional scope choice,
    not an oversight — flag it if the two should become mutually exclusive.
    """
    row = conn.execute("SELECT id FROM rating_events WHERE id = ?", (event_id,)).fetchone()
    if row is None:
        raise EventNotFoundError(f"No rating event with id {event_id}")

    try:
        conn.execute(
            "INSERT INTO dismissals (event_id, dismissed_by, reason, timestamp) VALUES (?, ?, ?, ?)",
            (event_id, dismissed_by, reason, timestamp),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise AlreadyDismissedError(f"Rating event {event_id} has already been dismissed") from e


def _is_dismissed(conn: sqlite3.Connection, event_id: int) -> bool:
    return conn.execute("SELECT 1 FROM dismissals WHERE event_id = ?", (event_id,)).fetchone() is not None


def contest_event(
    conn: sqlite3.Connection,
    event_id: int,
    contested_by: str,
    reason: str,
    timestamp: str,
) -> None:
    """Record that the rated party is contesting a rating made against them
    (SPEC.md §5). Symmetric by construction: this takes whatever event_id is
    given, with no check on which "side" is contesting — the covenant runs
    both ways, and the API encodes no privileged direction. One open contest
    per event."""
    row = conn.execute("SELECT id FROM rating_events WHERE id = ?", (event_id,)).fetchone()
    if row is None:
        raise EventNotFoundError(f"No rating event with id {event_id}")

    if _is_dismissed(conn, event_id):
        raise AlreadyDismissedError(
            f"Rating event {event_id} was already dismissed; nothing left to contest"
        )

    try:
        conn.execute(
            "INSERT INTO contests (event_id, contested_by, reason, timestamp) VALUES (?, ?, ?, ?)",
            (event_id, contested_by, reason, timestamp),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise AlreadyContestedError(f"Rating event {event_id} has already been contested") from e


def uphold_contest(
    conn: sqlite3.Connection,
    event_id: int,
    upheld_by: str,
    reason: str,
    timestamp: str,
) -> None:
    """Adjudicator resolution: the rating stands. Recorded as its own
    append-only annotation (never edits the contest or the rating event) so
    reads can surface "contested, and upheld" per SPEC.md §6."""
    contest_row = conn.execute("SELECT id FROM contests WHERE event_id = ?", (event_id,)).fetchone()
    if contest_row is None:
        raise ContestNotFoundError(f"No contest on record for rating event {event_id}")

    if _is_dismissed(conn, event_id):
        raise AlreadyDismissedError(
            f"Rating event {event_id} was already dismissed; cannot also uphold it"
        )

    try:
        conn.execute(
            "INSERT INTO upholds (event_id, upheld_by, reason, timestamp) VALUES (?, ?, ?, ?)",
            (event_id, upheld_by, reason, timestamp),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise AlreadyUpheldError(f"Rating event {event_id} has already been upheld") from e
