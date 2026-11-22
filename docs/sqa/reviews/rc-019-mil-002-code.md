# SQA Review Record

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-019 |
| CrossReference | [MIL-002], [QC-PY-001], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Proposed | Jens Tirsvad Nielsen | S01 | Code review of the MIL-002 deliverable on Flask ([ADR-0002]) | [b5dc5b5] |

---

## Artifact Under Review

- Instance reviewed: the MIL-002 code (`src/`, `tests/`, `tools/`) and the step 2 wiki pages (`docs/wiki/`)
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
| 9 | `logging`, not `print` | Pass | The only `print` is the stderr message of the CLI script `scripts/run_opengrep.py` |
| 10 | Trace to DCD | Pass | Product, Money and ProductRepository follow the MIL-002 task list; no DCD exists in this plan |
| 11 | Tests for new behaviour | Pass | 56 tests pass, coverage 100% (limit 90%); tests use the Flask test client and a temporary SQLite file, no network |
| 12 | Strict mypy (Optional) | Pass | `mypy --strict src` |
| 13 | Dependencies declared (Optional) | Pass | Only Flask is a runtime dependency, pinned `Flask==3.1.3` ([ADR-0002]); dev group in `pyproject.toml` |
| 14 | One place per piece of knowledge | Pass | Constants live in `constants.py` |
| 15 | Imports point inward | Pass | `tests/unit/test_layering.py` checks that domain, application and infrastructure import no Flask or Werkzeug code; domain and application import nothing from outer layers |
| 16 | SOLID | Pass | Blueprints are controllers, Jinja2 templates are views, the port keeps the repository replaceable |
| 17 | Layer and folder layout | Pass | Four layers under `src/`; `unit`, `integration`, `e2e` under `tests/` |
| 18 | File and folder names | Pass | English, no space; `.egg-info` is ignored by git |

Also run: `scripts/run_opengrep.py` 0 findings; the step 2 screenshot was captured in Docker from the Flask app and viewed.

## Overall Verdict

Go: no Mandatory criterion fails. Reviewer is the stand-in for S01, not independent.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| none | S01 | - |

---

[MIL-002]: ../../milestones/mil-002-catalog-storage.md
[QC-PY-001]: ../../../framework/qc/code/qc-programming-python.md
[ADR-0002]: ../../adr/adr-0002-flask-web-framework.md
[b5dc5b5]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/commit/b5dc5b570d69026ab3b7c8b65bdebd6d2da33533
