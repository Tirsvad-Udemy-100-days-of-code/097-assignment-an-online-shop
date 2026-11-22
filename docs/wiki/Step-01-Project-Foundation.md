**English** · [Dansk](Step-01-Project-Foundation-da) · [Bahasa Malaysia](Step-01-Project-Foundation-ms)

# Step 1: Project foundation

The first step builds nothing the shopper can use yet. It sets up the tooling and the structure that every later step stands on, and serves one page.

![Step 1](https://git.tirsystem.com/Tirsvad-Udemy-100-days-of-code/097-assignment-an-nnline-shop/raw/branch/main/docs/screenshots/step-01.png)

## Setup

- **Python 3.14 or newer and no runtime dependencies.** `pyproject.toml` lists only a `dev` group: pytest, pytest-cov, ruff and mypy.
- **A local virtual environment.** `python -m venv .venv`, activate it, then `python -m pip install --upgrade pip` and `python -m pip install -e ".[dev]"`. The environment keeps the project's packages apart from the system Python.
- **Run the shop** with `python -m online_shop` and open http://127.0.0.1:8000/.

## Structure

The code in `src/online_shop/` has four layers: `domain`, `application`, `infrastructure` and `presentation`. Dependencies point inward, so the business rules never import the web server. The presentation layer follows MVC: a controller answers a request and a view builds the HTML.

## Constants

Every literal that more than one place needs lives once in `src/online_shop/constants.py`: the app title, host, port, content types, status codes and error messages. Changing the port means editing one line.

## Checks

- `pytest` runs unit and integration tests and fails below 90 percent coverage.
- `python scripts/run_opengrep.py` scans the code and must find nothing of severity error before a push.
- The screenshot is taken by a headless browser in a Docker container, never on the desktop.

## What I learned

- The standard library is enough to serve a page: `http.server` plus a small router.
- Putting constants in one module and layers in separate folders from day one costs little and saves rework later.
- A test that starts the real server on a free port catches mistakes that unit tests miss.
