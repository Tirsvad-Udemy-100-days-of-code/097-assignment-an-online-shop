"""Tests of the checkout routes through the real app, SQLite and a fake gateway."""

import os
import re
from dataclasses import replace
from pathlib import Path

import pytest
from werkzeug.test import TestResponse

from fakes import FakePaymentGateway, fake_key
from online_shop import constants
from online_shop.infrastructure.settings import Settings
from online_shop.infrastructure.stripe_settings import StripeConfigurationError
from online_shop.presentation.app import create_app

PASSWORD = "correct horse"
SECRET = fake_key("sk", "test")
SEE_OTHER = 303


class Shop:
    def __init__(self, tmp_path: Path, payments: FakePaymentGateway | None) -> None:
        self.payments = payments
        self.database = tmp_path / "shop.sqlite3"
        self.client = create_app(self.database, payments=payments).test_client()

    def token(self, path: str = "/login") -> str:
        html = self.client.get(path).get_data(as_text=True)
        match = re.search(r'name="csrf_token" value="([^"]+)"', html)
        assert match
        return match.group(1)

    def post(self, path: str, **fields: str) -> TestResponse:
        data = {constants.CSRF_FORM_FIELD: self.token(), **fields}
        return self.client.post(path, data=data)

    def sign_up(self, email: str = "ann@example.com") -> None:
        self.post("/register", email=email, password=PASSWORD)

    def sign_out(self) -> None:
        self.post("/logout")

    def add(self, product_id: int, quantity: int = 1) -> None:
        self.post("/basket/add", product_id=str(product_id), quantity=str(quantity))

    def text(self, path: str) -> str:
        return self.client.get(path).get_data(as_text=True)

    def begin(self) -> str:
        response = self.post("/checkout")
        assert response.status_code == SEE_OTHER
        return response.headers["Location"].rsplit("/", 1)[1]


@pytest.fixture
def payments() -> FakePaymentGateway:
    return FakePaymentGateway()


@pytest.fixture
def shop(tmp_path: Path, payments: FakePaymentGateway) -> Shop:
    shop = Shop(tmp_path, payments)
    shop.sign_up()
    return shop


def test_basket_shows_the_checkout_button_only_with_items(shop: Shop) -> None:
    assert 'action="/checkout"' not in shop.text("/basket")
    shop.add(1)
    html = shop.text("/basket")
    assert 'action="/checkout"' in html
    assert constants.TEXT_CHECKOUT in html
    assert 'name="csrf_token"' in html


def test_checkout_button_is_hidden_when_stripe_is_not_configured(
    tmp_path: Path,
) -> None:
    shop = Shop(tmp_path, None)
    shop.sign_up()
    shop.add(1)
    assert 'action="/checkout"' not in shop.text("/basket")


def test_checkout_is_unavailable_without_a_gateway(tmp_path: Path) -> None:
    shop = Shop(tmp_path, None)
    shop.sign_up()
    shop.add(1)
    response = shop.post("/checkout")
    assert response.status_code == 503
    assert constants.ERROR_CHECKOUT_UNAVAILABLE in response.get_data(as_text=True)
    assert shop.client.get("/checkout/success?session_id=x").status_code == 503


def test_app_starts_without_the_key_file(tmp_path: Path) -> None:
    settings = Settings(stripe_env_file=tmp_path / "missing.env")
    app = create_app(tmp_path / "shop.sqlite3", settings)
    assert app.test_client().get("/").status_code == 200


def test_app_loads_test_keys_from_the_key_file(tmp_path: Path) -> None:
    keys = tmp_path / "keys.env"
    publishable = fake_key("pk", "test")
    keys.write_text(
        f"PUBLISHABLE_KEY={publishable}\nSECRET_KEY={SECRET}\n", encoding="utf-8"
    )
    app = create_app(tmp_path / "shop.sqlite3", Settings(stripe_env_file=keys))
    client = app.test_client()
    client.post("/register")  # no token: refused, only to prove the app serves
    html = client.get("/login").get_data(as_text=True)
    assert SECRET not in html


def test_app_refuses_a_live_key_file(tmp_path: Path) -> None:
    keys = tmp_path / "keys.env"
    publishable, secret = fake_key("pk", "live"), fake_key("sk", "live")
    keys.write_text(
        f"PUBLISHABLE_KEY={publishable}\nSECRET_KEY={secret}\n", encoding="utf-8"
    )
    with pytest.raises(StripeConfigurationError):
        create_app(tmp_path / "shop.sqlite3", Settings(stripe_env_file=keys))


def test_anonymous_checkout_goes_to_login(tmp_path: Path) -> None:
    shop = Shop(tmp_path, FakePaymentGateway())
    response = shop.post("/checkout")
    assert response.status_code == SEE_OTHER
    assert response.headers["Location"] == "/login?next=/basket"


def test_checkout_without_a_csrf_token_is_refused(shop: Shop) -> None:
    shop.add(1)
    assert shop.client.post("/checkout").status_code == 403


def test_empty_basket_checkout_is_a_400(shop: Shop) -> None:
    response = shop.post("/checkout")
    assert response.status_code == 400
    assert constants.ERROR_CHECKOUT_EMPTY in response.get_data(as_text=True)


def test_checkout_redirects_to_the_session_url(
    shop: Shop, payments: FakePaymentGateway
) -> None:
    shop.add(1, 2)
    response = shop.post("/checkout")
    assert response.status_code == SEE_OTHER
    assert response.headers["Location"] == "https://pay.example/cs_test_1"
    request = payments.requests[0]
    assert request.success_url == (
        "http://localhost/checkout/success?session_id={CHECKOUT_SESSION_ID}"
    )
    assert request.cancel_url == "http://localhost/checkout/cancel"
    assert request.client_reference_id == "1"


def test_gateway_failure_is_a_502_with_a_generic_message(
    shop: Shop, payments: FakePaymentGateway
) -> None:
    shop.add(1)
    payments.fail = True
    response = shop.post("/checkout")
    html = response.get_data(as_text=True)
    assert response.status_code == 502
    assert constants.ERROR_CHECKOUT_GATEWAY in html
    assert "fake failure" not in html


def test_paid_session_creates_an_order_and_empties_the_basket(
    shop: Shop, payments: FakePaymentGateway
) -> None:
    shop.add(1, 2)
    session_id = shop.begin()
    payments.pay(session_id)
    response = shop.client.get(f"/checkout/success?session_id={session_id}")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'class="order-number">1<' in html
    assert "Needs confirmation" in html
    assert "25.00" in html
    assert "Notebook" in html
    assert constants.TEXT_BASKET_EMPTY in shop.text("/basket")
    assert "basket-badge" not in shop.text("/basket")
    # reloading the page does not create a second order
    again = shop.client.get(f"/checkout/success?session_id={session_id}")
    assert again.status_code == 200
    assert 'class="order-number">1<' in again.get_data(as_text=True)


def test_unpaid_session_is_a_400_and_keeps_the_basket(shop: Shop) -> None:
    shop.add(1)
    session_id = shop.begin()
    response = shop.client.get(f"/checkout/success?session_id={session_id}")
    assert response.status_code == 400
    assert constants.ERROR_CHECKOUT_NOT_PAID in response.get_data(as_text=True)
    assert constants.TEXT_BASKET_EMPTY not in shop.text("/basket")


def test_missing_session_id_is_a_400(shop: Shop) -> None:
    assert shop.client.get("/checkout/success").status_code == 400


def test_session_of_another_user_is_a_403(
    shop: Shop, payments: FakePaymentGateway
) -> None:
    shop.add(1)
    session_id = shop.begin()
    payments.pay(session_id)
    shop.sign_out()
    shop.sign_up("bob@example.com")
    response = shop.client.get(f"/checkout/success?session_id={session_id}")
    assert response.status_code == 403
    assert constants.ERROR_CHECKOUT_FOREIGN in response.get_data(as_text=True)


def test_unknown_session_is_a_502(shop: Shop) -> None:
    assert shop.client.get("/checkout/success?session_id=cs_nope").status_code == 502


def test_anonymous_success_goes_to_login_and_back(tmp_path: Path) -> None:
    shop = Shop(tmp_path, FakePaymentGateway())
    response = shop.client.get("/checkout/success?session_id=cs_1")
    assert response.status_code == SEE_OTHER
    assert response.headers["Location"].startswith("/login?next=")
    assert "cs_1" in response.headers["Location"]


def test_cancel_keeps_the_basket_and_creates_no_order(shop: Shop) -> None:
    shop.add(1)
    response = shop.client.get("/checkout/cancel")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert constants.TEXT_CHECKOUT_CANCEL_BODY in html
    assert 'href="/basket"' in html
    assert constants.TEXT_BASKET_EMPTY not in shop.text("/basket")


def test_cancel_for_an_anonymous_visitor_goes_to_login(tmp_path: Path) -> None:
    shop = Shop(tmp_path, None)
    assert shop.client.get("/checkout/cancel").status_code == SEE_OTHER


def test_checkout_routes_only_accept_their_method(shop: Shop) -> None:
    assert shop.client.get("/checkout").status_code == 405


def test_create_app_uses_the_environment_keys_when_the_file_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(constants.ENV_STRIPE_PUBLISHABLE_KEY, fake_key("pk", "test"))
    monkeypatch.setenv(constants.ENV_STRIPE_SECRET_KEY, SECRET)
    settings = Settings.from_environment(os.environ)
    settings = replace(settings, stripe_env_file=tmp_path / "absent.env")
    client = create_app(tmp_path / "shop.sqlite3", settings).test_client()
    shop = Shop.__new__(Shop)
    shop.client = client
    shop.sign_up()
    shop.add(1)
    assert 'action="/checkout"' in shop.text("/basket")


def test_create_app_without_settings_ignores_the_real_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(constants.ENV_STRIPE_PUBLISHABLE_KEY, fake_key("pk", "live"))
    monkeypatch.setenv(constants.ENV_STRIPE_SECRET_KEY, fake_key("sk", "live"))
    assert (
        create_app(tmp_path / "shop.sqlite3").test_client().get("/").status_code == 200
    )


def test_create_app_refuses_a_live_key_from_the_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(constants.ENV_STRIPE_PUBLISHABLE_KEY, fake_key("pk", "test"))
    monkeypatch.setenv(constants.ENV_STRIPE_SECRET_KEY, fake_key("sk", "live"))
    settings = replace(
        Settings.from_environment(os.environ), stripe_env_file=tmp_path / "absent.env"
    )
    with pytest.raises(StripeConfigurationError):
        create_app(tmp_path / "shop.sqlite3", settings)
