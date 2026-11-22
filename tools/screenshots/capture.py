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

from online_shop import constants
from online_shop.application.payment_gateway import (
    CheckoutRequest,
    CheckoutSession,
    SessionResult,
)
from online_shop.domain.order import OrderStatus
from online_shop.infrastructure.settings import Settings
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
## Id prefix of the sessions of the in-process gateway; the first one is paid in step 5.
FAKE_SESSION_PREFIX = "cs_test_fake_"


def _fill_basket(page: Page, base_url: str, product_ids: tuple[int, ...]) -> None:
    """@brief Put each product in the basket through the add form of its page."""
    for product_id in product_ids:
        page.goto(f"{base_url}/products/{product_id}")
        with page.expect_navigation():
            page.click("form.add-form button[type=submit]")


def step_04(page: Page, base_url: str) -> None:
    """@brief Register through the real form, fill the basket, open the basket page."""
    page.goto(base_url + "/register")
    page.fill("#email", SHOT_EMAIL)
    page.fill("#password", SHOT_PASSWORD)
    with page.expect_navigation():
        page.click("section.auth-panel button[type=submit]")
    _fill_basket(page, base_url, SHOT_BASKET_PRODUCTS)
    page.goto(base_url + "/basket")
    page.wait_for_selector("ul.basket-lines li.basket-line")


class InProcessPaymentGateway:
    """@brief A payment gateway that never leaves the process: no Stripe, no keys.

    Every session is paid at once and its address is the shop's own success page,
    so "paying" is only the redirect that Stripe would do after the card step.
    """

    def __init__(self) -> None:
        """@brief Start without sessions."""
        self._sessions: dict[str, SessionResult] = {}

    def create_checkout_session(self, request: CheckoutRequest) -> CheckoutSession:
        """@brief Open a session that is already paid."""
        session_id = f"{FAKE_SESSION_PREFIX}{len(self._sessions) + 1}"
        total = sum(
            item.unit_amount_cents * item.quantity for item in request.line_items
        )
        self._sessions[session_id] = SessionResult(
            session_id, True, total, request.currency, request.client_reference_id
        )
        url = request.success_url.replace(
            constants.CHECKOUT_SESSION_PLACEHOLDER, session_id
        )
        return CheckoutSession(session_id, url)

    def retrieve_session(self, session_id: str) -> SessionResult:
        """@brief Return the session made earlier."""
        return self._sessions[session_id]


def step_05(page: Page, base_url: str) -> None:
    """@brief Pay one basket through the fake gateway, then fill the basket again.

    The first order is the one the phone frame shows; the desktop view ends on
    the basket page with its Checkout button.
    """
    page.goto(base_url + "/register")
    page.fill("#email", SHOT_EMAIL)
    page.fill("#password", SHOT_PASSWORD)
    with page.expect_navigation():
        page.click("section.auth-panel button[type=submit]")
    _fill_basket(page, base_url, SHOT_BASKET_PRODUCTS)
    page.goto(base_url + "/basket")
    with page.expect_navigation():
        page.click("form.checkout-form button[type=submit]")
    page.wait_for_selector("dl.order-summary")
    _fill_basket(page, base_url, SHOT_BASKET_PRODUCTS[:2])
    page.goto(base_url + "/basket")
    page.wait_for_selector("form.checkout-form button[type=submit]")


SHOT_ADMIN_EMAIL = "owner@example.com"
SHOT_ADMIN_PASSWORD = "owner password for the shots"
## Customers and what each buys in step 6: product ids per order, in buying order.
SHOT_ORDERS = (
    ("ann@example.com", (1, 2)),
    ("bob@example.com", (3,)),
    ("ann@example.com", (4, 1)),
    ("cleo@example.com", (5, 6)),
    ("bob@example.com", (2,)),
)
## Where the board owner moves the orders: order number and target column.
SHOT_MOVES = (
    (1, OrderStatus.CONFIRMED),
    (2, OrderStatus.BEING_PACKED),
    (3, OrderStatus.SHIPPED),
    (4, OrderStatus.DELIVERED),
    (5, OrderStatus.CONFIRMED),
)
BOARD_CARD = ".board-card"


def _sign_in(page: Page, base_url: str, path: str, email: str, password: str) -> None:
    """@brief Fill and send the register or the login form."""
    page.goto(base_url + path)
    page.fill("#email", email)
    page.fill("#password", password)
    with page.expect_navigation():
        page.click("section.auth-panel button[type=submit]")


def _buy(
    browser: Browser,
    base_url: str,
    email: str,
    products: tuple[int, ...],
    first_time: bool,
) -> None:
    """@brief One customer pays for one basket; registers first, else signs in."""
    context = browser.new_context(viewport=VIEWPORT)
    page = context.new_page()
    _sign_in(
        page, base_url, "/register" if first_time else "/login", email, SHOT_PASSWORD
    )
    _fill_basket(page, base_url, products)
    page.goto(base_url + "/basket")
    with page.expect_navigation():
        page.click("form.checkout-form button[type=submit]")
    page.wait_for_selector("dl.order-summary")
    context.close()


def step_06(page: Page, base_url: str) -> None:
    """@brief Five paid orders from three customers; the owner sorts them on the board.

    The moves go through the select on each card, the keyboard path of the
    board, and are checked again after a reload.
    """
    browser = page.context.browser
    assert browser is not None
    customers: set[str] = set()
    for email, products in SHOT_ORDERS:
        _buy(browser, base_url, email, products, email not in customers)
        customers.add(email)
    _sign_in(page, base_url, "/login", SHOT_ADMIN_EMAIL, SHOT_ADMIN_PASSWORD)
    page.goto(base_url + "/admin/board")
    page.wait_for_selector(BOARD_CARD)
    for number, status in SHOT_MOVES:
        card = f'{BOARD_CARD}[data-order-id="{number}"]'
        page.select_option(f"{card} select", status.value)
        page.wait_for_selector(f'section[data-status="{status.value}"] {card}')
    page.reload()
    page.wait_for_selector(BOARD_CARD)


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
    "step-05": step_05,
    "step-06": step_06,
}

## Steps that compose a desktop shot with a phone frame, and what the frame shows.
PHONE_PAGES: dict[str, tuple[str, str]] = {
    "step-02": ("/", "ul.product-grid li.product-card"),
    "step-03": ("/register", "section.auth-panel form"),
    "step-04": ("/basket", "ul.basket-lines li.basket-line"),
    "step-05": (
        f"/checkout/success?{constants.CHECKOUT_SESSION_QUERY}={FAKE_SESSION_PREFIX}1",
        "dl.order-summary",
    ),
    "step-06": ("/admin/board", BOARD_CARD),
}

## Steps that pay through the in-process gateway.
PAYMENT_STEPS = frozenset({"step-05", "step-06"})


def main(step: str) -> int:
    """@brief Run one scenario and save its screenshot.

    @param step The scenario name, for example step-01.
    @return The exit code.
    """
    database = Path(tempfile.mkdtemp()) / "shots.sqlite3"
    payments = InProcessPaymentGateway() if step in PAYMENT_STEPS else None
    settings = (
        Settings(admin_email=SHOT_ADMIN_EMAIL, admin_password=SHOT_ADMIN_PASSWORD)
        if step == "step-06"
        else None
    )
    app = create_app(database, settings, payments=payments)
    server = make_server("127.0.0.1", 0, app, threaded=True)
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
