#!/usr/bin/env python3
"""
Plain-assert tests for event_store.py — no pytest dependency, run directly
with `python3 api/test_event_store.py`.

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0
"""

import sqlite3
import sys

from event_store import DuplicateRatingError, get_connection, get_events_for_party_role, insert_event


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

    conn.close()
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    try:
        run()
    except AssertionError as e:
        print(f"TEST FAILURE: {e}")
        sys.exit(1)
