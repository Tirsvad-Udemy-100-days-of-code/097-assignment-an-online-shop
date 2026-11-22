# Milestone 4: Shopping basket

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-004 |
| CrossReference | [BC-001] |
| Language | en |
| Domain | it |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Deprecated | Jens Tirsvad Nielsen | S01 | Initial version | pending |
| 2026-11-22 | Accepted | Jens Tirsvad Nielsen | S01 | Accepted after review RC-008; stand-in review, not independent | pending |

---

## Purpose

Decide whether a shopper can collect products in a working basket before paying.

## Deliverable

A basket that adds, changes and removes products, shows totals, and belongs to the signed-in user, with tests and the step 4 screenshot.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | Adding a product twice increases its quantity | Met | Not met: fix and review again |
| 2 | Quantity can be changed or set to 0 to remove the line | Met | Not met: fix and review again |
| 3 | The basket total equals the sum of price times quantity in cents | Met | Not met: fix and review again |
| 4 | The basket is kept after logout and login | Met | Not met: fix and review again |
| 5 | A visitor who is not signed in is asked to sign in when adding to the basket | Met | Not met: fix and review again |
| 6 | `docs/screenshots/step-04.png` exists and is shown in the README and the wiki | Met | Not met: fix and review again |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-003 | Signed-in user |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| Objective 1 | [BC-001] |
| CN-001 | [SA-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S01 |
| Approving reviewer | S01 |

## Target Date

2026-12-02 — inside the plan window.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Model the basket | Add the Basket and BasketLine entities with quantity limits and totals, with unit tests. | No |  |
| 2 | Implement basket storage and use cases | Add the SQLite basket repository and the add, update, remove and view use cases, with integration tests. | No |  |
| 3 | Build the basket page and add to basket buttons | Add the basket controller, the basket page, and add to basket forms on the catalog and detail pages with CSRF tokens. | No |  |
| 4 | Show the basket count in the navigation | Add a basket item count to the navigation bar for signed-in users. | No |  |
| 5 | Capture step screenshot for step 4 | Capture docs/screenshots/step-04.png of a filled basket and add it to the README. | No |  |
| 6 | Write wiki pages for step 4 | Write the three-language wiki pages about the basket model and totals. | No |  |

---


[BC-001]: ../business-case.md
