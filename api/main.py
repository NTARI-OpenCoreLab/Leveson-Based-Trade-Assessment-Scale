#!/usr/bin/env python3
"""
LBTAS API — entry point
========================

Minimal FastAPI app. This is the starting scaffold for the networked API
described in CLAUDE.md ("What the API does"). POST /ratings runs a submission
through the -1 comment validation rule; it does not yet persist anything —
the event store lands separately.

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from api.rating_validation import RatingValidationError, validate_rating_submission

app = FastAPI(title="LBTAS API", version="2.0.0")


class RatingSubmission(BaseModel):
    exchange_id: str = Field(..., description="Triggering exchange/transaction id")
    rater: str = Field(..., description="Party submitting the rating")
    rated_party: str = Field(..., description="Party being rated")
    category: Optional[str] = None
    value: int = Field(..., description="Rating value, -1 to +4")
    comment: Optional[str] = Field(
        None, description="Justifying comment; mandatory and <=500 words when value is -1"
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ratings", status_code=201)
def submit_rating(submission: RatingSubmission) -> dict:
    try:
        validate_rating_submission(submission.value, submission.comment)
    except RatingValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "accepted", "submission": submission.model_dump()}
