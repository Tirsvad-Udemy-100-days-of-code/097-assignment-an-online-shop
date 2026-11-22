# Milestone 2: Product catalog and storage

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-002 |
| CrossReference | [BC-001] |
| Language | en |
| Domain | it |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Deprecated | Jens Tirsvad Nielsen | S01 | Initial version | pending |
| 2026-11-22 | Accepted | Jens Tirsvad Nielsen | S01 | Accepted after review RC-006; stand-in review, not independent | pending |

---

## Purpose

Decide whether the shop can store and show products, which every later feature depends on.

## Deliverable

Product entity, SQLite repository, seeded catalog, product list and product detail pages, tests and the step 2 screenshot.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | Products are stored in SQLite and survive a restart | Met | Not met: fix and review again |
| 2 | The home page lists all seeded products with name, image, description and price | Met | Not met: fix and review again |
| 3 | A product detail page shows one product and answers 404 for an unknown id | Met | Not met: fix and review again |
| 4 | Domain and application layers import nothing from infrastructure or presentation | Met | Not met: fix and review again |
| 5 | `docs/screenshots/step-02.png` exists and is shown in the README and the wiki | Met | Not met: fix and review again |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-001 | Tooling, skeleton and server |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| Objective 1 | [BC-001] |
| CN-001, CN-004 | [SA-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S01 |
| Approving reviewer | S01 |

## Target Date

2026-11-26 — inside the plan window.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Model products and money | Add the Product entity and a Money value in whole minor units (cents) with validation, and a repository port, with unit tests. | No |  |
| 2 | Implement the SQLite product repository | Add a sqlite3 adapter behind the port, with migration on start and a seed of sample products, with integration tests. | No |  |
| 3 | Add the list and detail use cases | Add use cases that list products and fetch one product, mapped to DTOs, with unit tests. | No |  |
| 4 | Render the catalog pages | Add the product grid on the home page and the product detail page with a small router, templates written with string.Template and a stylesheet. | No |  |
| 5 | Capture step screenshot for step 2 | Capture docs/screenshots/step-02.png of the catalog and add it to the README. | No |  |
| 6 | Write wiki pages for step 2 | Write the three-language wiki pages about layering, SQLite and money in cents. | No |  |

---


[BC-001]: ../business-case.md
