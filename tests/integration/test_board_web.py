"""Tests of the board page, the board API and the order history on the real app."""

import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from online_shop import constants
from online_shop.domain.money import Money
from online_shop.domain.order import OrderLine, OrderStatus
from online_shop.domain.user import UserRole
from online_shop.infrastructure.settings import Settings
from online_shop.infrastructure.sqlite_order_repository import SqliteOrderRepository
from online_shop.infrastructure.sqlite_user_repository import SqliteUserRepository
from online_shop.presentation.app import create_app

PASSWORD = "correct horse"
ADMIN_EMAIL = "root@example.com"
ADMIN_PASSWORD = "admin password"
NOW = datetime(2026, 5, 6, 7, 8, tzinfo=UTC)
SEE_OTHER = 303
STATUSES = [
    "Needs confirmation",
    "Confirmed",
    "Being packed",
    "Shipped",
    "Delivered",
]


class Shop:
    """The app on a SQLite file with two customers who each have orders."""

    def __init__(self, tmp_path: Path) -> None:
        self.path = tmp_path / "shop.sqlite3"
        settings = Settings("test-key", ADMIN_EMAIL, ADMIN_PASSWORD)
        self.app = create_app(self.path, settings)
        users = SqliteUserRepository(self.path)
        self.ann = users.add("ann@example.com", "x", UserRole.CUSTOMER).id
        self.bob = users.add("bob@example.com", "x", UserRole.CUSTOMER).id
        self.orders = SqliteOrderRepository(self.path)
        self.add_order(self.ann, 1)
        self.add_order(self.bob, 2)
        self.add_order(self.ann, 3)

    def add_order(self, user_id: int, number: int) -> int:
        lines = (OrderLine("Mug", Money(1200), 2), OrderLine("Lamp", Money(3490), 1))
        return self.orders.add(
            user_id,
            f"cs_{number}",
            Money(5890),
            "eur",
            NOW + timedelta(minutes=number),
            lines,
        ).id

    def client(self) -> FlaskClient:
        return self.app.test_client()


def token_of(client: FlaskClient, path: str = "/login") -> str:
    html = client.get(path).get_data(as_text=True)
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match
    return match.group(1)


def sign_in(client: FlaskClient, email: str, password: str) -> None:
    data = {constants.CSRF_FORM_FIELD: token_of(client), "email": email}
    client.post("/login", data={**data, "password": password})


def sign_in_customer(shop: Shop) -> FlaskClient:
    # The seeded customers have no usable hash, so register a real one.
    client = shop.client()
    data = {constants.CSRF_FORM_FIELD: token_of(client, "/register")}
    fields = {**data, "email": "zoe@example.com", "password": PASSWORD}
    client.post("/register", data=fields)
    return client


def admin_client(shop: Shop) -> FlaskClient:
    client = shop.client()
    sign_in(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    return client


def move(
    client: FlaskClient, payload: object, token: str | None = None
) -> TestResponse:
    headers = {constants.CSRF_HEADER: token or token_of(client, "/admin/board")}
    return client.post("/api/board/move", json=payload, headers=headers)


def column_ids(client: FlaskClient, status: str) -> list[int]:
    columns = client.get("/api/board").get_json()["columns"]
    column = next(c for c in columns if c["status"] == status)
    return [card["order_id"] for card in column["cards"]]


@pytest.fixture
def shop(tmp_path: Path) -> Shop:
    return Shop(tmp_path)


def test_board_page_is_for_admins_only(shop: Shop) -> None:
    anonymous = shop.client().get("/admin/board")
    assert anonymous.status_code == SEE_OTHER
    assert anonymous.headers["Location"] == "/login"
    assert sign_in_customer(shop).get("/admin/board").status_code == 403
    page = admin_client(shop).get("/admin/board")
    html = page.get_data(as_text=True)
    assert page.status_code == 200
    assert 'name="csrf-token"' in html
    assert 'src="/static/board.js"' in html
    assert 'id="board"' in html
    assert " onclick=" not in html


def test_board_api_answers_each_role(shop: Shop) -> None:
    path = "/api/board"
    anonymous = shop.client().get(path)
    assert anonymous.status_code == 401
    assert anonymous.get_json() == {"error": constants.ERROR_UNAUTHORIZED}
    customer = sign_in_customer(shop).get(path)
    assert customer.status_code == 403
    assert customer.get_json() == {"error": constants.ERROR_FORBIDDEN}
    assert admin_client(shop).get(path).status_code == 200


def test_board_lists_five_columns_with_cards(shop: Shop) -> None:
    data = admin_client(shop).get("/api/board").get_json()
    assert [c["status"] for c in data["columns"]] == STATUSES
    first = data["columns"][0]
    assert first["count"] == 3
    card = first["cards"][0]
    assert card["order_id"] == 1
    assert card["customer_email"] == "ann@example.com"
    assert card["items"] == ["2 x Mug", "1 x Lamp"]
    assert card["total_cents"] == 5890
    assert card["total"] == "€58.90"
    assert card["created"] == "2026-05-06 07:09"
    assert data["columns"][1]["cards"] == []


def test_move_requires_an_admin(shop: Shop) -> None:
    anonymous = shop.client()
    body = {"order_id": 1, "status": "Confirmed", "index": 0}
    token = token_of(anonymous)
    assert move(anonymous, body, token).status_code == 401
    assert move(sign_in_customer(shop), body).status_code == 403
    assert column_ids(admin_client(shop), "Confirmed") == []


def test_move_without_a_csrf_token_is_refused(shop: Shop) -> None:
    client = admin_client(shop)
    body = {"order_id": 1, "status": "Confirmed", "index": 0}
    assert client.post("/api/board/move", json=body).status_code == 403
    wrong = move(client, body, "not-the-token")
    assert wrong.status_code == 403
    assert column_ids(client, "Confirmed") == []


def test_move_persists_and_survives_a_new_session(shop: Shop) -> None:
    client = admin_client(shop)
    response = move(client, {"order_id": 2, "status": "Confirmed", "index": 0})
    assert response.status_code == 200
    assert [c["count"] for c in response.get_json()["columns"]] == [2, 1, 0, 0, 0]
    again = admin_client(shop)
    assert column_ids(again, "Confirmed") == [2]
    assert column_ids(again, "Needs confirmation") == [1, 3]


def test_move_renumbers_positions_in_both_columns(shop: Shop) -> None:
    client = admin_client(shop)
    move(client, {"order_id": 1, "status": "Shipped", "index": 0})
    move(client, {"order_id": 3, "status": "Shipped", "index": 0})
    assert column_ids(client, "Shipped") == [3, 1]
    assert column_ids(client, "Needs confirmation") == [2]
    positions = {o.id: o.position for o in shop.orders.list_board()}
    assert positions == {3: 0, 1: 1, 2: 0}


def test_move_within_a_column_reorders_it(shop: Shop) -> None:
    client = admin_client(shop)
    move(client, {"order_id": 1, "status": "Needs confirmation", "index": 2})
    assert column_ids(client, "Needs confirmation") == [2, 3, 1]


@pytest.mark.parametrize(
    "payload",
    [
        {"order_id": 1, "status": "Lost", "index": 0},
        {"order_id": 1, "status": "Confirmed", "index": -1},
        {"order_id": 1, "status": "Confirmed"},
        {"order_id": "1", "status": "Confirmed", "index": 0},
        {"order_id": True, "status": "Confirmed", "index": 0},
        {"order_id": 1, "status": 5, "index": 0},
        {"order_id": 1, "status": "Confirmed", "index": 1.5},
        [1, 2],
        "text",
    ],
)
def test_move_with_invalid_input_is_a_400_json_error(
    shop: Shop, payload: object
) -> None:
    client = admin_client(shop)
    response = move(client, payload)
    assert response.status_code == 400
    assert "error" in response.get_json()
    assert column_ids(client, "Confirmed") == []


def test_move_with_a_body_that_is_not_json_is_a_400(shop: Shop) -> None:
    client = admin_client(shop)
    headers = {constants.CSRF_HEADER: token_of(client, "/admin/board")}
    response = client.post("/api/board/move", data="nope", headers=headers)
    assert response.status_code == 400
    assert response.get_json() == {"error": constants.ERROR_MOVE_BODY}


def test_move_of_an_unknown_order_is_a_404_json_error(shop: Shop) -> None:
    response = move(
        admin_client(shop), {"order_id": 99, "status": "Confirmed", "index": 0}
    )
    assert response.status_code == 404
    assert response.get_json() == {"error": constants.ERROR_ORDER_NOT_FOUND}


def test_admin_page_links_to_the_board(shop: Shop) -> None:
    html = admin_client(shop).get("/admin").get_data(as_text=True)
    assert 'href="/admin/board"' in html


def test_order_history_for_anonymous_goes_to_login(shop: Shop) -> None:
    response = shop.client().get("/orders")
    assert response.status_code == SEE_OTHER
    assert response.headers["Location"].startswith("/login")


def test_order_history_lists_only_own_orders_newest_first(shop: Shop) -> None:
    client = sign_in_customer(shop)
    html = client.get("/orders").get_data(as_text=True)
    assert constants.TEXT_ORDERS_EMPTY in html
    assert 'class="order-number"' not in html
    zoe = SqliteUserRepository(shop.path).get_by_email("zoe@example.com")
    assert zoe is not None
    shop.add_order(zoe.id, 10)
    shop.add_order(zoe.id, 11)
    shop.orders.move(shop.orders.list_for_user(zoe.id)[0].id, OrderStatus.SHIPPED, 0)
    html = client.get("/orders").get_data(as_text=True)
    numbers = re.findall(r'class="order-number">(\d+)<', html)
    assert numbers == ["5", "4"]
    assert "status-shipped" in html
    assert "status-needs-confirmation" in html
    assert "Shipped" in html
    assert "2026-05-06" in html
    assert "2 &times; Mug" in html
    assert "ann@example.com" not in html
    assert 'href="/orders"' in html


def test_header_shows_the_orders_link_to_signed_in_users_only(shop: Shop) -> None:
    assert 'href="/orders"' not in shop.client().get("/").get_data(as_text=True)
    assert 'href="/orders"' in sign_in_customer(shop).get("/").get_data(as_text=True)
