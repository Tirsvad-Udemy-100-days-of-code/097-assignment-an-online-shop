# Business Case: Online Shop

## Metadata
| Key | Value |
| --- | --- |
| ID | BC-001 |
| CrossReference | [SA-001], [ADR-0002] |
| Language | en |
| Domain | it |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Deprecated | Jens Tirsvad Nielsen | S01 | Accepted after review RC-002; stand-in review, not independent | [bfd7827] |
| 2026-11-22 | Accepted | Jens Tirsvad Nielsen | S01 | Flask as the only runtime dependency (objective 5, KPI 5, scope, risk, constraint) per ADR-0002; accepted after review RC-014, stand-in review, not independent | [4d90862] |

---

## Executive Summary

Day 97 of the 100 Days of Code bootcamp asks the participant to build an
eCommerce website with a working basket and checkout, real payment processing
and login and registration. The Product Owner builds it as a small, readable
Python shop built with Flask, takes payment through Stripe
Checkout in a Stripe sandbox, and gives the shop owner a Kanban board to track
orders from "Needs confirmation" to "Delivered", in the style of the Day 89
todo list. It is documented in three languages and every build step is shown
with a screenshot. It serves as a portfolio piece and as a reference for other
course participants.

## Methodological and Standards Foundation

- Methodology: Larman, *Applying UML and Patterns*, for the domain model and
  use cases; Clean Architecture for the layers; MVC for the web presentation.
- Quality standard: ISO/IEC 25010:2023 characteristics tag every QC criterion.
- Process: the project's SQA and QC framework (plan first, review each artifact,
  one pull request per milestone).
- Code: Python 3.14 or newer, pytest, doxygen comments, constants kept in
  `constants.py`.

## Problem Statement

1. An online shop is the capstone of a web course, but many solutions stop at a
   product list and skip payment, accounts and order handling, so they show
   little of what a real shop needs.
2. A shop that takes payment but gives its owner no way to follow an order
   from payment to delivery is incomplete; a Kanban board is a familiar way
   to show that flow.
3. The belief that would kill the idea if false: payment through Stripe
   Checkout can be integrated with the Python standard library (`urllib`)
   alone, in test mode, without a Stripe package. If it cannot, the
   "Flask is the only direct runtime dependency" promise to S03 breaks.

## Business Opportunity

A finished, tested and documented shop gives S01 a concrete artifact for
interviews, gives S02 a clear solution to compare with their own, and gives
S03 a repository with ideas that runs with a few commands.

## Objectives

1. Deliver a web shop that lists products, shows product details and keeps a
   working shopping basket, stored persistently.
2. Provide registration, login and logout, with safe password storage, signed
   sessions and an admin role.
3. Take payment through Stripe Checkout, tested in a Stripe sandbox with test
   keys, and create an order only from a paid session.
4. Give the admin a Kanban board of orders with the columns Needs confirmation,
   Confirmed, Being packed, Shipped and Delivered, moved by drag and drop, and
   give each customer a view of their own order status.
5. Ship it with Flask as the only direct runtime dependency, tests with pytest, doxygen comments, a
   Doxyfile, a README that documents a local `.venv`, running the shop and
   running the tests.
6. Show every build step with a screenshot in the README and in the wiki, and
   explain in the wiki what each step taught, in English, Danish and Bahasa Malaysia.
7. Publish the repository with a description and topics.

## Scope

### In Scope

- A single-shop web application: product catalog, product detail, basket,
  checkout with Stripe, registration, login, logout, customer order history
  and an admin order board.
- Persistence in a local SQLite file; a small seeded catalog.
- Stripe Checkout in test mode, called through the Stripe REST API with
  `urllib`; a fake gateway for tests.
- Unit, integration and browser tests; the browser tests and the screenshots run
  in a Docker container.
- README from the framework template; wiki in three languages; Doxyfile;
  `pyproject.toml`; Python `.gitignore`; a static code scan with opengrep before
  every push.
- Repository description and topics on the git host.

### Out of Scope

- Live payments, refunds, taxes, shipping rates, discount codes and invoices.
- Product management screens for the admin (the catalog is seeded).
- Email delivery, password reset and social sign-in.
- Deployment to a public server and any paid service.
- Third-party runtime packages.

## Expected Benefits

### Tangible Benefits

- A runnable portfolio project with a passing test suite.
- A README and a three-language wiki a newcomer can follow without help.
- Screenshots that prove each step works.

### Intangible Benefits

- Practice in planning, layering and testing a complete shop with payment.
- A written reflection that helps the next project.

## Strategic Alignment

The project completes Day 97 of the bootcamp and supports the participant's
goal of a strong interview portfolio. It reuses the Kanban design of the Day 89
project and follows the framework's plan-first workflow, so the repository
also demonstrates process, not only code.

## Success Criteria

| # | Criterion | Target | Measure |
| --- | --- | --- | --- |
| 1 | Shop features work | Browse, register, sign in, add to basket and check out pass an end-to-end test against a fake gateway | Browser test in a container exits 0 |
| 2 | Real payment in test mode | One test payment with the Stripe test card completes in the sandbox | Recorded result of the sandbox run |
| 3 | Order board | A paid order moves across all five columns and keeps its place after reload | Browser test in a container exits 0 |
| 4 | Tests | At least 90 percent line coverage of `src/` on unit and integration tests | pytest coverage report |
| 5 | One runtime dependency | `[project].dependencies` lists only Flask, pinned | Inspect `pyproject.toml` |
| 6 | Setup works from the README | A fresh clone reaches a running shop in 6 commands or fewer | Follow the README in a clean container |
| 7 | Screenshots | One screenshot per build step (6) in the README and in every wiki language | Count image links |
| 8 | Wiki languages | 3 languages with the same page set | Page list of `docs/wiki/` |
| 9 | Static scan | 0 findings of severity error from opengrep at each push | Scan output |
| 10 | Repository metadata | Description and at least 5 topics set | Read back from the git host |

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Stripe integration without its package is harder than expected | Schedule slip on the payment milestone | Call only two REST endpoints (create and retrieve a Checkout Session); keep a gateway port and a fake |
| Stripe keys leak into the repository or logs | Security defect | Keys live only in the ignored `.env`, are never printed, never committed; opengrep scan before each push |
| Account and session code has flaws | Security defect | Use Flask's signed session, `hashlib.scrypt` and `secrets`; CSRF tokens; tests for tampering |
| Screenshots need a browser and the host desktop must not be used | Screenshots not produced | Headless browser in a Docker container; stop and report if Docker is unavailable |
| The test keys in `stripe.env` are rejected by Stripe | Payment milestone blocked | Stop and report; the gateway port and fake let other work continue |
| Wiki translations drift from English | Inconsistent documentation | English is written first; the page set is checked equal across languages |

## Assumptions

- S01 is the Product Owner, developer and reviewer, and reachable in chat.
- S02 and S03 are reached only through the published repository.
- The git host `git.tirsystem.com` accepts the tokens in `.env`, and the
  repository exists under the organization `Tirsvad-Udemy-100_days_of_code`.
- Docker is available on the development machine.
- S01 supplies the Stripe sandbox test keys in a local `stripe.env` file (test mode only); the Chrome dashboard is used only if a key must be checked.
- The wiki is enabled in the repository settings.

## Constraints

- Python 3.14 or newer; a local `.venv`; pytest; constants in `constants.py`.
- Folders `src/`, `tests/` and `docs/`.
- Flask is the only direct runtime dependency ([ADR-0002]); no ORM and no Stripe package.
- No artifact of the repository names the tools used to write it.
- Duration: finish by 2026-12-11, about 200 minutes of course effort plus
  documentation work.
- Tokens come from `.env` for personal use only; the git host tokens are not
  imported into the project, tested or committed. Only the Stripe test keys of
  the sandbox are read by the running shop, from environment variables.

## Cost–Benefit Assessment

| Costs | Benefits |
| --- | --- |
| About 50 hours of S01's time across the plan, including documentation and translation | A portfolio-grade shop, a reference for S02, a repository of ideas for S03 |
| No licences or hosting fees; Stripe test mode is free | No recurring cost |

The assessment is qualitative because the project is a learning exercise with
no revenue.

## Stakeholders

| ID | Role in this project |
| --- | --- |
| S01 | Product Owner, developer and reviewer |
| S02 | Udemy participants who compare solutions |
| S03 | Repository viewers who look for ideas |

The roles, power and interest of each are in [SA-001].

## Recommendation

Proceed.

---

[SA-001]: ./stakeholder-analysis.md
[bfd7827]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/commit/bfd782710394ff04fce3f51f464e5e342cbeb4ca
[ADR-0002]: ./adr/adr-0002-flask-web-framework.md
[4d90862]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/commit/4d908627163f1be713505164ac4973b394740c4f
