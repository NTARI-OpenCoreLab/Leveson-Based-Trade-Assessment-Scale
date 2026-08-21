# Changelog

All notable changes to LBTAS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

A working networked API implementation now exists under `api/` (FastAPI +
SQLite, no other external dependencies) — the production surface `CLAUDE.md`
describes, previously undocumented anywhere but the spec. Not yet deployed to
NTARIHQ. See `api/requirements.txt` for run/test instructions and
`api/main.py`'s module docstring for exactly what's implemented versus still
coarse.

### Added

- **Rating submission and role-scoped reads** (`POST /ratings`,
  `GET /ratings/{party}/{role}`), backed by an individual-event SQLite store
  (not the CLI's JSON file) per `CLAUDE.md`'s data model.
- **The `-1` comment rule** enforced at the API boundary: mandatory,
  ≤500 words and a byte ceiling, rejected rather than truncated.
- **Dismiss-as-annotate, symmetric contest/uphold, and timeout defaults**
  (`SPEC.md` §4–§7): a bad-faith rating can be dismissed without erasing it;
  a rated party can contest a rating against them and have it upheld or
  dismissed; an exchange left unrated past its window gets a
  system-attributed `+2`, always distinguishable from an affirmed rating.
- **Two independent auth keys** (`LBTAS_API_KEY` for reads/adjudication,
  `LBTAS_SUBMIT_KEY` for submission), both failing closed with none
  configured, per `CLAUDE.md`'s "submission and review are distinct
  capabilities" rule.
- **Three test suites** (`api/test_rating_validation.py`,
  `api/test_event_store.py`, `api/test_main.py`) — the last spins up a real
  server against a temp database to cover the HTTP/auth layer end to end.

### Known limitations

- Auth is one shared secret per capability, not a credential scoped to a
  specific party or a specific served prompt.
- No trigger mechanism yet: nothing fires a rating prompt automatically off
  a transaction event; submission is direct only.
- Role-scoping is implemented in `api/` but not yet in the four reference
  CLIs (tracked separately in `CONFORMANCE.md`) — doing so would require
  changing the CLI's frozen JSON storage shape, which is out of scope here.

## [2.0.0] - 2026-06-28

Distribution release. **Breaking change to the read API:** ratings are no
longer averaged. A reputation is now the count of ratings at each level
(`-1`..`+4`) plus the total. See `CLAUDE.md` for the canonical model.

### Changed (breaking)

- **No averaging.** `view_ratings()` now returns a per-category distribution
  (`{distribution, total}`) instead of a mean. `generate_report()` returns
  overall, per-category, and per-exchange distributions. Removed
  `system_average`, `category_averages`, and the average-ranked
  `top_performers` / `bottom_performers`. Reputation is a distribution, never a
  mean — a single `-1` ("No Trust") is never diluted by surrounding praise.
- **License correction.** The authoritative license for LBTAS is and has been
  AGPL-3.0 (GNU **Affero** General Public License v3.0), consistent with NTARI's
  Licensing and Enforcement Strategy (P2-004). Any earlier MIT or plain
  `GPL-3.0` designation was a documentation error; the full AGPL-3.0 text is
  present as `LICENSE`, and every source header plus `init.py` now declare
  AGPL-3.0. Use under previously stated terms prior to this correction is
  honored; new derivative work follows AGPL-3.0.
- **Attribution clarified.** Professor Nancy Leveson, whose safety-critical
  software assessment methodology LBTAS adapts, has been informed of this work
  and does not endorse the application of her methodology to commerce
  assessment; she has not restricted NTARI's use of the underlying framework.
  LBTAS is an independent application of methods she developed for other
  purposes; any errors in the adaptation are NTARI's alone.

### Added

- **`harm_flagged`** in `generate_report()`: every exchange that received one or
  more `-1` ratings, sorted by `-1` count descending. `list` appends a
  `, Nx -1 No Trust` flag to any exchange that has a `-1`.
- **Reputation count as signal.** `view` and `report` surface the stored
  creation date as `In service since:` and label the total as transaction
  volume (`Total ratings (transaction volume): N`).
- **`CLAUDE.md`** — canonical guidance: the no-averaging rule, the
  count-as-signal rationale, the API surface (served on NTARIHQ), the mandatory
  `-1` comment (≤500 words, enforced at the API boundary), the event-store data
  model, and the authorization posture.

### Fixed

- **Build files renamed** to the names their toolchains expect:
  `view cargo.toml` → `Cargo.toml`, `view go.mod` → `go.mod`.
- **Python module renamed** `LBTAS.py` → `lbtas.py`, fixing the case mismatch
  with `init.py`'s `from .lbtas import …` that fails on case-sensitive Linux.
- **CSV export** uses a 1-based `index` column instead of a fabricated per-row
  timestamp; all four implementations share one header
  (`exchange,category,rating,index`).
- **TypeScript** `ExchangeData` typing no longer breaks `tsc --strict`.

### Notes

The four reference CLIs (`lbtas.py`, `lbtas.go`, `lbtas.rs`, `lbtas.ts`) were
migrated together and remain behaviourally identical. The CLI JSON storage shape
is unchanged (`exchange → { category: [int…], _metadata }`); distributions are
computed on read, so existing data files remain readable.

## [1.0.0]

Initial multi-language release: the `LevesonRatingSystem` class, the 6-point
scale from `-1` to `+4`, the four default criteria (reliability, usability,
performance, support), the interactive `rate_exchange()` workflow, and JSON file
storage — implemented in Python, Go, Rust, and TypeScript.

For the research framing of LBTAS, see the
[LBTAS whitepaper](https://www.ntari.org/post/lbtas-leveson-based-trade-assessment-scale).

---

[2.0.0]: https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale/releases/tag/v2.0.0
[1.0.0]: https://github.com/NTARI-RAND/Leveson-Based-Trade-Assessment-Scale/releases/tag/v1.0.0
