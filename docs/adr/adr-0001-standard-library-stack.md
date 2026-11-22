# ADR-0001: Standard-library stack

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0001 |
| CrossReference | [BC-001], [SA-001], [ADR-0002] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Deprecated | Jens Tirsvad Nielsen | S01 | Accepted after review RC-004; stand-in review, not independent | [bfd7827] |
| 2026-11-22 | Superseded by ADR-0002 | Jens Tirsvad Nielsen | S01 | Web layer now Flask; the rest stands | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

The online shop must run for S02 and S03 without installing runtime
packages ([BC-001], concern CN-007 in [SA-001]). It needs a web server, a
database, accounts, a payment provider and a page that updates without reload.
The assignment suggests Flask and the Stripe package.

Options evaluated:

1. Flask, an ORM and the Stripe package. Fast to write, but adds runtime
   dependencies and hides the HTTP, SQL and payment calls the exercise teaches.
2. The Python standard library: `http.server`, `sqlite3`, `hashlib.scrypt`,
   `hmac`, `urllib` for the Stripe REST API, and plain JavaScript in the
   browser. More code, no dependencies.
3. A single-page application with a JavaScript build tool. Adds a second
   toolchain and Node as a requirement.

Forces: no runtime dependencies, readable code, small scope, secrets kept out
of the repository, Python 3.14 or newer.

## Decision

Use option 2, with an MVC presentation layer over a clean-architecture core
(domain, application, infrastructure, presentation). Stripe sits behind a
`PaymentGateway` port; the adapter uses `urllib` and a fake serves the tests.
Development tools (pytest, ruff, mypy) stay in an optional `dev` group.

## Consequences

**Positive:**

- The runtime dependency list is empty; setup is a virtual environment and one command.
- Every layer is visible and testable; the payment provider can be replaced or faked.

**Negative:**

- More code than a framework (router, sessions, CSRF, form handling).
- Security-sensitive code is written by hand and needs focused tests.
- `http.server` is not meant for heavy load; the scope is a demonstration shop.

## Affected Artifacts

- [BC-001]
- [SA-001]
- [ADR-0002] — supersedes this decision for the web layer

---

[BC-001]: ../business-case.md
[SA-001]: ../stakeholder-analysis.md
[ADR-0002]: ./adr-0002-flask-web-framework.md
[bfd7827]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/commit/bfd782710394ff04fce3f51f464e5e342cbeb4ca
