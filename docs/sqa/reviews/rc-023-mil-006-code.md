# SQA Review Record

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-023 |
| CrossReference | [MIL-006], [QC-PY-001], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-23 | Proposed | Jens Tirsvad Nielsen | S01 | Code review of the MIL-006 deliverable (order Kanban board and order history) | [94264f4] |

---

## Artifact Under Review

- Instance reviewed: the MIL-006 code (`src/`, `tests/`, `tools/`) and the step 6 wiki pages (`docs/wiki/`)
- Checklist used: [QC-PY-001]
- Scope: full review
- Mode: autonomous, not independent (the reviewer is AI as stand-in for S01)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | PEP 8 casing | Pass | `ruff check` clean |
| 2 | Names state purpose | Pass | Read through |
| 3 | Formatter and linter, no unexplained suppressions | Pass | `ruff check`: all checks passed; one `nosemgrep` in the Dockerfile has a reason comment |
| 4 | Signatures type-annotated | Pass | `mypy src tests`: no issues (Flask ships types) |
| 5 | No bare except | Pass | grep finds none |
| 6 | No mutable defaults, no shadowed builtins | Pass | ruff clean |
| 7 | Context managers | Pass | Read through |
| 8 | Docstrings (Optional) | Pass | Doxygen comments in `src/` |
| 9 | `logging`, not `print`; no secrets in log output | Pass | `src/` logs no order data; the only `print` is the stderr message of `scripts/run_opengrep.py` |
| 10 | Trace to DCD | Pass | The statuses, placement rule, MoveOrder, ViewBoard and ListMyOrders follow the MIL-006 task list; no DCD exists in this plan |
| 11 | Tests for new behaviour | Pass | 341 tests pass, coverage 99.81% (limit 90%); roles on every board route, CSRF on the move, persistence across a new session, position renumbering, the v4 to v5 migration and rollback on a failed write are tested; 6 browser tests pass in the Docker container (real drag then reload, customer status, 403, 400 px, refused move reverted, select without drag) |
| 12 | Strict mypy (Optional) | Pass | `mypy --strict src` |
| 13 | Dependencies declared (Optional) | Pass | Only Flask is a runtime dependency, pinned `Flask==3.1.3` ([ADR-0002]); dev group in `pyproject.toml` |
| 14 | One place per piece of knowledge | Pass | Constants live in `constants.py` |
| 15 | Imports point inward | Pass | `tests/unit/test_layering.py` checks that domain, application and infrastructure import no Flask or Werkzeug code; domain and application import nothing from outer layers |
| 16 | SOLID | Pass | Blueprints are controllers, Jinja2 templates are views, the port keeps the repository replaceable |
| 17 | Layer and folder layout | Pass | Four layers under `src/`; `unit`, `integration`, `e2e` under `tests/` |
| 18 | File and folder names | Pass | English, no space; `.egg-info` is ignored by git |

Also run: `scripts/run_opengrep.py` 0 findings; `opengrep scan --config p/python` 0 findings; the step 6 screenshot was captured in Docker and viewed. `board.js` is plain JavaScript with no inline handlers and builds the DOM with `textContent` only. The Day 89 project was read, not changed.

## Overall Verdict

Go: no Mandatory criterion fails. Reviewer is the stand-in for S01, not independent.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| none | S01 | - |

---

[MIL-006]: ../../milestones/mil-006-order-kanban.md
[QC-PY-001]: ../../../framework/qc/code/qc-programming-python.md
[ADR-0002]: ../../adr/adr-0002-flask-web-framework.md
[94264f4]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/commit/94264f4b666049e069a71f5b4511583e22eea3f6
