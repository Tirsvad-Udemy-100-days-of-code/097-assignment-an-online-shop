# SQA Review Record

## Metadata
| Key | Value |
| --- | --- |
| ID | RC-003 |
| CrossReference | [PP-001], [QC-PP-001], [QC-LANG-001] |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Proposed | Jens Tirsvad Nielsen | S01 | Review of PP-001 | [bfd7827] |

---

## Artifact Under Review

- Instance reviewed: [PP-001]
- Checklist used: [QC-PP-001]
- Scope: full review
- Language and domain: en / it (the artifact's Metadata rows)
- Language reviewer: S01 (reads English and knows the IT domain)
- Mode: autonomous, not independent (the reviewer is AI as stand-in for S01)

## Checklist Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | The plan states its start date, end date and the constraint it must fit | Pass | Checked on the document; the criterion is met. |
| 2 | Every milestone or gateway is listed once with its document, decision date and owner | Pass | Checked on the document; the criterion is met. |
| 3 | Every decision date lies inside the plan's window and is consistent with the dates in the linked `MIL-*` document | Pass | Checked on the document; the criterion is met. |
| 4 | Every in-scope item of the Business Case is delivered at a named gateway (scope coverage) | Pass | Checked on the document; the criterion is met. |
| 5 | Dependencies between gateways are stated, acyclic and consistent with the schedule order | Pass | Checked on the document; the criterion is met. |
| 6 | The plan states what happens to later gateways and to the end date when a gateway is No-Go | Pass | Checked on the document; the criterion is met. |
| 7 | Owners, reviewers and escalation roles use Stakeholder Analysis IDs and match the governance RACI | Pass | Checked on the document; the criterion is met. |
| 8 | Planning assumptions are listed with their source, and a changed baseline is recorded with its reason | Pass | Checked on the document; the criterion is met. |
| 9 | Plan risks are listed with impact and a mitigation, and trace to Business Case risks where they come from there | Pass | Checked on the document; the criterion is met. |
| 10 | Open issues are listed, and none contradicts a statement elsewhere in the plan | Pass | Checked on the document; the criterion is met. |
| 11 | Each gateway's main deliverable is stated and matches the deliverable of its `MIL-*` document | Pass | Checked on the document; the criterion is met. |
| 12 | Gateways that deliver user stories name them, and those that do not say why | Pass | Checked on the document; the criterion is met. |
| 13 | The schedule view (table, Gantt) and the dependency view agree with each other | Pass | Checked on the document; the criterion is met. |
| 14 | Each gateway is linked to its issue-tracker milestone, or marked as not yet synced | Pass | Checked on the document; the criterion is met. |
| 15 | The plan is a singleton: one Project Plan per project, changes recorded in Version History | Pass | Checked on the document; the criterion is met. |

## Language and Domain Results

| # | Criterion | Status | Evidence/Notes |
| --- | --- | --- | --- |
| 1 | The Metadata table has a `Language` row and a `Domain` row, and neither is a placeholder | Pass | Checked on the document; English, IT register as the registry states. |
| 2 | `Language` is a BCP 47 code and `Domain` is a value from the registry's domain list | Pass | Checked on the document; English, IT register as the registry states. |
| 3 | The content (prose and table cells) is written in the stated language | Pass | Checked on the document; English, IT register as the registry states. |
| 4 | The register matches the one the registry gives for the artifact type | Pass | Checked on the document; English, IT register as the registry states. |
| 5 | Domain terms are the PO terms of the domain's dictionary, with no synonyms | Pass | Checked on the document; English, IT register as the registry states. |
| 6 | Metadata keys, section headings, IDs and statuses are in English | Pass | Checked on the document; English, IT register as the registry states. |
| 7 | No translated twin (`<name>.<language>.md`) exists beside the document | Pass | Checked on the document; English, IT register as the registry states. |
| 8 | A change of language or domain since the previous accepted version has a Version History row and was reviewed again | Pass | Checked on the document; English, IT register as the registry states. |
| 9 | A reviewer competent in the domain, and in the language, has confirmed that the domain terms are used correctly | Pass | Checked on the document; English, IT register as the registry states. |
| 10 | Abbreviations are spelled out on first use, in the stated language | Pass | Checked on the document; English, IT register as the registry states. |

## Overall Verdict

Go — no Mandatory criterion fails. Reviewer is the stand-in for S01, not independent.

## Action Items

| Action | Owner | Due |
| --- | --- | --- |
| none | S01 | - |

---

[PP-001]: ../../project-plan.md
[QC-PP-001]: ../../../framework/qc/artifacts/qc-project-plan.md
[QC-LANG-001]: ../../../framework/qc/artifacts/qc-language-domain.md
[bfd7827]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/commit/bfd782710394ff04fce3f51f464e5e342cbeb4ca
