# Milestone 6: Order Kanban board

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-006 |
| CrossReference | [BC-001] |
| Language | en |
| Domain | it |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Deprecated | Jens Tirsvad Nielsen | S01 | Initial version | [bfd7827] |
| 2026-11-22 | Accepted | Jens Tirsvad Nielsen | S01 | Accepted after review RC-010; stand-in review, not independent | [bfd7827] |

---

## Purpose

Decide whether the shop owner can track orders on a Kanban board like the Day 89 todo list.

## Deliverable

An admin-only Kanban board with the columns Needs confirmation, Confirmed, Being packed, Shipped and Delivered, where order cards move by drag and drop, a customer order history, tests and the step 6 screenshot.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | A paid order appears in Needs confirmation | Met | Not met: fix and review again |
| 2 | Dragging an order to another column changes its status and survives a reload | Met | Not met: fix and review again |
| 3 | Only an admin can see the board and move orders; a customer cannot | Met | Not met: fix and review again |
| 4 | A customer sees the current status of their own orders | Met | Not met: fix and review again |
| 5 | Layout works at 1280 and 400 pixel widths | Met | Not met: fix and review again |
| 6 | `docs/screenshots/step-06.png` exists and is shown in the README and the wiki | Met | Not met: fix and review again |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-005 | Paid orders |
| Day 89 todo list | Board design, drag and drop and layout used as the model |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| Objective 4 | [BC-001] |
| CN-001, CN-010 | [SA-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S01 |
| Approving reviewer | S01 |

## Target Date

2026-12-10 — inside the plan window.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Model order statuses and moves | Add the five statuses and the transition and move use case with positions, with unit tests. | No |  |
| 2 | Add the board API | Add admin-only endpoints that list the board and move an order, with integration tests. | No |  |
| 3 | Build the board page and drag and drop | Port the Day 89 board layout and plain JavaScript drag and drop to order cards with customer, items and total. | No |  |
| 4 | Add the customer order history | Add a page where a customer sees their orders and status. | No |  |
| 5 | Add the end-to-end board test | Test in a headless browser in a Docker container that a dragged order stays moved after reload. | No |  |
| 6 | Capture step screenshot for step 6 | Capture docs/screenshots/step-06.png of the order board and add it to the README. | No |  |
| 7 | Write wiki pages for step 6 | Write the three-language wiki pages about the board, status flow and what was reused from Day 89. | No |  |

---


[BC-001]: ../business-case.md
[bfd7827]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/commit/bfd782710394ff04fce3f51f464e5e342cbeb4ca
