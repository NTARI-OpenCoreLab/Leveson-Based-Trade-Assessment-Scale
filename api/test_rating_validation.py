#!/usr/bin/env python3
"""
Plain-assert tests for rating_validation.py — no pytest dependency, run
directly with `python3 api/test_rating_validation.py`, matching the "no
external dependencies required" posture of this project.

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0
"""

import sys

from rating_validation import (
    MAX_COMMENT_WORDS,
    RatingValidationError,
    validate_rating_submission,
)


def expect_ok(value, comment=None, label=""):
    try:
        validate_rating_submission(value, comment)
    except RatingValidationError as e:
        raise AssertionError(f"[{label}] expected OK but got error: {e}")


def expect_error(value, comment=None, label="", must_contain=None):
    try:
        validate_rating_submission(value, comment)
    except RatingValidationError as e:
        if must_contain and must_contain not in str(e):
            raise AssertionError(
                f"[{label}] error message missing expected text {must_contain!r}: {e}"
            )
        return
    raise AssertionError(f"[{label}] expected RatingValidationError but got none")


def run():
    # -1 with a valid short comment passes.
    expect_ok(-1, "The seller sent a counterfeit item and refused a refund.", "minus_one_valid_comment")

    # -1 with no comment at all is rejected.
    expect_error(-1, None, "minus_one_missing_comment", must_contain="requires a justifying comment")

    # -1 with an empty string is rejected.
    expect_error(-1, "", "minus_one_empty_comment", must_contain="requires a justifying comment")

    # -1 with a whitespace-only comment is rejected.
    expect_error(-1, "   \n\t  ", "minus_one_whitespace_comment", must_contain="requires a justifying comment")

    # -1 with exactly 500 words passes.
    exactly_500 = " ".join(["word"] * MAX_COMMENT_WORDS)
    expect_ok(-1, exactly_500, "minus_one_exactly_500_words")

    # -1 with 501 words is rejected, and NOT silently truncated (we only
    # check that it raises with the right message; truncation would show up
    # as no exception at all, which the expect_error helper would catch).
    over_limit = " ".join(["word"] * (MAX_COMMENT_WORDS + 1))
    expect_error(-1, over_limit, "minus_one_over_limit", must_contain="500 words or fewer")

    # Ratings 0..+4: comment is optional.
    for level in (0, 1, 2, 3, 4):
        expect_ok(level, None, f"level_{level}_no_comment")

    # Ratings 0..+4: a comment, even a very long one, is fine (no cap imposed
    # by CLAUDE.md at these levels).
    long_comment = " ".join(["great"] * 600)
    expect_ok(2, long_comment, "level_2_long_comment_allowed")

    # Out-of-range values are rejected regardless of comment.
    expect_error(-2, "some comment", "below_range")
    expect_error(5, "some comment", "above_range")

    # Non-integer values are rejected.
    expect_error(1.5, "some comment", "float_rating")
    expect_error("3", "some comment", "string_rating")
    expect_error(True, "some comment", "bool_rating")  # bool is technically an int subclass in Python

    print("ALL TESTS PASSED")


if __name__ == "__main__":
    try:
        run()
    except AssertionError as e:
        print(f"TEST FAILURE: {e}")
        sys.exit(1)
