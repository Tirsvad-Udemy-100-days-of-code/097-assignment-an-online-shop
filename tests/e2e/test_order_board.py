"""Browser tests of the order board: real drag and drop in headless Chromium.

They run only in the Docker image of tools/screenshots (see README.md in this
folder) and are skipped when Playwright is not installed.
"""

import threading
from collections.abc import Iterator
from pathlib import Path

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import (  # noqa: E402
    Browser,
    BrowserContext,
    Page,
    expect,
    sync_playwright,
)
from werkzeug.serving import make_server  # noqa: E402

from fakes import FakePaymentGateway  # noqa: E402
from online_shop import constants  # noqa: E402
from online_shop.application.payment_gateway import (  # noqa: E402
    CheckoutRequest,
    CheckoutSession,
)
from online_shop.infrastructure.settings import Settings  # noqa: E402
from online_shop.presentation.app import create_app  # noqa: E402

ADMIN_EMAIL = "owner@example.com"
ADMIN_PASSWORD = "owner password"
CUSTOMER_PASSWORD = "correct horse battery"
SESSION_SECRET = "e2e-session-secret"
DESKTOP = {"width": 1280, "height": 800}
PHONE = {"width": 400, "height": 800}
COLUMN_COUNT = 5
CARD = ".board-card"
EMAIL_ID = "#email"
PASSWORD_ID = "#password"
SUBMIT = "section.auth-panel button[type=submit]"


class InstantPaymentGateway(FakePaymentGateway):
    """In-process gateway: every session is paid at once, no Stripe, no network."""

    def create_checkout_session(self, request: CheckoutRequest) -> CheckoutSession:
        """@brief Open a paid session whose address is the shop's success page."""
        session = super().create_checkout_session(request)
        self.pay(session.id)
        url = request.success_url.replace(
            constants.CHECKOUT_SESSION_PLACEHOLDER, session.id
        )
        return CheckoutSession(session.id, url)


@pytest.fixture(scope="module")
def base_url(tmp_path_factory: pytest.TempPathFactory) -> Iterator[str]:
    database = Path(tmp_path_factory.mktemp("e2e")) / "shop.sqlite3"
    settings = Settings(SESSION_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD)
    app = create_app(database, settings, payments=InstantPaymentGateway())
    server = make_server("127.0.0.1", 0, app, threaded=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    host, port = server.server_address[:2]
    yield f"http://{host!s}:{port}"
    server.shutdown()


@pytest.fixture(scope="module")
def browser() -> Iterator[Browser]:
    with sync_playwright() as playwright:
        chromium = playwright.chromium.launch()
        yield chromium
        chromium.close()


def _submit(page: Page, path: str, email: str, password: str, base_url: str) -> None:
    page.goto(base_url + path)
    page.fill(EMAIL_ID, email)
    page.fill(PASSWORD_ID, password)
    with page.expect_navigation():
        page.click(SUBMIT)


def _register_and_buy(browser: Browser, base_url: str, email: str) -> int:
    """Register through the form, pay for one product, return the order number."""
    context = browser.new_context(viewport=DESKTOP)
    page = context.new_page()
    _submit(page, "/register", email, CUSTOMER_PASSWORD, base_url)
    page.goto(f"{base_url}/products/1")
    with page.expect_navigation():
        page.click("form.add-form button[type=submit]")
    page.goto(base_url + "/basket")
    with page.expect_navigation():
        page.click("form.checkout-form button[type=submit]")
    page.wait_for_selector("dl.order-summary")
    number = int(page.inner_text(".order-number"))
    context.close()
    return number


def _admin_board(browser: Browser, base_url: str, viewport: dict[str, int]) -> Page:
    context: BrowserContext = browser.new_context(viewport=viewport)
    page = context.new_page()
    _submit(page, "/login", ADMIN_EMAIL, ADMIN_PASSWORD, base_url)
    page.goto(base_url + "/admin/board")
    page.wait_for_selector(CARD)
    return page


def _column(status: str) -> str:
    return f'section.board-column[data-status="{status}"]'


def test_dragged_order_stays_in_confirmed_after_a_reload(
    browser: Browser, base_url: str
) -> None:
    number = _register_and_buy(browser, base_url, "drag@example.com")
    page = _admin_board(browser, base_url, DESKTOP)
    mine = f'{CARD}[data-order-id="{number}"]'
    expect(page.locator(f"{_column('Needs confirmation')} {mine}")).to_have_count(1)
    page.locator(mine).drag_to(page.locator(f"{_column('Confirmed')} .board-cards"))
    expect(page.locator(f"{_column('Confirmed')} {mine}")).to_have_count(1)
    expect(page.locator("#board-message")).to_have_text("")
    page.reload()
    page.wait_for_selector(CARD)
    expect(page.locator(f"{_column('Confirmed')} {mine}")).to_have_count(1)
    expect(page.locator(f"{_column('Needs confirmation')} {mine}")).to_have_count(0)


def test_customer_sees_the_new_status_on_the_order_history(
    browser: Browser, base_url: str
) -> None:
    email = "history@example.com"
    number = _register_and_buy(browser, base_url, email)
    admin = _admin_board(browser, base_url, DESKTOP)
    admin.locator(f'{CARD}[data-order-id="{number}"] select').select_option("Shipped")
    expect(
        admin.locator(f'{_column("Shipped")} {CARD}[data-order-id="{number}"]')
    ).to_have_count(1)
    customer = browser.new_page(viewport=DESKTOP)
    _submit(customer, "/login", email, CUSTOMER_PASSWORD, base_url)
    customer.goto(base_url + "/orders")
    expect(customer.locator("li.order-card .status-badge")).to_have_text("Shipped")


def test_customer_cannot_open_the_board(browser: Browser, base_url: str) -> None:
    context = browser.new_context(viewport=DESKTOP)
    page = context.new_page()
    _submit(page, "/register", "plain@example.com", CUSTOMER_PASSWORD, base_url)
    response = page.goto(base_url + "/admin/board")
    assert response is not None
    assert response.status == 403
    context.close()


def test_board_columns_are_reachable_at_phone_width(
    browser: Browser, base_url: str
) -> None:
    _register_and_buy(browser, base_url, "phone@example.com")
    page = _admin_board(browser, base_url, PHONE)
    columns = page.locator("section.board-column")
    expect(columns).to_have_count(COLUMN_COUNT)
    for index in range(COLUMN_COUNT):
        column = columns.nth(index)
        column.scroll_into_view_if_needed()
        box = column.bounding_box()
        assert box is not None
        assert box["x"] >= 0
        assert box["x"] + box["width"] <= PHONE["width"]
    assert page.evaluate("document.documentElement.scrollWidth") <= PHONE["width"]


def test_select_on_a_card_moves_it_without_dragging(
    browser: Browser, base_url: str
) -> None:
    number = _register_and_buy(browser, base_url, "keys@example.com")
    page = _admin_board(browser, base_url, PHONE)
    page.locator(f'{CARD}[data-order-id="{number}"] select').select_option("Delivered")
    expect(
        page.locator(f'{_column("Delivered")} {CARD}[data-order-id="{number}"]')
    ).to_have_count(1)
    page.reload()
    page.wait_for_selector(CARD)
    expect(
        page.locator(f'{_column("Delivered")} {CARD}[data-order-id="{number}"]')
    ).to_have_count(1)


def test_a_refused_move_is_undone_and_explained(
    browser: Browser, base_url: str
) -> None:
    number = _register_and_buy(browser, base_url, "refused@example.com")
    page = _admin_board(browser, base_url, DESKTOP)
    page.route("**/api/board/move", lambda route: route.fulfill(status=500, body="no"))
    page.locator(f'{CARD}[data-order-id="{number}"] select').select_option("Shipped")
    expect(page.locator("#board-message")).not_to_have_text("")
    expect(
        page.locator(
            f'{_column("Needs confirmation")} {CARD}[data-order-id="{number}"]'
        )
    ).to_have_count(1)
    expect(
        page.locator(f'{_column("Shipped")} {CARD}[data-order-id="{number}"]')
    ).to_have_count(0)
