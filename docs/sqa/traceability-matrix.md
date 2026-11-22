# Traceability Matrix

## Metadata
| Key | Value |
| --- | --- |
| ID | TM-001 |
| CrossReference | [BC-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Proposed | Jens Tirsvad Nielsen | S01 | Initial version | [bfd7827] |
| 2026-11-22 | Proposed | Jens Tirsvad Nielsen | S01 | Added ADR-0002 and the reviews RC-013 to RC-018 for the Flask change | pending |

---

## Purpose

Tracks backward/forward links between artifact instances so that the Business Case's
cross-artifact traceability success criterion is measurable. A row is added or
updated whenever an artifact instance is created or reviewed.

## Traceability Table

| Artifact Instance | Type | Language | Domain | Upstream (Backward Link) | Downstream (Forward Link) | Last Reviewed (RC-ID) |
| --- | --- | --- | --- | --- | --- | --- |
| BC-001 | Business Case | en | it | - | SA-001, PP-001 | RC-014 |
| SA-001 | Stakeholder Analysis | en | it | BC-001 | PP-001 | RC-015 |
| PP-001 | Project Plan | en | it | BC-001, SA-001 | MIL-001 to MIL-007 | RC-016 |
| ADR-0001 | ADR | - | - | BC-001, SA-001 | ADR-0002 | RC-004 |
| ADR-0002 | ADR | - | - | BC-001, SA-001, ADR-0001 | - | RC-013 |
| MIL-001 | Milestone | en | it | BC-001 | - | RC-005 |
| MIL-002 | Milestone | en | it | BC-001 | - | RC-017 |
| MIL-003 | Milestone | en | it | BC-001 | - | RC-018 |
| MIL-004 | Milestone | en | it | BC-001 | - | RC-008 |
| MIL-005 | Milestone | en | it | BC-001 | - | RC-009 |
| MIL-006 | Milestone | en | it | BC-001 | - | RC-010 |
| MIL-007 | Milestone | en | it | BC-001 | - | RC-011 |

## Concern Coverage

| Concern (CN-ID) | Views that answer it | Decisions (ADR) | Quality check (TP) | Status |
| --- | --- | --- | --- | --- |
| CN-001 | - | ADR-0001 | - | Gap |
| CN-002 | - | ADR-0001 | - | Gap |
| CN-003 | - | ADR-0001 | - | Gap |
| CN-004 | - | ADR-0001 | - | Gap |
| CN-005 | - | ADR-0001 | - | Gap |
| CN-006 | - | ADR-0001 | - | Gap |
| CN-007 | - | ADR-0001 | - | Covered |
| CN-008 | - | ADR-0001 | - | Gap |
| CN-009 | - | ADR-0001 | - | Gap |
| CN-010 | - | ADR-0001 | - | Gap |

## Open Inconsistencies

| # | Views | Inconsistency | Found in (RC-ID) | Status | Resolved in |
| --- | --- | --- | --- | --- | --- |
| 1 | - | none | - | Closed | - |

---

[BC-001]: ../business-case.md
[bfd7827]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/commit/bfd782710394ff04fce3f51f464e5e342cbeb4ca
