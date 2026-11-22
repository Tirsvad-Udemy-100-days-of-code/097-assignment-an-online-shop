# SQA Review Record

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-022 |
| CrossReference | [MIL-005], [QC-PY-001], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-23 | Proposed | Jens Tirsvad Nielsen | S01 | Code review of the MIL-005 deliverable (Stripe checkout and orders) | [abe424a] |

---

## Artifact Under Review

- Instance reviewed: the MIL-005 code (`src/`, `tests/`, `tools/`) and the step 5 wiki pages (`docs/wiki/`)
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
| 9 | `logging`, not `print`; no secrets in log output | Pass | `src/` never logs a key or a Stripe response body (tests assert it); the only `print` is the stderr message of `scripts/run_opengrep.py` |
| 10 | Trace to DCD | Pass | Order, the OrderRepository and PaymentGateway ports and the use cases follow the MIL-005 task list; no DCD exists in this plan |
| 11 | Tests for new behaviour | Pass | 289 tests pass, coverage 99.8% (limit 90%); the gateway is tested against a fake and a local fake Stripe server on 127.0.0.1, no network; key refusal (file and environment), no key in repr or errors, no redirects followed, paid-only orders, idempotent success page and foreign sessions are tested |
| 12 | Strict mypy (Optional) | Pass | `mypy --strict src` |
| 13 | Dependencies declared (Optional) | Pass | Only Flask is a runtime dependency, pinned `Flask==3.1.3` ([ADR-0002]); dev group in `pyproject.toml` |
| 14 | One place per piece of knowledge | Pass | Constants live in `constants.py` |
| 15 | Imports point inward | Pass | `tests/unit/test_layering.py` checks that domain, application and infrastructure import no Flask or Werkzeug code; domain and application import nothing from outer layers |
| 16 | SOLID | Pass | Blueprints are controllers, Jinja2 templates are views, the port keeps the repository replaceable |
| 17 | Layer and folder layout | Pass | Four layers under `src/`; `unit`, `integration`, `e2e` under `tests/` |
| 18 | File and folder names | Pass | English, no space; `.egg-info` is ignored by git |

Also run: `scripts/run_opengrep.py` 0 findings; `opengrep scan --config p/python` 0 findings; the step 5 screenshot was captured in Docker with an in-process fake gateway and viewed. One test-mode call to the real Stripe API created a Checkout Session of the right amount and read it back unpaid, so the adapter and the keys work. Go/No-Go criterion 6 (a payment with the test card) is NOT yet verified: it needs a person to pay on the Stripe page, and is recorded as an open action item.

## Overall Verdict

Go: no Mandatory criterion fails. Reviewer is the stand-in for S01, not independent.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| Pay once with the Stripe test card and record the result (criterion 6, issue 33) | S01 | before MIL-007 |

---

[MIL-005]: ../../milestones/mil-005-stripe-checkout.md
[QC-PY-001]: ../../../framework/qc/code/qc-programming-python.md
[ADR-0002]: ../../adr/adr-0002-flask-web-framework.md
[abe424a]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/commit/abe424abf48ba2b5ad74aa1151eafa325b89849a
