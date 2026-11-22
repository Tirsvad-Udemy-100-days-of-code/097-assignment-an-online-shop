# Milestone 7: Wiki, reflection and release

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-007 |
| CrossReference | [BC-001] |
| Language | en |
| Domain | it |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Deprecated | Jens Tirsvad Nielsen | S01 | Initial version | pending |
| 2026-11-22 | Accepted | Jens Tirsvad Nielsen | S01 | Accepted after review RC-011; stand-in review, not independent | pending |

---

## Purpose

Decide whether the project is complete, documented and ready to be shared.

## Deliverable

A complete three-language wiki, the README reflection and gallery, final quality checks and the repository metadata.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | The wiki has the same page set in en, da and ms | Met | Not met: fix and review again |
| 2 | Every step 1 to 6 screenshot is in the README and in every wiki language | Met | Not met: fix and review again |
| 3 | The README holds the reflection answering the assignment questions | Met | Not met: fix and review again |
| 4 | Coverage is at least 90 percent on unit and integration tests and opengrep reports 0 errors | Met | Not met: fix and review again |
| 5 | `framework/scripts/check-readme.sh` and `check-plan.sh` pass | Met | Not met: fix and review again |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-006 | All features done |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| Objectives 4, 5 and 6 | [BC-001] |
| CN-008 | [SA-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S01 |
| Approving reviewer | S01 |

## Target Date

2026-12-11 — inside the plan window.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Complete the wiki home pages and sidebar | Add Home and _Sidebar pages in en, da and ms linking every step page. | No |  |
| 2 | Write the reflection | Write the reflection in the README: approach, what was hard and easy, biggest learning and what to do differently. | No |  |
| 3 | Run the final checks | Run pytest with coverage, ruff, mypy, opengrep and the framework check scripts and fix findings. | No |  |
| 4 | Verify repository metadata | Read the description and topics back from the git host and fix them if needed. | No |  |

---


[BC-001]: ../business-case.md
