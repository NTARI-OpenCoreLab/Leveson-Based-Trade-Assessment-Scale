#!/usr/bin/env python3
"""
HTTP-layer tests for main.py.

Spins up a real uvicorn subprocess against a temp SQLite file and drives it
with stdlib urllib — no TestClient/httpx, matching the "no external
dependencies" posture the other test files establish (fastapi.testclient
needs httpx, an extra dependency not otherwise needed anywhere in this repo).

This complements test_event_store.py rather than duplicating it: the store
tests already exhaustively cover business-logic edge cases (role isolation,
exchange-tie, timeout math, ...) at the function level. This file's job is
the HTTP wiring on top of that — status codes, the two-key auth gating, and
response shapes — which had previously only ever been checked by hand with
curl.

Run from the REPO ROOT: `python3 api/test_main.py` (matches requirements.txt;
unlike the other two test files, this one doesn't need to run from inside
api/ — it has no sibling-module imports, and the uvicorn subprocess's cwd is
pinned to the repo root explicitly regardless of where this script is invoked
from).

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

HOST = "127.0.0.1"
# Overridable in case 8934 is ever busy on the machine running this.
PORT = int(os.environ.get("LBTAS_TEST_PORT", "8934"))
BASE_URL = f"http://{HOST}:{PORT}"
READ_KEY = "test-read-key"
SUBMIT_KEY = "test-submit-key"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def request(method, path, body=None, api_key=None):
    """Minimal JSON HTTP client. Returns (status_code, parsed_body_or_None)."""
    url = BASE_URL + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"}
    if api_key is not None:
        headers["X-API-Key"] = api_key
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        return e.code, (json.loads(raw) if raw else None)


def expect(method, path, expect_status, body=None, api_key=None, label=""):
    status, payload = request(method, path, body=body, api_key=api_key)
    if status != expect_status:
        raise AssertionError(
            f"[{label}] {method} {path}: expected HTTP {expect_status}, got {status}: {payload}"
        )
    return payload


def start_server(env_overrides):
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    os.remove(db_path)  # let the app create it fresh on first connection

    env = os.environ.copy()
    env["LBTAS_DB_PATH"] = db_path
    env.update(env_overrides)

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", HOST, "--port", str(PORT)],
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            status, _ = request("GET", "/health")
            if status == 200:
                return proc, db_path
        except (urllib.error.URLError, ConnectionRefusedError, ConnectionResetError):
            pass
        if proc.poll() is not None:
            output = proc.stdout.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Server process exited early:\n{output}")
        time.sleep(0.2)
    raise RuntimeError("Server did not become healthy in time")


def stop_server(proc, db_path):
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
    if os.path.exists(db_path):
        os.remove(db_path)


def run_no_keys_configured():
    """Every submission and read must fail closed (503) with nothing set —
    never fall open just because a key happens to be unconfigured."""
    proc, db_path = start_server({"LBTAS_API_KEY": "", "LBTAS_SUBMIT_KEY": ""})
    try:
        expect(
            "POST", "/ratings", 503, label="no_keys_submit",
            body={"exchange_id": "tx", "rater": "a", "rated_party": "b", "role": "market_buyer", "value": 2},
        )
        expect(
            "POST", "/exchanges", 503, label="no_keys_register_exchange",
            body={"exchange_id": "tx", "party_a": "a", "role_a": "market_seller", "party_b": "b", "role_b": "market_buyer"},
        )
        expect("GET", "/ratings/anyone/anyrole", 503, label="no_keys_read")
    finally:
        stop_server(proc, db_path)


def run_with_keys_configured():
    proc, db_path = start_server({"LBTAS_API_KEY": READ_KEY, "LBTAS_SUBMIT_KEY": SUBMIT_KEY})
    try:
        expect("GET", "/health", 200, label="health")

        # --- Two-key auth separation ---
        expect(
            "POST", "/ratings", 401, api_key=READ_KEY, label="read_key_cannot_submit",
            body={"exchange_id": "tx-1", "rater": "alice", "rated_party": "Bob", "role": "market_buyer", "value": 2},
        )
        submitted = expect(
            "POST", "/ratings", 201, api_key=SUBMIT_KEY, label="submit_key_can_submit",
            body={"exchange_id": "tx-1", "rater": "alice", "rated_party": "Bob", "role": "market_buyer", "value": 2},
        )
        assert submitted["status"] == "accepted"
        event_id = submitted["event_id"]
        assert isinstance(event_id, int), f"expected an integer event_id, got {submitted!r}"

        expect("GET", "/ratings/Bob/market_buyer", 401, api_key=SUBMIT_KEY, label="submit_key_cannot_read")
        read_back = expect("GET", "/ratings/Bob/market_buyer", 200, api_key=READ_KEY, label="read_key_can_read")
        assert read_back["distribution"]["2"] == 1
        assert read_back["total"] == 1
        assert read_back["events"][0]["event_id"] == event_id

        # --- -1 comment rule enforced at the boundary ---
        expect(
            "POST", "/ratings", 400, api_key=SUBMIT_KEY, label="minus_one_no_comment",
            body={"exchange_id": "tx-2", "rater": "carol", "rated_party": "Bob", "role": "market_buyer", "value": -1},
        )

        # --- Duplicate submission rejected ---
        expect(
            "POST", "/ratings", 409, api_key=SUBMIT_KEY, label="duplicate_submission",
            body={"exchange_id": "tx-1", "rater": "alice", "rated_party": "Bob", "role": "market_buyer", "value": 3},
        )

        # --- Contest: gated behind SUBMIT_KEY, only the rated party may contest ---
        expect(
            "POST", f"/ratings/{event_id}/contest", 401, label="contest_needs_a_key",
            body={"contested_by": "Bob", "reason": "testing"},
        )
        expect(
            "POST", f"/ratings/{event_id}/contest", 403, api_key=SUBMIT_KEY, label="contest_wrong_party",
            body={"contested_by": "SomeoneElse", "reason": "not the rated party"},
        )
        contested = expect(
            "POST", f"/ratings/{event_id}/contest", 200, api_key=SUBMIT_KEY, label="contest_right_party",
            body={"contested_by": "Bob", "reason": "Delay was outside my control."},
        )
        assert contested["status"] == "contested"

        # --- Uphold: gated behind API_KEY (adjudicator side), not SUBMIT_KEY ---
        expect(
            "POST", f"/ratings/{event_id}/uphold", 401, api_key=SUBMIT_KEY, label="uphold_wrong_key",
            body={"upheld_by": "adjudicator-1", "reason": "Rating stands."},
        )
        upheld = expect(
            "POST", f"/ratings/{event_id}/uphold", 200, api_key=READ_KEY, label="uphold_right_key",
            body={"upheld_by": "adjudicator-1", "reason": "Rating stands."},
        )
        assert upheld["status"] == "upheld"

        after_uphold = expect("GET", "/ratings/Bob/market_buyer", 200, api_key=READ_KEY, label="read_after_uphold")
        event_after = after_uphold["events"][0]
        assert event_after["contested"] is True and event_after["upheld"] is True

        # --- Exchange registration: time/window validation at the boundary ---
        expect(
            "POST", "/exchanges", 400, api_key=SUBMIT_KEY, label="malformed_completed_at",
            body={
                "exchange_id": "tx-bad-time", "party_a": "A", "role_a": "market_seller",
                "party_b": "B", "role_b": "market_buyer", "completed_at": "not-a-date",
            },
        )
        expect(
            "POST", "/exchanges", 400, api_key=SUBMIT_KEY, label="naive_completed_at",
            body={
                "exchange_id": "tx-naive-time", "party_a": "A", "role_a": "market_seller",
                "party_b": "B", "role_b": "market_buyer", "completed_at": "2026-01-01T00:00:00",
            },
        )
        expect(
            "POST", "/exchanges", 422, api_key=SUBMIT_KEY, label="zero_window_rejected",
            body={
                "exchange_id": "tx-zero-window", "party_a": "A", "role_a": "market_seller",
                "party_b": "B", "role_b": "market_buyer", "rating_window_seconds": 0,
            },
        )

        # --- Exchange-tied + role-pinned rating rejection ---
        expect(
            "POST", "/exchanges", 201, api_key=SUBMIT_KEY, label="register_tied_exchange",
            body={
                "exchange_id": "tx-tied", "party_a": "TiedSeller", "role_a": "market_seller",
                "party_b": "TiedBuyer", "role_b": "market_buyer",
                "completed_at": "2026-01-01T00:00:00+00:00", "rating_window_seconds": 3600,
            },
        )
        expect(
            "POST", "/ratings", 400, api_key=SUBMIT_KEY, label="outsider_rejected",
            body={"exchange_id": "tx-tied", "rater": "RandomOutsider", "rated_party": "TiedSeller", "role": "market_seller", "value": 2},
        )
        expect(
            "POST", "/ratings", 400, api_key=SUBMIT_KEY, label="wrong_role_rejected",
            body={"exchange_id": "tx-tied", "rater": "TiedBuyer", "rated_party": "TiedSeller", "role": "market_buyer", "value": 2},
        )
        expect(
            "POST", "/ratings", 201, api_key=SUBMIT_KEY, label="correct_direction_accepted",
            body={"exchange_id": "tx-tied", "rater": "TiedBuyer", "rated_party": "TiedSeller", "role": "market_seller", "value": 4},
        )

        # --- Timeout defaults: register an already-overdue exchange, apply, verify ---
        expect(
            "POST", "/exchanges", 201, api_key=SUBMIT_KEY, label="register_overdue_exchange",
            body={
                "exchange_id": "tx-overdue", "party_a": "OverdueSeller", "role_a": "market_seller",
                "party_b": "OverdueBuyer", "role_b": "market_buyer",
                "completed_at": "2020-01-01T00:00:00+00:00", "rating_window_seconds": 1,
            },
        )
        expect(
            "POST", "/exchanges/tx-overdue/apply-timeouts", 401, api_key=SUBMIT_KEY,
            label="apply_timeouts_wrong_key",
        )
        applied = expect(
            "POST", "/exchanges/tx-overdue/apply-timeouts", 200, api_key=READ_KEY,
            label="apply_timeouts_right_key",
        )
        assert applied["status"] == "processed"
        assert set(applied["defaulted"]) == {"OverdueSeller", "OverdueBuyer"}

        defaulted_read = expect(
            "GET", "/ratings/OverdueSeller/market_seller", 200, api_key=READ_KEY, label="read_defaulted"
        )
        assert defaulted_read["defaulted_count"] == 1
        assert defaulted_read["events"][0]["defaulted"] is True
        assert defaulted_read["events"][0]["value"] == 2

        # --- A late real rating on an already-defaulted direction is rejected ---
        expect(
            "POST", "/ratings", 409, api_key=SUBMIT_KEY, label="late_rating_after_default",
            body={"exchange_id": "tx-overdue", "rater": "OverdueBuyer", "rated_party": "OverdueSeller", "role": "market_seller", "value": 4},
        )

        print("ALL TESTS PASSED")
    finally:
        stop_server(proc, db_path)


def run():
    run_no_keys_configured()
    run_with_keys_configured()


if __name__ == "__main__":
    try:
        run()
    except AssertionError as e:
        print(f"TEST FAILURE: {e}")
        sys.exit(1)
