"""@brief Start the shop and save a screenshot of one build step.

Runs inside the container of tools/screenshots/Dockerfile, never on the host
desktop. The repository is mounted at /work; the PNG is written to
docs/screenshots/.

Usage: capture.py <step>   (for example: capture.py step-01)
"""

import base64
import sys
import tempfile
import threading
from collections.abc import Callable
from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from werkzeug.serving import make_server

from online_shop.presentation.app import create_app

OUTPUT_DIR = Path("/work/docs/screenshots")
VIEWPORT = {"width": 1280, "height": 720}
PHONE_VIEWPORT = {"width": 375, "height": 812}
BOARD_VIEWPORT = {"width": 1600, "height": 900}
BOARD = """<!doctype html><html><body style="margin:0;width:1600px;height:900px;
background:radial-gradient(circle at 30% 20%,#3a3a3a,#0c0c0c);position:relative;
overflow:hidden;font-family:sans-serif">
<img src="data:image/png;base64,$DESKTOP" style="position:absolute;left:50px;top:90px;
width:1100px;border:6px solid #111;box-shadow:0 20px 60px #000">
<img src="data:image/png;base64,$PHONE" style="position:absolute;left:1090px;top:130px;
width:330px;border:14px solid #f4f4f4;border-radius:44px;box-shadow:0 20px 60px #000">
</body></html>"""


def step_01(page: Page, base_url: str) -> None:
    """@brief Open the first page: the welcome text."""
    page.goto(base_url + "/")
    page.wait_for_selector("section.hero")


def step_02(page: Page, base_url: str) -> None:
    """@brief Open the home page with the product grid."""
    page.goto(base_url + "/")
    page.wait_for_selector("ul.product-grid li.product-card")


def step_03(page: Page, base_url: str) -> None:
    """@brief Open the login page; the phone frame shows the register page."""
    page.goto(base_url + "/login")
    page.wait_for_selector("section.auth-panel form")


SHOT_EMAIL = "shopper@example.com"
SHOT_PASSWORD = "correct horse battery"
## Product ids (seed order) put in the basket for step 4; the first goes in twice.
SHOT_BASKET_PRODUCTS = (1, 2, 1, 4)


def step_04(page: Page, base_url: str) -> None:
    """@brief Register through the real form, fill the basket, open the basket page."""
    page.goto(base_url + "/register")
    page.fill("#email", SHOT_EMAIL)
    page.fill("#password", SHOT_PASSWORD)
    with page.expect_navigation():
        page.click("section.auth-panel button[type=submit]")
    for product_id in SHOT_BASKET_PRODUCTS:
        page.goto(f"{base_url}/products/{product_id}")
        with page.expect_navigation():
            page.click("form.add-form button[type=submit]")
    page.goto(base_url + "/basket")
    page.wait_for_selector("ul.basket-lines li.basket-line")


def _png_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def compose_desktop_and_phone(
    browser: Browser,
    base_url: str,
    desktop: bytes,
    phone_path: str = "/",
    phone_selector: str = "ul.product-grid li.product-card",
    context: BrowserContext | None = None,
) -> bytes:
    """@brief Place the desktop shot and a phone-sized shot side by side.

    @param browser The running browser.
    @param base_url The address of the shop.
    @param desktop PNG bytes of the desktop view.
    @param phone_path The page the phone frame shows.
    @param phone_selector A selector that is present once that page is ready.
    @param context The browser context to open the phone page in, so it shares
        the cookies (the sign-in) of the desktop page; a fresh one when omitted.
    @return PNG bytes of the composed image.
    """
    if context is None:
        phone_page = browser.new_page(viewport=PHONE_VIEWPORT)
    else:
        phone_page = context.new_page()
        phone_page.set_viewport_size(PHONE_VIEWPORT)
    phone_page.goto(base_url + phone_path)
    phone_page.wait_for_selector(phone_selector)
    phone = phone_page.screenshot()
    phone_page.close()
    board = browser.new_page(viewport=BOARD_VIEWPORT)
    board.set_content(
        BOARD.replace("$DESKTOP", _png_base64(desktop)).replace(
            "$PHONE", _png_base64(phone)
        )
    )
    image = board.screenshot()
    board.close()
    return image


SCENARIOS: dict[str, Callable[[Page, str], None]] = {
    "step-01": step_01,
    "step-02": step_02,
    "step-03": step_03,
    "step-04": step_04,
}

## Steps that compose a desktop shot with a phone frame, and what the frame shows.
PHONE_PAGES: dict[str, tuple[str, str]] = {
    "step-02": ("/", "ul.product-grid li.product-card"),
    "step-03": ("/register", "section.auth-panel form"),
    "step-04": ("/basket", "ul.basket-lines li.basket-line"),
}


def main(step: str) -> int:
    """@brief Run one scenario and save its screenshot.

    @param step The scenario name, for example step-01.
    @return The exit code.
    """
    database = Path(tempfile.mkdtemp()) / "shots.sqlite3"
    server = make_server("127.0.0.1", 0, create_app(database), threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    host, port = server.server_address[:2]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(viewport=VIEWPORT)
        page = context.new_page()
        base = f"http://{host!s}:{port}"
        SCENARIOS[step](page, base)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        shot = page.screenshot()
        if step in PHONE_PAGES:
            shot = compose_desktop_and_phone(
                browser, base, shot, *PHONE_PAGES[step], context=context
            )
        (OUTPUT_DIR / f"{step}.png").write_bytes(shot)
        browser.close()
    server.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
