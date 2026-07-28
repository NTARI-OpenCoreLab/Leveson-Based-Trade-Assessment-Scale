#!/usr/bin/env python3
"""
LBTAS API — rating submission validation
=========================================

Enforces the -1 comment rule described in CLAUDE.md ("The -1 comment
requirement"):

  - A rating of -1 ("No Trust") MUST carry a justifying comment of 500
    words or less.
  - The comment is mandatory for -1. Submitting -1 with no comment (or a
    blank/whitespace-only one) is rejected.
  - The 500-word maximum is enforced by rejecting the submission outright,
    never by silently truncating it.
  - For ratings 0 through +4, a comment is optional and unbounded here
    (product requirements may add limits later, but CLAUDE.md does not
    impose one on those levels).

This module has no external dependencies, matching the "no external
dependencies required for basic functionality" posture of the reference
CLIs (see requirements.txt). It is intended to sit at the API boundary,
in front of whatever framework/route handles rating submission (FastAPI,
per requirements.txt's commented-out dependency).

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from typing import Optional

MIN_RATING = -1
MAX_RATING = 4
HARM_RATING = -1
MAX_COMMENT_WORDS = 500


class RatingValidationError(ValueError):
    """Raised when a rating submission fails validation at the API boundary."""


def _word_count(comment: str) -> int:
    """Count words by whitespace splitting (leading/trailing whitespace ignored)."""
    return len(comment.split())


def validate_rating_submission(value: int, comment: Optional[str] = None) -> None:
    """
    Validate a single rating submission before it is accepted into the event
    store. Raises RatingValidationError on any violation; callers should
    reject the request (e.g. HTTP 400) rather than coerce or truncate it.

    Args:
        value: The rating value; must be an integer in [-1, 4].
        comment: The justifying comment, if any. Mandatory and capped at
            500 words when value == -1 (HARM_RATING). Optional and
            unbounded for all other levels.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise RatingValidationError(
            f"Rating must be an integer between {MIN_RATING} and {MAX_RATING}, got {value!r}"
        )

    if value < MIN_RATING or value > MAX_RATING:
        raise RatingValidationError(
            f"Rating must be between {MIN_RATING} and {MAX_RATING}, got {value}"
        )

    if value == HARM_RATING:
        if comment is None or not comment.strip():
            raise RatingValidationError(
                "A rating of -1 (No Trust) requires a justifying comment; none was provided."
            )

        word_count = _word_count(comment)
        if word_count > MAX_COMMENT_WORDS:
            raise RatingValidationError(
                f"Comment for a -1 (No Trust) rating must be {MAX_COMMENT_WORDS} words or "
                f"fewer; got {word_count}. Submission rejected, not truncated."
            )

    # Ratings 0..+4: comment is optional and unbounded here; nothing to enforce.
