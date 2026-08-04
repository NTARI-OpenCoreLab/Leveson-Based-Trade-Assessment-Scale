#!/usr/bin/env python3
"""
LBTAS API — entry point
========================

Minimal FastAPI app. This is the starting scaffold for the networked API
described in CLAUDE.md ("What the API does"). POST /ratings runs a submission
through the -1 comment validation rule and persists it (rejecting a repeat
submission for the same exchange/rater/rated_party with 409); GET
/ratings/{rated_party}/{role} reads back a distribution (never an average)
plus first/last rated timestamps and a transaction count, per CLAUDE.md's
"Reading and reporting reputation" and "data model" sections. Reads are
role-scoped per SPEC.md §3: a rating earned in one role must never
contaminate another role's distribution.

Events persist to a local SQLite file (api/event_store.py) so ratings survive
a restart, per CLAUDE.md's "Storing ratings locally" requirement.

Reads are gated behind LBTAS_API_KEY (see require_api_key below) so an
unconfigured deployment fails closed, per CLAUDE.md's authorization section.
Writes are not yet gated — CLAUDE.md treats submission and review as separate
capabilities, and only the read side was flagged as unauthorized in review;
gating submission is a separate, not-yet-built piece. Running this on
NTARIHQ is likewise separate.

POST /ratings/{event_id}/dismiss lets an adjudicator dismiss a bad-faith
rating (SPEC.md §4, §6): the dismissal is its own append-only annotation,
never an edit or delete of the original event. GET /ratings/{party}/{role}
computes its distribution from active (non-dismissed) events only, but
always surfaces every dismissed event alongside it, with who dismissed it
and why — dismissal forgives, it does not hide. There is no distinct
adjudicator identity yet; dismissal is gated behind the same LBTAS_API_KEY
as reads, which is coarser than SPEC.md's "operator-local adjudicator role."

POST /ratings/{event_id}/contest lets the rated party dispute a rating made
against them, in either direction (SPEC.md §5 — the covenant is symmetric,
no privileged side); it is ungated, like POST /ratings, since it's the rated
party exercising their own right rather than a privileged review. POST
/ratings/{event_id}/uphold is the adjudicator's other resolution besides
dismissal: the rating stands, but GET marks it "contested" and "upheld" (with
who and why) rather than silently leaving it looking unquestioned.

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import os
import secrets
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from . import event_store
from .rating_validation import RatingValidationError, validate_rating_submission

app = FastAPI(title="LBTAS API", version="2.0.0")

API_KEY_ENV_VAR = "LBTAS_API_KEY"


def require_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    """Fail-closed read gate: with no key configured, every read is denied —
    never falls open. Compares with secrets.compare_digest to avoid a timing
    side-channel on the key check."""
    configured_key = os.environ.get(API_KEY_ENV_VAR)
    if not configured_key:
        raise HTTPException(
            status_code=503,
            detail=f"Reads are not available: {API_KEY_ENV_VAR} is not configured on this deployment.",
        )
    if not x_api_key or not secrets.compare_digest(x_api_key, configured_key):
        raise HTTPException(status_code=401, detail="Missing or invalid API key.")


class RatingSubmission(BaseModel):
    exchange_id: str = Field(..., description="Triggering exchange/transaction id")
    rater: str = Field(..., description="Party submitting the rating")
    rated_party: str = Field(..., description="Party being rated")
    # Deliberately free text, not a closed enum: SPEC.md §3 gives named examples
    # (market_seller/market_buyer, service_provider/service_client,
    # plan_producer/plan_backer) as "e.g.", derived from the exchange type,
    # which this API does not own or enumerate. A typo here silently opens a
    # fresh, empty reputation bucket rather than erroring — accepted as an
    # operator-layer concern (exchange-type validation belongs upstream of
    # this API, same division CONFORMANCE.md draws for the rest of the
    # covenant lifecycle), not a gap to close with a hardcoded vocabulary here.
    role: str = Field(
        ...,
        min_length=1,
        description="Capacity the rated party acted in, e.g. 'market_seller', 'market_buyer' (SPEC.md §3); open vocabulary, not validated here",
    )
    category: Optional[str] = None
    value: int = Field(..., description="Rating value, -1 to +4")
    comment: Optional[str] = Field(
        None, description="Justifying comment; mandatory and <=500 words when value is -1"
    )


class DismissalRequest(BaseModel):
    dismissed_by: str = Field(..., min_length=1, description="The adjudicator dismissing this rating")
    reason: str = Field(..., min_length=1, description="Why the rating is bad-faith / being dismissed")


class ContestRequest(BaseModel):
    contested_by: str = Field(..., min_length=1, description="The rated party contesting this rating")
    reason: str = Field(..., min_length=1, description="Why the rating is being disputed")


class UpholdRequest(BaseModel):
    upheld_by: str = Field(..., min_length=1, description="The adjudicator upholding this rating")
    reason: str = Field(..., min_length=1, description="Why the contest was rejected and the rating stands")


def _new_distribution() -> dict:
    return {str(level): 0 for level in (-1, 0, 1, 2, 3, 4)}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ratings", status_code=201)
def submit_rating(submission: RatingSubmission) -> dict:
    try:
        validate_rating_submission(submission.value, submission.comment)
    except RatingValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    event = submission.model_dump()
    event["timestamp"] = datetime.now(timezone.utc).isoformat()

    conn = event_store.get_connection()
    try:
        event_store.insert_event(
            conn,
            exchange_id=event["exchange_id"],
            rater=event["rater"],
            rated_party=event["rated_party"],
            role=event["role"],
            category=event["category"],
            value=event["value"],
            comment=event["comment"],
            timestamp=event["timestamp"],
        )
    except event_store.DuplicateRatingError as e:
        raise HTTPException(status_code=409, detail=str(e))
    finally:
        conn.close()

    return {"status": "accepted", "submission": event}


@app.post("/ratings/{event_id}/dismiss", dependencies=[Depends(require_api_key)])
def dismiss_rating(event_id: int, dismissal: DismissalRequest) -> dict:
    """Adjudicator dismissal (SPEC.md §4, §6): annotates, never erases. Removes
    the event from the active distribution on read, but the event and this
    annotation both stay permanently visible via GET's "dismissed" list."""
    timestamp = datetime.now(timezone.utc).isoformat()

    conn = event_store.get_connection()
    try:
        event_store.dismiss_event(
            conn,
            event_id=event_id,
            dismissed_by=dismissal.dismissed_by,
            reason=dismissal.reason,
            timestamp=timestamp,
        )
    except event_store.EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except event_store.AlreadyDismissedError as e:
        raise HTTPException(status_code=409, detail=str(e))
    finally:
        conn.close()

    return {
        "status": "dismissed",
        "event_id": event_id,
        "dismissed_by": dismissal.dismissed_by,
        "reason": dismissal.reason,
        "timestamp": timestamp,
    }


@app.post("/ratings/{event_id}/contest")
def contest_rating(event_id: int, contest: ContestRequest) -> dict:
    """The rated party disputes a rating made against them (SPEC.md §5).
    Ungated, unlike dismiss/uphold: this is the rated party's own right, not
    an adjudicator action — same posture as POST /ratings, which is also not
    yet gated behind per-party auth."""
    timestamp = datetime.now(timezone.utc).isoformat()

    conn = event_store.get_connection()
    try:
        event_store.contest_event(
            conn,
            event_id=event_id,
            contested_by=contest.contested_by,
            reason=contest.reason,
            timestamp=timestamp,
        )
    except event_store.EventNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (event_store.AlreadyDismissedError, event_store.AlreadyContestedError) as e:
        raise HTTPException(status_code=409, detail=str(e))
    finally:
        conn.close()

    return {
        "status": "contested",
        "event_id": event_id,
        "contested_by": contest.contested_by,
        "reason": contest.reason,
        "timestamp": timestamp,
    }


@app.post("/ratings/{event_id}/uphold", dependencies=[Depends(require_api_key)])
def uphold_rating(event_id: int, uphold: UpholdRequest) -> dict:
    """Adjudicator resolution: the contest is rejected and the rating stands
    (SPEC.md §6). Requires an existing contest on this event (404 if none);
    GET then marks the event "contested" and "upheld" rather than letting it
    look unquestioned."""
    timestamp = datetime.now(timezone.utc).isoformat()

    conn = event_store.get_connection()
    try:
        event_store.uphold_contest(
            conn,
            event_id=event_id,
            upheld_by=uphold.upheld_by,
            reason=uphold.reason,
            timestamp=timestamp,
        )
    except event_store.ContestNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (event_store.AlreadyDismissedError, event_store.AlreadyUpheldError) as e:
        raise HTTPException(status_code=409, detail=str(e))
    finally:
        conn.close()

    return {
        "status": "upheld",
        "event_id": event_id,
        "upheld_by": uphold.upheld_by,
        "reason": uphold.reason,
        "timestamp": timestamp,
    }


@app.get("/ratings/{rated_party}/{role}", dependencies=[Depends(require_api_key)])
def read_ratings(rated_party: str, role: str) -> dict:
    """Role-scoped read (SPEC.md §3): a -1 earned as e.g. market_seller must never
    show up in, or be averaged into, the rated party's market_buyer distribution.

    The distribution/total/timestamps below reflect only active (non-dismissed)
    events (SPEC.md §6). Dismissed events are never omitted from the response
    entirely — they're always listed under "dismissed", annotated with who
    dismissed them and why, even if that leaves no active events at all.
    """
    conn = event_store.get_connection()
    try:
        active_rows = event_store.get_events_for_party_role(conn, rated_party, role)
        dismissed_rows = event_store.get_dismissed_events_for_party_role(conn, rated_party, role)
    finally:
        conn.close()

    if not active_rows and not dismissed_rows:
        raise HTTPException(
            status_code=404, detail=f"No ratings found for '{rated_party}' in role '{role}'"
        )

    distribution = _new_distribution()
    for row in active_rows:
        distribution[str(row["value"])] += 1

    events = []
    for row in active_rows:
        event = {
            "event_id": row["id"],
            "value": row["value"],
            "category": row["category"],
            "comment": row["comment"],
            "exchange_id": row["exchange_id"],
            "rater": row["rater"],
            "rated_at": row["timestamp"],
            "contested": row["contested_by"] is not None,
        }
        if row["contested_by"] is not None:
            event["contested_by"] = row["contested_by"]
            event["contest_reason"] = row["contest_reason"]
            event["contested_at"] = row["contested_at"]
            event["upheld"] = row["upheld_by"] is not None
            # SPEC.md §6: surface that a contested rating was upheld, not just
            # that it was contested — a pending contest and a resolved one
            # must not look the same.
            if row["upheld_by"] is not None:
                event["upheld_by"] = row["upheld_by"]
                event["uphold_reason"] = row["uphold_reason"]
                event["upheld_at"] = row["upheld_at"]
        events.append(event)

    dismissed = [
        {
            "event_id": row["id"],
            "value": row["value"],
            "category": row["category"],
            "comment": row["comment"],
            "exchange_id": row["exchange_id"],
            "rater": row["rater"],
            "rated_at": row["timestamp"],
            "dismissed_by": row["dismissed_by"],
            "reason": row["dismissal_reason"],
            "dismissed_at": row["dismissed_at"],
        }
        for row in dismissed_rows
    ]

    result = {
        "rated_party": rated_party,
        "role": role,
        "distribution": distribution,
        "total": len(active_rows),
        "events": events,
        "dismissed_count": len(dismissed),
        "dismissed": dismissed,
    }

    if active_rows:
        timestamps = [row["timestamp"] for row in active_rows]
        exchange_ids = {row["exchange_id"] for row in active_rows}
        result["first_rated_at"] = min(timestamps)
        result["last_rated_at"] = max(timestamps)
        result["transaction_count"] = len(exchange_ids)
    else:
        result["first_rated_at"] = None
        result["last_rated_at"] = None
        result["transaction_count"] = 0

    return result
