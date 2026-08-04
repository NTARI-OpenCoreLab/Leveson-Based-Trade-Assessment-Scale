#!/usr/bin/env python3
"""
Plain-assert tests for event_store.py — no pytest dependency, run directly
with `python3 api/test_event_store.py`.

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0
"""

import sqlite3
import sys

from event_store import (
    AlreadyContestedError,
    AlreadyDismissedError,
    AlreadyUpheldError,
    ContestNotFoundError,
    DuplicateRatingError,
    EventNotFoundError,
    contest_event,
    dismiss_event,
    get_connection,
    get_dismissed_events_for_party_role,
    get_events_for_party_role,
    insert_event,
    uphold_contest,
)


def expect_error(fn, exc_type, label=""):
    try:
        fn()
    except exc_type:
        return
    raise AssertionError(f"[{label}] expected {exc_type.__name__} but got none")


def run():
    # Role isolation (SPEC.md §3): a -1 earned as market_buyer must never show
    # up in, or affect, the same party's market_seller distribution.
    conn = get_connection(":memory:")

    insert_event(
        conn,
        exchange_id="ex-1",
        rater="alice",
        rated_party="Bob",
        role="market_buyer",
        category=None,
        value=-1,
        comment="Never paid after receiving the goods.",
        timestamp="2026-01-01T00:00:00+00:00",
    )
    insert_event(
        conn,
        exchange_id="ex-2",
        rater="carol",
        rated_party="Bob",
        role="market_seller",
        category=None,
        value=2,
        comment=None,
        timestamp="2026-01-02T00:00:00+00:00",
    )
    insert_event(
        conn,
        exchange_id="ex-3",
        rater="dave",
        rated_party="Bob",
        role="market_seller",
        category=None,
        value=4,
        comment=None,
        timestamp="2026-01-03T00:00:00+00:00",
    )

    buyer_rows = get_events_for_party_role(conn, "Bob", "market_buyer")
    seller_rows = get_events_for_party_role(conn, "Bob", "market_seller")

    assert len(buyer_rows) == 1, f"expected 1 market_buyer event, got {len(buyer_rows)}"
    assert buyer_rows[0]["value"] == -1, "market_buyer event should be the -1"

    assert len(seller_rows) == 2, f"expected 2 market_seller events, got {len(seller_rows)}"
    seller_values = sorted(row["value"] for row in seller_rows)
    assert seller_values == [2, 4], f"market_seller values should be [2, 4], got {seller_values}"

    # The -1 must not appear anywhere in the market_seller rows: isolation, not
    # just non-overlap by count.
    assert all(row["value"] != -1 for row in seller_rows), "the -1 leaked into market_seller"

    # A role with no events for this party returns empty, not the other role's data.
    empty_rows = get_events_for_party_role(conn, "Bob", "service_provider")
    assert empty_rows == [], "an unrelated role should see no events for this party"

    # Uniqueness constraint (CLAUDE.md: the count itself is a trust signal —
    # a repeat submission for the same exchange/rater/rated_party must not
    # inflate it).
    expect_error(
        lambda: insert_event(
            conn,
            exchange_id="ex-1",
            rater="alice",
            rated_party="Bob",
            role="market_buyer",
            category=None,
            value=-1,
            comment="Trying to submit the same exchange again.",
            timestamp="2026-01-04T00:00:00+00:00",
        ),
        DuplicateRatingError,
        "duplicate_exchange_rater_party",
    )

    # Same exchange/rated_party but a *different* rater is not a duplicate
    # (bidirectional: both parties may rate the same exchange).
    insert_event(
        conn,
        exchange_id="ex-1",
        rater="bob_the_seller",
        rated_party="Bob",
        role="market_seller",
        category=None,
        value=1,
        comment=None,
        timestamp="2026-01-05T00:00:00+00:00",
    )

    # CHECK constraint on value range: an out-of-range value must not persist.
    expect_error(
        lambda: insert_event(
            conn,
            exchange_id="ex-4",
            rater="eve",
            rated_party="Bob",
            role="market_buyer",
            category=None,
            value=7,
            comment=None,
            timestamp="2026-01-06T00:00:00+00:00",
        ),
        sqlite3.IntegrityError,
        "out_of_range_value_rejected",
    )

    # --- Dismiss-as-annotate (SPEC.md §4, §6) ---

    # Grab the id of the bad-faith market_buyer -1 to dismiss it.
    dismissed_event_id = buyer_rows[0]["id"]

    dismiss_event(
        conn,
        event_id=dismissed_event_id,
        dismissed_by="adjudicator-1",
        reason="Rater retaliated after a price dispute; contested and found bad-faith.",
        timestamp="2026-01-07T00:00:00+00:00",
    )

    # The dismissed -1 must disappear from the ACTIVE market_buyer read...
    active_buyer_rows = get_events_for_party_role(conn, "Bob", "market_buyer")
    assert active_buyer_rows == [], (
        f"dismissed event should be excluded from the active read, got {active_buyer_rows}"
    )

    # ...but it MUST NOT be hidden: it stays visible via the dismissed list,
    # annotated with who dismissed it and why.
    dismissed_buyer_rows = get_dismissed_events_for_party_role(conn, "Bob", "market_buyer")
    assert len(dismissed_buyer_rows) == 1, f"expected 1 dismissed event, got {len(dismissed_buyer_rows)}"
    dismissed_row = dismissed_buyer_rows[0]
    assert dismissed_row["id"] == dismissed_event_id
    assert dismissed_row["value"] == -1, "the dismissed event's original value must be preserved, not erased"
    assert dismissed_row["dismissed_by"] == "adjudicator-1"
    assert "bad-faith" in dismissed_row["dismissal_reason"]
    assert dismissed_row["dismissed_at"] == "2026-01-07T00:00:00+00:00"

    # Dismissal must not touch other roles/parties. market_seller has 3 active
    # events by this point (the original 2 plus bob_the_seller's, inserted above).
    seller_rows_after_dismissal = get_events_for_party_role(conn, "Bob", "market_seller")
    assert len(seller_rows_after_dismissal) == 3, "dismissing a market_buyer event must not affect market_seller"

    # Dismissing a nonexistent event id is rejected, not silently accepted.
    expect_error(
        lambda: dismiss_event(
            conn,
            event_id=999_999,
            dismissed_by="adjudicator-1",
            reason="does not exist",
            timestamp="2026-01-08T00:00:00+00:00",
        ),
        EventNotFoundError,
        "dismiss_nonexistent_event",
    )

    # Dismissing the same event twice is rejected — one dismissal per event,
    # never a second edit (SPEC.md §6).
    expect_error(
        lambda: dismiss_event(
            conn,
            event_id=dismissed_event_id,
            dismissed_by="adjudicator-2",
            reason="trying to dismiss again",
            timestamp="2026-01-09T00:00:00+00:00",
        ),
        AlreadyDismissedError,
        "double_dismissal_rejected",
    )

    # --- Symmetric contest (SPEC.md §5) + uphold (SPEC.md §6) ---

    # seller_rows_after_dismissal is ordered by timestamp: [+2 (carol/ex-2),
    # +4 (dave/ex-3), +1 (bob_the_seller/ex-1)].
    contested_event_id = seller_rows_after_dismissal[0]["id"]
    assert seller_rows_after_dismissal[0]["value"] == 2

    # Before any contest, the row's contest columns are all NULL.
    pre_contest = get_events_for_party_role(conn, "Bob", "market_seller")
    pre_row = next(r for r in pre_contest if r["id"] == contested_event_id)
    assert pre_row["contested_by"] is None, "an uncontested event must show no contest annotation"

    # The rated party (Bob) contests the +2 made against him.
    contest_event(
        conn,
        event_id=contested_event_id,
        contested_by="Bob",
        reason="Rating was based on a shipping delay outside my control.",
        timestamp="2026-01-10T00:00:00+00:00",
    )

    contested_rows = get_events_for_party_role(conn, "Bob", "market_seller")
    contested_row = next(r for r in contested_rows if r["id"] == contested_event_id)
    assert contested_row["contested_by"] == "Bob"
    assert "shipping delay" in contested_row["contest_reason"]
    assert contested_row["upheld_by"] is None, "contested but not yet resolved must not show an uphold"

    # An adjudicator reviews and upholds it: the rating stands, but it must be
    # distinguishable from an unquestioned rating.
    uphold_contest(
        conn,
        event_id=contested_event_id,
        upheld_by="adjudicator-1",
        reason="Delay was within seller's control; rating stands.",
        timestamp="2026-01-11T00:00:00+00:00",
    )

    upheld_rows = get_events_for_party_role(conn, "Bob", "market_seller")
    upheld_row = next(r for r in upheld_rows if r["id"] == contested_event_id)
    assert upheld_row["value"] == 2, "upholding must not change the original rating value"
    assert upheld_row["upheld_by"] == "adjudicator-1"
    assert "stands" in upheld_row["uphold_reason"]

    # Symmetric: the same mechanism works for a rating in the OTHER direction
    # too — no privileged side. bob_the_seller's own +1 (as market_seller) can
    # equally be contested by its rated party.
    other_event_id = seller_rows_after_dismissal[2]["id"]
    assert seller_rows_after_dismissal[2]["value"] == 1
    contest_event(
        conn,
        event_id=other_event_id,
        contested_by="Bob",
        reason="Testing symmetric contest in the other direction.",
        timestamp="2026-01-12T00:00:00+00:00",
    )
    other_contested = next(
        r for r in get_events_for_party_role(conn, "Bob", "market_seller") if r["id"] == other_event_id
    )
    assert other_contested["contested_by"] == "Bob"

    # Upholding a contest that doesn't exist is rejected.
    expect_error(
        lambda: uphold_contest(
            conn,
            event_id=999_999,
            upheld_by="adjudicator-1",
            reason="no such contest",
            timestamp="2026-01-13T00:00:00+00:00",
        ),
        ContestNotFoundError,
        "uphold_without_contest",
    )

    # Contesting the same event twice is rejected — one open contest per event.
    expect_error(
        lambda: contest_event(
            conn,
            event_id=contested_event_id,
            contested_by="Bob",
            reason="trying to contest again",
            timestamp="2026-01-14T00:00:00+00:00",
        ),
        AlreadyContestedError,
        "double_contest_rejected",
    )

    # Upholding the same contest twice is rejected.
    expect_error(
        lambda: uphold_contest(
            conn,
            event_id=contested_event_id,
            upheld_by="adjudicator-2",
            reason="trying to uphold again",
            timestamp="2026-01-15T00:00:00+00:00",
        ),
        AlreadyUpheldError,
        "double_uphold_rejected",
    )

    # Contesting an already-dismissed event is rejected — nothing left to
    # contest once an adjudicator already ruled it out entirely.
    expect_error(
        lambda: contest_event(
            conn,
            event_id=dismissed_event_id,
            contested_by="alice",
            reason="trying to contest a dismissed event",
            timestamp="2026-01-16T00:00:00+00:00",
        ),
        AlreadyDismissedError,
        "contest_dismissed_event_rejected",
    )

    # A contested-then-dismissed event: dismiss remains independent of
    # contest/uphold state by design, so this must succeed...
    contest_then_dismiss_id = seller_rows_after_dismissal[1]["id"]
    contest_event(
        conn,
        event_id=contest_then_dismiss_id,
        contested_by="Bob",
        reason="Contesting before a separate dismissal happens.",
        timestamp="2026-01-17T00:00:00+00:00",
    )
    dismiss_event(
        conn,
        event_id=contest_then_dismiss_id,
        dismissed_by="adjudicator-1",
        reason="Found bad-faith on independent review.",
        timestamp="2026-01-18T00:00:00+00:00",
    )
    # ...but upholding it afterward must now be rejected: an adjudicator
    # already ruled the event out entirely.
    expect_error(
        lambda: uphold_contest(
            conn,
            event_id=contest_then_dismiss_id,
            upheld_by="adjudicator-2",
            reason="trying to uphold a dismissed event",
            timestamp="2026-01-19T00:00:00+00:00",
        ),
        AlreadyDismissedError,
        "uphold_dismissed_event_rejected",
    )

    conn.close()
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    try:
        run()
    except AssertionError as e:
        print(f"TEST FAILURE: {e}")
        sys.exit(1)
