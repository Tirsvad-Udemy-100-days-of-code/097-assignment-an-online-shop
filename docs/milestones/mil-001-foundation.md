# Milestone 1: Project foundation

## Metadata
| Key | Value |
| --- | --- |
| ID | MIL-001 |
| CrossReference | [BC-001] |
| Language | en |
| Domain | it |

## Version History
| Date | Status | Author | Reviewer | Change | Commit |
| --- | --- | --- | --- | --- | --- |
| 2026-11-22 | Deprecated | Jens Tirsvad Nielsen | S01 | Initial version | [bfd7827] |
| 2026-11-22 | Accepted | Jens Tirsvad Nielsen | S01 | Accepted after review RC-005; stand-in review, not independent | [bfd7827] |

---

## Purpose

Decide whether the project has the tooling, structure and documentation every later step builds on.

## Deliverable

Python project skeleton with pyproject.toml, local .venv instructions, pytest, constants.py, Doxyfile, Python .gitignore, editorconfig, opengrep scan script, README from the framework template, a first page served by the standard library, the step 1 screenshot and the repository description and topics.

## Go / No-Go Criteria

| # | Criterion (objectively checkable) | Go | No-Go |
| --- | --- | --- | --- |
| 1 | `pyproject.toml` sets Python 3.14 or newer, no runtime dependencies, and `pytest` runs green in a fresh `.venv` | Met | Not met: fix and review again |
| 2 | The README explains creating and using `.venv`, `python -m pip install --upgrade pip`, running the shop and running the tests | Met | Not met: fix and review again |
| 3 | `Doxyfile` exists and `src/` uses doxygen comments; constants live in `src/online_shop/constants.py` | Met | Not met: fix and review again |
| 4 | `scripts/run_opengrep.py` runs opengrep with 0 findings of severity error | Met | Not met: fix and review again |
| 5 | `docs/screenshots/step-01.png` exists and is shown in the README and the wiki | Met | Not met: fix and review again |
| 6 | The repository has a description and at least 5 topics on the git host | Met | Not met: fix and review again |

## Dependencies

| Depends on | Reason |
| --- | --- |
| None | First milestone |

## Traceability

| Business Case objective / KPI / user story | Reference |
| --- | --- |
| Objectives 3, 4, 5 and 6 | [BC-001] |
| CN-005, CN-006, CN-007 | [SA-001] |

## Ownership

| Role | Stakeholder ID (SA) |
| --- | --- |
| Owner | S01 |
| Approving reviewer | S01 |

## Target Date

2026-11-24 — inside the plan window.

## Tasks

| # | Task | Summary | Needs its own Use Case/User Story? | Reference |
| --- | --- | --- | --- | --- |
| 1 | Create the project skeleton | Add pyproject.toml (Python 3.14 or newer, empty runtime dependencies, dev group with pytest, ruff, mypy), the src/online_shop package, tests/ folders, constants.py, .gitignore, .editorconfig and the Doxyfile. | No |  |
| 2 | Write the README from the template | Use the framework README template; document creating and using a local .venv, upgrading pip, running the shop and the tests, with the screenshot gallery and a reflection placeholder. | No |  |
| 3 | Add the opengrep scan script | Add .opengrep/rules.yml and scripts/run_opengrep.py that call the local opengrep binary before every push and fail on severity error. | No |  |
| 4 | Serve a first page | Add the main module and a standard-library HTTP server that serves a home page, with a unit test and an integration test. | No |  |
| 5 | Build the screenshot harness | Build a Docker image with a headless browser and a script that starts the shop and captures docs/screenshots/step-NN.png, so the host desktop is never used. | No |  |
| 6 | Capture step screenshot for step 1 | Capture docs/screenshots/step-01.png of the first page and add it to the README. | No |  |
| 7 | Set repository description and topics | Set the description and topics on the git host through its API with the repository token from .env, which is read by the shell only and never printed or committed. | No |  |
| 8 | Write wiki pages for step 1 | Write the three-language wiki pages (en, da, ms) about the project setup, venv, constants and what was learned. | No |  |

---


[BC-001]: ../business-case.md
[bfd7827]: https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-online-shop/commit/bfd782710394ff04fce3f51f464e5e342cbeb4ca
