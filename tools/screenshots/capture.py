"""@brief Start the shop and save a screenshot of one build step.

Runs inside the container of tools/screenshots/Dockerfile, never on the host
desktop. The repository is mounted at /work; the PNG is written to
docs/screenshots/.

Usage: capture.py <step>   (for example: capture.py step-01)
"""

import sys
import tempfile
import threading
from collections.abc import Callable
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

from online_shop.main import build_router_for
from online_shop.presentation.http_server import create_server

OUTPUT_DIR = Path("/work/docs/screenshots")
VIEWPORT = {"width": 1280, "height": 720}


def step_01(page: Page, base_url: str) -> None:
    """@brief Open the first page: the welcome text."""
    page.goto(base_url + "/")
    page.wait_for_selector("section.hero")


SCENARIOS: dict[str, Callable[[Page, str], None]] = {
    "step-01": step_01,
}


def main(step: str) -> int:
    """@brief Run one scenario and save its screenshot.

    @param step The scenario name, for example step-01.
    @return The exit code.
    """
    database = Path(tempfile.mkdtemp()) / "shots.sqlite3"
    server = create_server("127.0.0.1", 0, build_router_for(database))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    host, port = server.server_address[:2]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT)
        SCENARIOS[step](page, f"http://{host!s}:{port}")
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(OUTPUT_DIR / f"{step}.png"))
        browser.close()
    server.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
