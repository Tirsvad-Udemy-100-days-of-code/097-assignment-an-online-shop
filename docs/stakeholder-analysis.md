# Stakeholder Analysis

## Metadata
| Key | Value |
| --- | --- |
| ID | SA-001 |
| CrossReference | [BC-001] |
| Language | en |
| Domain | it |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Deprecated | Jens Tirsvad Nielsen | S01 | Accepted after review RC-001; stand-in review, not independent | [bfd7827] |
| 2026-11-22 | Accepted | Jens Tirsvad Nielsen | S01 | Reworded the payment conflict for Flask per ADR-0002; accepted after review RC-015, stand-in review, not independent | pending |

---

## Purpose

This analysis names the people the online shop serves, how much power and
interest each has, and what each expects. It follows the power/interest grid
and maps each concern to a FURPS+ attribute so the plan can answer it.

## Stakeholder Summary Table

| ID | Name | Role/Title | Organization | Power Level | Interest Level | Quadrant | Primary Concern (Business Language) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | Jens Tirsvad Nielsen | Course participant; Product Owner, developer and reviewer | Tirsvad | HIGH | HIGH | Manage Closely | A working, tested shop with real payment flow that impresses an interviewer |
| S02 | Udemy participants | Course participants who share code and compare solutions | Udemy community | LOW | HIGH | Keep Informed | Readable, runnable code with the assignment's names and README instructions |
| S03 | Repository viewers | Visitors who browse the repository for ideas | GitHub and Gitea community | LOW | MEDIUM | Monitor | A clear description, topics and README, and no runtime dependencies |

## Power/Interest Classification Rationale

- **Manage Closely (S01):** decides scope, reviews every artifact and accepts the plan.
- **Keep Informed (S02):** cannot change the project but depends on its clarity.
  They get the README and wiki.
- **Monitor (S03):** casual visitors; the repository description, topics and
  README serve them without further contact.

## Primary Concerns and FURPS+ Mapping

| Concern ID | Stakeholder | Concern | FURPS+ attribute |
| --- | --- | --- | --- |
| CN-001 | S01 | The shop must have a working basket, checkout, login and registration | Functionality |
| CN-002 | S01 | Tests and quality checks must give confidence before every push | Reliability |
| CN-003 | S01 | Progress must be traceable through branches and pull requests | Supportability |
| CN-004 | S02 | The code must be readable and use the assignment's names | Supportability |
| CN-005 | S02 | A newcomer must be able to run the project and its tests from the README | Usability |
| CN-006 | S03 | The repository must have a clear description, topics and README | Usability |
| CN-007 | S03 | The project must not require installing runtime packages | Implementation constraint |
| CN-008 | S02 | Every build step must be shown by a screenshot and explained in the wiki, in English, Danish and Bahasa Malaysia | Usability |
| CN-009 | S01 | Payment keys and passwords must be kept safe | Reliability |
| CN-010 | S01 | Orders must be tracked on a Kanban board from confirmation to delivery | Functionality |

## Communication Requirements

| ID | Channel | Frequency | Deliverable | Phase / Milestone |
| --- | --- | --- | --- | --- |
| COM-001 | Chat with S01 | At plan acceptance and at the end of the run | Plan; run summary | All |
| COM-002 | Pull request description | One per milestone | Changes and closed issues | MIL-001 to MIL-007 |
| COM-003 | README and wiki | Updated every milestone | Instructions, screenshots, lessons | MIL-001 to MIL-007 |

## Conflicting Interests and Mitigations

| Conflict | Stakeholders | Mitigation |
| --- | --- | --- |
| Real payment through Stripe versus a short dependency list | S01, S03 | Call the Stripe REST API with the standard library, behind a port; Flask is the only direct dependency |
| Three-language wiki effort versus delivery date | S01, S02 | English first; translations follow page by page within the same milestone |

## Traceability Analysis

### Business Goal Alignment

| Stakeholder | Concern | Business Case objective |
| --- | --- | --- |
| S01 | CN-001 | Objectives 1, 2 and 3 of [BC-001] |
| S01 | CN-010 | Objective 4 of [BC-001] |
| S01 | CN-002, CN-003, CN-009 | Objectives 3 and 5 of [BC-001] |
| S02 | CN-004, CN-005 | Objective 5 of [BC-001] |
| S02 | CN-008 | Objective 6 of [BC-001] |
| S03 | CN-006 | Objective 7 of [BC-001] |
| S03 | CN-007 | Objective 5 of [BC-001] |

## Sign-Off

| Stakeholder | Decision | Date |
| --- | --- | --- |
| S01 | pending review | |

---

[BC-001]: ./business-case.md
[bfd7827]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/commit/bfd782710394ff04fce3f51f464e5e342cbeb4ca
