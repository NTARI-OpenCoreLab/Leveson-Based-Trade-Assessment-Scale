#!/usr/bin/env python3
"""
LBTAS API — entry point
========================

Minimal FastAPI app. This is the starting scaffold for the networked API
described in CLAUDE.md ("What the API does"). POST /ratings runs a submission
through the -1 comment validation rule and persists it; GET /ratings/{rated_party}/{role}
reads back a distribution (never an average) plus first/last rated timestamps
and a transaction count, per CLAUDE.md's "Reading and reporting reputation"
and "data model" sections. Reads are role-scoped per SPEC.md §3: a rating
earned in one role must never contaminate another role's distribution.

Events persist to a local SQLite file (api/event_store.py) so ratings survive
a restart, per CLAUDE.md's "Storing ratings locally" requirement. There is no
authorization layer yet — that, and running this on NTARIHQ, are separate,
not-yet-built pieces.

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from api import event_store
from api.rating_validation import RatingValidationError, validate_rating_submission

app = FastAPI(title="LBTAS API", version="2.0.0")


class RatingSubmission(BaseModel):
    exchange_id: str = Field(..., description="Triggering exchange/transaction id")
    rater: str = Field(..., description="Party submitting the rating")
    rated_party: str = Field(..., description="Party being rated")
    role: str = Field(
        ..., description="Capacity the rated party acted in, e.g. 'market_seller', 'market_buyer' (SPEC.md §3)"
    )
    category: Optional[str] = None
    value: int = Field(..., description="Rating value, -1 to +4")
    comment: Optional[str] = Field(
        None, description="Justifying comment; mandatory and <=500 words when value is -1"
    )


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
    finally:
        conn.close()

    return {"status": "accepted", "submission": event}


@app.get("/ratings/{rated_party}/{role}")
def read_ratings(rated_party: str, role: str) -> dict:
    """Role-scoped read (SPEC.md §3): a -1 earned as e.g. market_seller must never
    show up in, or be averaged into, the rated party's market_buyer distribution."""
    conn = event_store.get_connection()
    try:
        rows = event_store.get_events_for_party_role(conn, rated_party, role)
    finally:
        conn.close()

    if not rows:
        raise HTTPException(
            status_code=404, detail=f"No ratings found for '{rated_party}' in role '{role}'"
        )

    distribution = _new_distribution()
    for row in rows:
        distribution[str(row["value"])] += 1

    timestamps = [row["timestamp"] for row in rows]
    exchange_ids = {row["exchange_id"] for row in rows}

    return {
        "rated_party": rated_party,
        "role": role,
        "distribution": distribution,
        "total": len(rows),
        "first_rated_at": min(timestamps),
        "last_rated_at": max(timestamps),
        "transaction_count": len(exchange_ids),
    }
