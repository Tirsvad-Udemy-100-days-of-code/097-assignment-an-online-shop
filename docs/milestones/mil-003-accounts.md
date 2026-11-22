# Milestone 3: Registration and login

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-003 |
| CrossReference | [BC-001] |
| Language | en |
| Domain | it |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Deprecated | Jens Tirsvad Nielsen | S01 | Accepted after review RC-007; stand-in review, not independent | [bfd7827] |
| 2026-11-22 | Accepted | Jens Tirsvad Nielsen | S01 | Task 3 uses Flask's signed session per ADR-0002; accepted after review RC-018, stand-in review, not independent | [4d90862] |

---

## Purpose

Decide whether visitors can register and sign in safely, as the assignment requires.

## Deliverable

Registration, login and logout with scrypt password hashes, signed session cookies, CSRF protection on forms, an admin role, tests and the step 3 screenshot.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | A visitor can register with an email and a password; duplicate emails are refused | Met | Not met: fix and review again |
| 2 | Passwords are stored only as salted scrypt hashes | Met | Not met: fix and review again |
| 3 | Login sets a signed, HttpOnly session cookie and logout clears it | Met | Not met: fix and review again |
| 4 | Every state-changing form carries a CSRF token and a wrong token is refused | Met | Not met: fix and review again |
| 5 | An admin account exists from configuration and a customer cannot reach admin pages | Met | Not met: fix and review again |
| 6 | `docs/screenshots/step-03.png` exists and is shown in the README and the wiki | Met | Not met: fix and review again |

## Dependencies

| Depends on | Reason |
| --- | --- |
| MIL-002 | Router, storage and pages |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| Objective 2 | [BC-001] |
| CN-001 | [SA-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S01 |
| Approving reviewer | S01 |

## Target Date

2026-11-30 — inside the plan window.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Model users and password hashing | Add the User entity, email and password rules, and a scrypt hasher from hashlib behind a port, with unit tests. | No |  |
| 2 | Implement the user repository | Add the SQLite user repository and the register and authenticate use cases, with integration tests. | No |  |
| 3 | Add signed sessions and CSRF tokens | Add Flask's signed session cookie with expiry and per-session CSRF tokens using hmac and secrets, with tests for tampering. | No |  |
| 4 | Build the registration and login pages | Add the register, login and logout controllers and pages with error messages and a navigation bar showing the user. | No |  |
| 5 | Add the admin role | Add the role field, an admin created from environment configuration, and a guard for admin-only routes, with tests. | No |  |
| 6 | Capture step screenshot for step 3 | Capture docs/screenshots/step-03.png of the login and registration pages and add it to the README. | No |  |
| 7 | Write wiki pages for step 3 | Write the three-language wiki pages about password hashing, sessions and CSRF. | No |  |

---


[BC-001]: ../business-case.md
[bfd7827]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/commit/bfd782710394ff04fce3f51f464e5e342cbeb4ca
[4d90862]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/commit/4d908627163f1be713505164ac4973b394740c4f
