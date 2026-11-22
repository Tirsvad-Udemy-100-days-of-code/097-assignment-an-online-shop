# Milestone 5: Stripe checkout

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-005 |
| CrossReference | [BC-001] |
| Language | en |
| Domain | it |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Deprecated | Jens Tirsvad Nielsen | S01 | Initial version | [bfd7827] |
| 2026-11-22 | Accepted | Jens Tirsvad Nielsen | S01 | Accepted after review RC-009; stand-in review, not independent | [bfd7827] |

---

## Purpose

Decide whether the shop takes real payment through Stripe, tested in a Stripe sandbox.

## Deliverable

A checkout that creates a Stripe Checkout Session through the Stripe REST API with the standard library, redirects the shopper to Stripe, confirms payment on return and creates a paid order, tested with a fake gateway and once against the Stripe test mode, with the step 5 screenshot.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The sandbox test keys are read only from the local stripe.env, which is ignored by git, and a live key is refused | Met | Not met: fix and review again |
| 2 | Checkout creates a Stripe Checkout Session whose line items match the basket | Met | Not met: fix and review again |
| 3 | On return the session is retrieved from Stripe and only a paid session creates an order | Met | Not met: fix and review again |
| 4 | A cancelled payment keeps the basket and creates no order | Met | Not met: fix and review again |
| 5 | The payment gateway is a port, and tests run against a fake without network | Met | Not met: fix and review again |
| 6 | A test payment with the Stripe test card succeeds in the sandbox | Met | Not met: fix and review again |
| 7 | `docs/screenshots/step-05.png` exists and is shown in the README and the wiki | Met | Not met: fix and review again |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-004 | Basket to pay for |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| Objective 3 | [BC-001] |
| CN-001, CN-009 | [SA-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S01 |
| Approving reviewer | S01 |

## Target Date

2026-12-07 — inside the plan window.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Load the Stripe sandbox test keys | Read the sandbox test keys from the local, git-ignored stripe.env (publishable and secret key, test mode only) into environment variables at start, refuse live keys, never print them, and note the steps in the wiki. | No |  |
| 2 | Define the payment gateway port | Add a PaymentGateway port and a fake adapter for tests, with the order and payment domain rules. | No |  |
| 3 | Implement the Stripe adapter | Add an adapter using urllib that creates a Checkout Session and retrieves it, with form encoding, errors handled and tests on a local fake Stripe server. | No |  |
| 4 | Create orders from paid sessions | Add the checkout, success and cancel use cases and controllers, an Order entity with status Needs confirmation and a SQLite order repository. | No |  |
| 5 | Run a sandbox payment end to end | Pay with the Stripe test card in the sandbox through a Docker browser and record the result; keys are never printed. | No |  |
| 6 | Capture step screenshot for step 5 | Capture docs/screenshots/step-05.png of the checkout and success pages and add it to the README. | No |  |
| 7 | Write wiki pages for step 5 | Write the three-language wiki pages about Stripe Checkout, test mode and handling keys. | No |  |

---


[BC-001]: ../business-case.md
[bfd7827]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/commit/bfd782710394ff04fce3f51f464e5e342cbeb4ca
