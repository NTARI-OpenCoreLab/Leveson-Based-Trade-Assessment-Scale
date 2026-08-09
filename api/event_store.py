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
from datetime import datetime, timedelta
from typing import Optional

# CWD-relative paths make the DB location depend on where uvicorn is started
# from; an absolute default removes that ambiguity. Still overridable via env.
DEFAULT_DB_PATH = os.environ.get(
    "LBTAS_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "lbtas_events.db")
)

# SPEC.md §7: +2 ("Basic Satisfaction") is the conservative timeout default
# (it does not inflate reputation); +3 is the documented alternative. This is
# the only tunable constant in the scale.
TIMEOUT_DEFAULT_RATING = 2


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


class NotRatedPartyError(Exception):
    """Raised when contested_by doesn't match the event's rated_party.

    SPEC.md §5 grants the contest right to "any rated party" contesting "a
    rating made against them" — not to arbitrary third parties. Without this
    check, anyone could burn the one-contest-per-event slot with a junk
    reason and permanently lock the real rated party out (an uphold then
    cements it). Identity is still self-asserted until writes are
    authenticated, but this at least encodes the spec's semantic.
    """


class InvalidExchangePartyError(Exception):
    """Raised when a rating's (rater, rated_party, role) doesn't match either
    of a registered exchange's two directions (SPEC.md §7's
    party_a/role_a/party_b/role_b) — role is pinned too, not just the party
    pair, so a real pair can't slip through under the wrong role and misfile
    into the wrong §3 bucket. Unregistered exchanges skip this check and keep
    the prior permissive behavior — this only applies once an exchange has
    been registered.
    """


class ContestNotFoundError(Exception):
    """Raised when an uphold references an event with no contest on record."""


class AlreadyUpheldError(Exception):
    """Raised on a second uphold attempt against the same contest."""


class ExchangeNotFoundError(Exception):
    """Raised when apply_timeout_defaults targets an unregistered exchange_id."""


class ExchangeAlreadyExistsError(Exception):
    """Raised on registering an exchange_id that's already registered."""


class TimeoutAlreadyAppliedError(Exception):
    """Raised on a real rating submission for an (exchange_id, rated_party)
    direction that already has a system-attributed timeout default.

    SPEC.md §7 doesn't say what happens if a party rates late, after the
    window already closed and a default was recorded — but allowing it would
    silently double-count that direction (both the +2 default and the late
    real rating would sit in the distribution together). Rejecting it keeps
    one rating (real or default) per exchange per direction, consistent with
    the DuplicateRatingError invariant everywhere else in this store.
    """


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
            rater_role TEXT NOT NULL DEFAULT 'party' CHECK (rater_role IN ('party', 'system')),
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
    # SPEC.md §7: an exchange has two rating directions (party_a rates
    # party_b in role_b, and party_b rates party_a in role_a). Registering
    # one is what starts its rating window; apply_timeout_defaults checks
    # this row to decide whether either direction is overdue.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS exchanges (
            exchange_id TEXT PRIMARY KEY,
            completed_at TEXT NOT NULL,
            rating_window_seconds INTEGER NOT NULL,
            party_a TEXT NOT NULL,
            role_a TEXT NOT NULL,
            party_b TEXT NOT NULL,
            role_b TEXT NOT NULL
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
    rater_role: str = "party",
) -> None:
    # SPEC.md §7: a real ("party") rating arriving after a timeout default
    # already filled this exact direction would double-count it (both the
    # default and the late rating in the same distribution). The system's
    # own default insert (rater_role="system") skips this check — it's the
    # one thing allowed to occupy that slot when nothing else has.
    #
    # NOTE: this is check-then-insert against a fresh connection per call, not
    # inside a transaction — two concurrent requests for the same direction
    # could both pass this check before either commits. Not addressed here
    # (fine at this scale); a real fix would wrap the check+insert in
    # `BEGIN IMMEDIATE` to serialize it.
    if rater_role == "party":
        existing_default = conn.execute(
            "SELECT 1 FROM rating_events WHERE exchange_id = ? AND rated_party = ? AND rater_role = 'system'",
            (exchange_id, rated_party),
        ).fetchone()
        if existing_default:
            raise TimeoutAlreadyAppliedError(
                f"Exchange '{exchange_id}' already has a timeout default for '{rated_party}'; "
                "the rating window has closed."
            )

        # SPEC.md §7: once an exchange is registered, a rating must come from
        # one of its two actual directions, IN the role that direction is
        # actually registered under — pinning (rater, rated_party) alone
        # would let a real pair through under the wrong role and misfile it
        # into the wrong bucket, the same §3 mixup this check exists to
        # prevent. Unregistered exchanges are left permissive (this API
        # doesn't require registration before rating).
        exchange = get_exchange(conn, exchange_id)
        if exchange is not None:
            valid_directions = {
                (exchange["party_b"], exchange["party_a"], exchange["role_a"]),
                (exchange["party_a"], exchange["party_b"], exchange["role_b"]),
            }
            if (rater, rated_party, role) not in valid_directions:
                raise InvalidExchangePartyError(
                    f"'{rater}' rating '{rated_party}' as '{role}' doesn't match either registered "
                    f"direction for exchange '{exchange_id}'"
                )

    try:
        conn.execute(
            """
            INSERT INTO rating_events (exchange_id, rater, rated_party, role, category, value, comment, timestamp, rater_role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (exchange_id, rater, rated_party, role, category, value, comment, timestamp, rater_role),
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
    (SPEC.md §5). Symmetric by construction: this doesn't care which "side"
    (producer or consumer, buyer or seller) the rated_party happens to be —
    the covenant runs both ways, no privileged direction — but it does
    require contested_by to actually BE that event's rated_party. One open
    contest per event."""
    row = conn.execute("SELECT id, rated_party FROM rating_events WHERE id = ?", (event_id,)).fetchone()
    if row is None:
        raise EventNotFoundError(f"No rating event with id {event_id}")

    if contested_by != row["rated_party"]:
        raise NotRatedPartyError(
            f"Only the rated party ('{row['rated_party']}') may contest rating event {event_id}, "
            f"not '{contested_by}'"
        )

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


def register_exchange(
    conn: sqlite3.Connection,
    exchange_id: str,
    completed_at: str,
    rating_window_seconds: int,
    party_a: str,
    role_a: str,
    party_b: str,
    role_b: str,
) -> None:
    """Register an exchange's two rating directions and start its rating
    window (SPEC.md §7): party_b is expected to rate party_a (in role_a),
    and party_a is expected to rate party_b (in role_b)."""
    try:
        conn.execute(
            """
            INSERT INTO exchanges (exchange_id, completed_at, rating_window_seconds, party_a, role_a, party_b, role_b)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (exchange_id, completed_at, rating_window_seconds, party_a, role_a, party_b, role_b),
        )
        conn.commit()
    except sqlite3.IntegrityError as e:
        raise ExchangeAlreadyExistsError(f"Exchange '{exchange_id}' is already registered") from e


def get_exchange(conn: sqlite3.Connection, exchange_id: str) -> Optional[sqlite3.Row]:
    return conn.execute("SELECT * FROM exchanges WHERE exchange_id = ?", (exchange_id,)).fetchone()


def apply_timeout_defaults(conn: sqlite3.Connection, exchange_id: str, now: datetime) -> dict:
    """Backfill a system-attributed +2 (SPEC.md §7) for any direction of
    `exchange_id` still unrated once its rating window has elapsed.

    Idempotent and safe to call repeatedly — there's no background worker in
    this API, so a real deployment calls this from an external scheduler
    (e.g. cron hitting the endpoint that wraps this). A direction that
    already has any rating at all, real or a prior default, is left alone.
    """
    exchange = get_exchange(conn, exchange_id)
    if exchange is None:
        raise ExchangeNotFoundError(f"No exchange registered with id '{exchange_id}'")

    completed_at = datetime.fromisoformat(exchange["completed_at"])
    due_at = completed_at + timedelta(seconds=exchange["rating_window_seconds"])
    if now < due_at:
        return {"status": "not_due", "due_at": due_at.isoformat(), "defaulted": []}

    directions = [
        (exchange["party_a"], exchange["role_a"]),
        (exchange["party_b"], exchange["role_b"]),
    ]

    defaulted = []
    timestamp = now.isoformat()
    for rated_party, role in directions:
        # Same check-then-insert race noted in insert_event: two concurrent
        # apply-timeouts calls (or one racing a late real submission) could
        # both see "not yet rated" before either writes. Not addressed here.
        already_rated = conn.execute(
            "SELECT 1 FROM rating_events WHERE exchange_id = ? AND rated_party = ?",
            (exchange_id, rated_party),
        ).fetchone()
        if already_rated:
            continue

        insert_event(
            conn,
            exchange_id=exchange_id,
            rater="system",
            rated_party=rated_party,
            role=role,
            category=None,
            value=TIMEOUT_DEFAULT_RATING,
            comment=None,
            timestamp=timestamp,
            rater_role="system",
        )
        defaulted.append(rated_party)

    return {"status": "processed", "due_at": due_at.isoformat(), "defaulted": defaulted}
