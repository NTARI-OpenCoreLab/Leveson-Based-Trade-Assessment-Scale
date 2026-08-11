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

CLAUDE.md's authorization section treats submission and review as separate
capabilities that "must be authorized separately." Two keys, two gates:
LBTAS_API_KEY (require_api_key) covers the review/adjudication side — reads,
dismiss, uphold, apply-timeouts. LBTAS_SUBMIT_KEY (require_submit_key) covers
the submission side — POST /ratings, /contest, /exchanges. Both fail closed
(503) with no key configured, never falling open. This is still coarse
compared to CLAUDE.md's fuller model — one shared secret per capability, not
a credential scoped to a specific party or tied to a specific served prompt —
but it does now encode "these are different capabilities" as two actually
different secrets, not just a comment saying so.

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
no privileged side); it's gated behind LBTAS_SUBMIT_KEY like POST /ratings,
since it's the rated party exercising their own right, not a privileged
review. POST /ratings/{event_id}/uphold is the adjudicator's other
resolution besides dismissal: the rating stands, but GET marks it
"contested" and "upheld" (with who and why) rather than silently leaving it
looking unquestioned.

POST /exchanges registers an exchange's two rating directions and starts its
rating window (SPEC.md §7); gated behind LBTAS_SUBMIT_KEY, same posture as
POST /ratings. POST /exchanges/{exchange_id}/apply-timeouts backfills a
system-attributed +2 for any direction still unrated once the window has
elapsed — there's no background worker here, so a real deployment calls this
from an external scheduler. It's gated behind LBTAS_API_KEY, same as
dismiss/uphold. GET marks a timeout default as "defaulted" so it's never
mistaken for an affirmed rating, and surfaces a party/role's defaulted_count.

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
SUBMIT_KEY_ENV_VAR = "LBTAS_SUBMIT_KEY"
DEFAULT_RATING_WINDOW_SECONDS = 7 * 24 * 60 * 60  # 7 days


def _require_key(env_var: str, x_api_key: Optional[str], unavailable_detail: str) -> None:
    """Shared fail-closed check: with no key configured, deny everything —
    never fall open. secrets.compare_digest avoids a timing side-channel."""
    configured_key = os.environ.get(env_var)
    if not configured_key:
        raise HTTPException(status_code=503, detail=unavailable_detail)
    if not x_api_key or not secrets.compare_digest(x_api_key, configured_key):
        raise HTTPException(status_code=401, detail="Missing or invalid API key.")


def require_api_key(x_api_key: Optional[str] = Header(None)) -> None:
    """Review/adjudication gate: reads, dismiss, uphold, apply-timeouts."""
    _require_key(
        API_KEY_ENV_VAR,
        x_api_key,
        f"Reads are not available: {API_KEY_ENV_VAR} is not configured on this deployment.",
    )


def require_submit_key(x_api_key: Optional[str] = Header(None)) -> None:
    """Submission gate: POST /ratings, /contest, /exchanges. Deliberately a
    separate secret from require_api_key — CLAUDE.md: submitting a rating and
    reviewing accumulated records "are distinct capabilities and must be
    authorized separately." """
    _require_key(
        SUBMIT_KEY_ENV_VAR,
        x_api_key,
        f"Submissions are not available: {SUBMIT_KEY_ENV_VAR} is not configured on this deployment.",
    )


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


class ExchangeRegistration(BaseModel):
    exchange_id: str = Field(..., description="Unique id for this exchange")
    party_a: str = Field(..., description="One party to the exchange")
    role_a: str = Field(..., min_length=1, description="Capacity party_a acted in; party_b rates party_a on this")
    party_b: str = Field(..., description="The other party to the exchange")
    role_b: str = Field(..., min_length=1, description="Capacity party_b acted in; party_a rates party_b on this")
    completed_at: Optional[str] = Field(
        None, description="ISO-8601 completion time; defaults to now if omitted"
    )
    rating_window_seconds: Optional[int] = Field(
        None,
        gt=0,
        description=f"Rating window before a timeout default applies; defaults to {DEFAULT_RATING_WINDOW_SECONDS}s (7 days). Must be positive.",
    )


def _new_distribution() -> dict:
    return {str(level): 0 for level in (-1, 0, 1, 2, 3, 4)}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ratings", status_code=201, dependencies=[Depends(require_submit_key)])
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
    except (event_store.DuplicateRatingError, event_store.TimeoutAlreadyAppliedError) as e:
        raise HTTPException(status_code=409, detail=str(e))
    except event_store.InvalidExchangePartyError as e:
        raise HTTPException(status_code=400, detail=str(e))
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


@app.post("/ratings/{event_id}/contest", dependencies=[Depends(require_submit_key)])
def contest_rating(event_id: int, contest: ContestRequest) -> dict:
    """The rated party disputes a rating made against them (SPEC.md §5).
    Gated behind LBTAS_SUBMIT_KEY like POST /ratings, not LBTAS_API_KEY:
    this is the rated party's own right, not an adjudicator action."""
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
    except event_store.NotRatedPartyError as e:
        raise HTTPException(status_code=403, detail=str(e))
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


@app.post("/exchanges", status_code=201, dependencies=[Depends(require_submit_key)])
def register_exchange(exchange: ExchangeRegistration) -> dict:
    """Register an exchange's two rating directions and start its rating
    window (SPEC.md §7). Gated behind LBTAS_SUBMIT_KEY, same posture as
    POST /ratings.

    completed_at is parsed and required to be timezone-aware here: stored
    unparsed, a malformed or naive value would surface later as a 500 inside
    apply_timeout_defaults's datetime arithmetic instead of a clean 400 now.
    """
    if exchange.completed_at is not None:
        try:
            parsed_completed_at = datetime.fromisoformat(exchange.completed_at)
        except ValueError:
            raise HTTPException(
                status_code=400, detail="completed_at must be a valid ISO-8601 datetime"
            )
        if parsed_completed_at.tzinfo is None:
            raise HTTPException(
                status_code=400,
                detail="completed_at must be timezone-aware (include a UTC offset, e.g. '+00:00' or 'Z')",
            )
        completed_at = exchange.completed_at
    else:
        completed_at = datetime.now(timezone.utc).isoformat()

    # gt=0 on the model already rejects 0/negative; None means "use the default".
    rating_window_seconds = (
        exchange.rating_window_seconds
        if exchange.rating_window_seconds is not None
        else DEFAULT_RATING_WINDOW_SECONDS
    )

    conn = event_store.get_connection()
    try:
        event_store.register_exchange(
            conn,
            exchange_id=exchange.exchange_id,
            completed_at=completed_at,
            rating_window_seconds=rating_window_seconds,
            party_a=exchange.party_a,
            role_a=exchange.role_a,
            party_b=exchange.party_b,
            role_b=exchange.role_b,
        )
    except event_store.ExchangeAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    finally:
        conn.close()

    return {
        "status": "registered",
        "exchange_id": exchange.exchange_id,
        "completed_at": completed_at,
        "rating_window_seconds": rating_window_seconds,
        "party_a": exchange.party_a,
        "role_a": exchange.role_a,
        "party_b": exchange.party_b,
        "role_b": exchange.role_b,
    }


@app.post("/exchanges/{exchange_id}/apply-timeouts", dependencies=[Depends(require_api_key)])
def apply_timeouts(exchange_id: str) -> dict:
    """Backfill a system-attributed +2 (SPEC.md §7) for any direction of
    this exchange still unrated once its rating window has elapsed.
    Idempotent — safe to call repeatedly, e.g. from an external scheduler,
    since this API has no background worker of its own."""
    conn = event_store.get_connection()
    try:
        result = event_store.apply_timeout_defaults(conn, exchange_id, datetime.now(timezone.utc))
    except event_store.ExchangeNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    finally:
        conn.close()

    return result


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
            # SPEC.md §7: a timeout default MUST be distribution-distinguishable
            # from an affirmed rating — never look like praise or like silence.
            "defaulted": row["rater_role"] == "system",
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

    defaulted_count = sum(1 for row in active_rows if row["rater_role"] == "system")

    result = {
        "rated_party": rated_party,
        "role": role,
        "distribution": distribution,
        "total": len(active_rows),
        "events": events,
        "defaulted_count": defaulted_count,
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
