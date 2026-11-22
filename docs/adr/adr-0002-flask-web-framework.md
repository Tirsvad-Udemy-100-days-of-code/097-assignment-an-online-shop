# Flask web framework

## Metadata
| Key | Value |
| --- | --- |
| ID | ADR-0002 |
| CrossReference | [BC-001], [SA-001], [ADR-0001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version: Flask replaces the standard-library web layer | pending |

Allowed Status values: `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded by ADR-NNNN`.

---

## Context

The Product Owner (S01) decided in chat on 2026-11-22 that the shop uses Flask
for the website. [ADR-0001] chose the standard library and listed Flask as a
rejected option to keep the runtime dependency list empty ([BC-001], concern
CN-007 in [SA-001]). The assignment itself suggests Flask, and the first
milestones already show that a hand-written router, template and session layer
is a large share of the code.

Options evaluated:

1. Keep the standard library ([ADR-0001]). No dependencies, but more code and
   more hand-written security-sensitive code.
2. Flask for routing, requests, templates (Jinja2) and signed sessions, with
   `sqlite3`, `hashlib.scrypt` and `urllib` unchanged. One direct runtime
   dependency, which brings its own pinned dependencies (Werkzeug, Jinja2,
   itsdangerous, click, blinker, markupsafe).
3. Flask with an ORM and the Stripe package. Hides the SQL and payment calls
   the exercise teaches.

Forces: S02 and S03 can install one package into a `.venv`, readable code,
less hand-written security code, small scope, Python 3.14 or newer.

## Decision

Use option 2. Flask is the only direct runtime dependency, pinned in
`pyproject.toml`. The clean-architecture core stays unchanged: domain,
application and infrastructure do not import Flask; Flask lives in the
presentation layer (an application factory, blueprints per feature acting as
controllers, Jinja2 templates as views) and in the composition root. Sessions
use Flask's signed session cookie; CSRF tokens, password hashing
(`hashlib.scrypt`), SQLite and the Stripe REST calls (`urllib`, behind the
`PaymentGateway` port) stay as planned. Tests use the Flask test client.
[ADR-0001] is superseded for the web layer only; its decision on the
persistence, hashing and payment adapters stands.

## Consequences

**Positive:**

- Routing, request parsing, templates and sessions are maintained by a mature library.
- Jinja2 escapes output by default, which removes a class of hand-written escaping defects.
- The presentation code is shorter and closer to what the course teaches.

**Negative:**

- The "no runtime dependencies" objective of [BC-001] no longer holds; it becomes "one direct runtime dependency, Flask".
- Setup needs `pip install` of Flask and its dependencies.
- The hand-written server, router, request, response and template code of MIL-001 and MIL-002 is replaced.
- The dependency must be kept patched.

## Affected Artifacts

- [BC-001] — objective 5, KPI 5, scope, risks and constraints change.
- [SA-001] — the conflict "real payment versus no runtime dependencies" is reworded.
- [ADR-0001] — superseded for the web layer.

---

[BC-001]: ../business-case.md
[SA-001]: ../stakeholder-analysis.md
[ADR-0001]: ./adr-0001-standard-library-stack.md
