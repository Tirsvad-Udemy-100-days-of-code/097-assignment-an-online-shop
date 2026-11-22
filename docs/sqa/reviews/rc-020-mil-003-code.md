# SQA Review Record

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-020 |
| CrossReference | [MIL-003], [QC-PY-001], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-23 | Proposed | Jens Tirsvad Nielsen | S01 | Code review of the MIL-003 deliverable on Flask ([ADR-0002]) | [d0d75f8] |

---

## Artifact Under Review

- Instance reviewed: the MIL-003 code (`src/`, `tests/`, `tools/`) and the step 3 wiki pages (`docs/wiki/`)
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
| 9 | `logging`, not `print`; no secrets in log output | Pass | `src/` logs only a notice that the admin account was created (no email or password) and a warning when the session key is generated; the admin password is never logged and is hidden from `repr`; the only `print` is the stderr message of `scripts/run_opengrep.py` |
| 10 | Trace to DCD | Pass | User, the hasher and repository ports and the use cases follow the MIL-003 task list; no DCD exists in this plan |
| 11 | Tests for new behaviour | Pass | 117 tests pass, coverage 99.5% (limit 90%); tests use the Flask test client and a temporary SQLite file, no network; tampered cookie, wrong CSRF token, duplicate email, open redirect and the three admin cases are tested |
| 12 | Strict mypy (Optional) | Pass | `mypy --strict src` |
| 13 | Dependencies declared (Optional) | Pass | Only Flask is a runtime dependency, pinned `Flask==3.1.3` ([ADR-0002]); dev group in `pyproject.toml` |
| 14 | One place per piece of knowledge | Pass | Constants live in `constants.py` |
| 15 | Imports point inward | Pass | `tests/unit/test_layering.py` checks that domain, application and infrastructure import no Flask or Werkzeug code; domain and application import nothing from outer layers |
| 16 | SOLID | Pass | Blueprints are controllers, Jinja2 templates are views, the port keeps the repository replaceable |
| 17 | Layer and folder layout | Pass | Four layers under `src/`; `unit`, `integration`, `e2e` under `tests/` |
| 18 | File and folder names | Pass | English, no space; `.egg-info` is ignored by git |

Also run: `scripts/run_opengrep.py` 0 findings; `opengrep scan --config p/python` 0 findings; the step 3 screenshot is captured in Docker from the Flask app and viewed.

## Overall Verdict

Go: no Mandatory criterion fails. Reviewer is the stand-in for S01, not independent.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| none | S01 | - |

---

[MIL-003]: ../../milestones/mil-003-accounts.md
[QC-PY-001]: ../../../framework/qc/code/qc-programming-python.md
[ADR-0002]: ../../adr/adr-0002-flask-web-framework.md
[d0d75f8]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/commit/d0d75f899ac765e167a21b72a4d7a93f4fcad265
