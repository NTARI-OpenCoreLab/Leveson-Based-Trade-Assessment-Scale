#!/usr/bin/env python3
"""
LBTAS API — entry point
========================

Minimal FastAPI app. This is the starting scaffold for the networked API
described in CLAUDE.md ("What the API does"); it currently exposes only a
health check so the service can be stood up and verified end to end before
the rating-submission, storage, and authorization pieces are wired in.

Copyright (C) 2024 Network Theory Applied Research Institute
Licensed under GNU Affero General Public License v3.0

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

from fastapi import FastAPI

app = FastAPI(title="LBTAS API", version="2.0.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
