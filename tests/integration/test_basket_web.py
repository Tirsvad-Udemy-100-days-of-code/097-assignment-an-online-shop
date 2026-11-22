"""Tests of the basket routes, CSRF, login redirect and the header count."""

import re
from pathlib import Path

import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from online_shop import constants
from online_shop.presentation.app import create_app

PASSWORD = "correct horse"
SEE_OTHER = 303


@pytest.fixture
def client(tmp_path: Path) -> FlaskClient:
    return create_app(tmp_path / "shop.sqlite3").test_client()


def token_of(client: FlaskClient, path: str) -> str:
    html = client.get(path).get_data(as_text=True)
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match
    return match.group(1)


def post(client: FlaskClient, path: str, **fields: str) -> TestResponse:
    data = {constants.CSRF_FORM_FIELD: token_of(client, "/login"), **fields}
    return client.post(path, data=data)


def sign_up(client: FlaskClient, email: str = "ann@example.com") -> None:
    post(client, "/register", email=email, password=PASSWORD)


def sign_out(client: FlaskClient) -> None:
    post(client, "/logout")


def sign_in(client: FlaskClient, email: str = "ann@example.com") -> None:
    post(client, "/login", email=email, password=PASSWORD)


def page(client: FlaskClient, path: str = "/basket") -> str:
    return client.get(path).get_data(as_text=True)


def test_anonymous_basket_page_redirects_to_login(client: FlaskClient) -> None:
    response = client.get("/basket")
    assert response.status_code == SEE_OTHER
    assert response.headers["Location"] == "/login?next=/basket"


@pytest.mark.parametrize("path", ["/basket/add", "/basket/update", "/basket/remove"])
def test_anonymous_post_redirects_to_login(client: FlaskClient, path: str) -> None:
    response = post(client, path, product_id="1", next="/products/1")
    assert response.status_code == SEE_OTHER
    assert response.headers["Location"] == "/login?next=/products/1"


def test_anonymous_post_ignores_an_external_next(client: FlaskClient) -> None:
    response = post(client, "/basket/add", product_id="1", next="https://evil.test/")
    assert response.headers["Location"] == "/login?next=/basket"


def test_post_without_a_csrf_token_is_refused(client: FlaskClient) -> None:
    sign_up(client)
    assert client.post("/basket/add", data={"product_id": "1"}).status_code == 403


def test_empty_basket_shows_the_empty_state(client: FlaskClient) -> None:
    sign_up(client)
    html = page(client)
    assert constants.TEXT_BASKET_EMPTY in html
    assert 'href="/#shop"' in html
    assert "basket-badge" not in html


def test_add_twice_then_the_page_shows_quantity_total_and_badge(
    client: FlaskClient,
) -> None:
    sign_up(client)
    response = post(client, "/basket/add", product_id="1", next="/")
    assert response.status_code == SEE_OTHER
    assert response.headers["Location"] == "/"
    post(client, "/basket/add", product_id="1", quantity="2")
    post(client, "/basket/add", product_id="2")
    html = page(client)
    assert 'value="3"' in html
    assert constants.CURRENCY_SYMBOL + "37.50" in html
    assert constants.CURRENCY_SYMBOL + "34.90" in html
    assert constants.CURRENCY_SYMBOL + "72.40" in html
    assert '<span class="basket-badge">4</span>' in html


def test_add_without_next_goes_to_the_basket(client: FlaskClient) -> None:
    sign_up(client)
    response = post(client, "/basket/add", product_id="1", next="//evil.test")
    assert response.headers["Location"] == "/basket"


def test_update_sets_the_quantity_and_zero_removes(client: FlaskClient) -> None:
    sign_up(client)
    post(client, "/basket/add", product_id="1")
    post(client, "/basket/update", product_id="1", quantity="5")
    assert '<span class="basket-badge">5</span>' in page(client)
    post(client, "/basket/update", product_id="1", quantity="0")
    assert constants.TEXT_BASKET_EMPTY in page(client)


def test_remove_drops_the_line(client: FlaskClient) -> None:
    sign_up(client)
    post(client, "/basket/add", product_id="1")
    post(client, "/basket/remove", product_id="1")
    assert constants.TEXT_BASKET_EMPTY in page(client)


@pytest.mark.parametrize(
    ("quantity", "message"),
    [
        ("100", constants.ERROR_QUANTITY_LIMIT),
        ("-1", constants.ERROR_QUANTITY_INVALID),
        ("many", constants.ERROR_QUANTITY_INVALID),
    ],
)
def test_bad_quantity_shows_an_error_on_the_basket_page(
    client: FlaskClient, quantity: str, message: str
) -> None:
    sign_up(client)
    response = post(client, "/basket/update", product_id="1", quantity=quantity)
    assert response.status_code == 400
    assert message in response.get_data(as_text=True)


def test_adding_past_the_limit_is_an_error(client: FlaskClient) -> None:
    sign_up(client)
    post(client, "/basket/add", product_id="1", quantity="99")
    response = post(client, "/basket/add", product_id="1")
    assert response.status_code == 400
    assert constants.ERROR_QUANTITY_LIMIT in response.get_data(as_text=True)


@pytest.mark.parametrize("product_id", ["999", "abc", ""])
def test_unknown_product_is_404(client: FlaskClient, product_id: str) -> None:
    sign_up(client)
    response = post(client, "/basket/add", product_id=product_id)
    assert response.status_code == 404
    assert constants.ERROR_PRODUCT_NOT_FOUND in response.get_data(as_text=True)


def test_update_without_a_quantity_is_a_validation_error(client: FlaskClient) -> None:
    sign_up(client)
    assert post(client, "/basket/update", product_id="1").status_code == 400


def test_basket_is_kept_after_logout_and_login(client: FlaskClient) -> None:
    sign_up(client)
    post(client, "/basket/add", product_id="3", quantity="2")
    sign_out(client)
    sign_in(client)
    assert '<span class="basket-badge">2</span>' in page(client)


def test_baskets_are_separate_per_user(client: FlaskClient) -> None:
    sign_up(client)
    post(client, "/basket/add", product_id="1")
    sign_out(client)
    sign_up(client, "bob@example.com")
    assert constants.TEXT_BASKET_EMPTY in page(client)


def test_catalog_and_detail_pages_have_add_forms_with_csrf(
    client: FlaskClient,
) -> None:
    for path, next_path in (("/", "/"), ("/products/1", "/products/1")):
        html = page(client, path)
        assert 'action="/basket/add"' in html
        assert 'name="csrf_token"' in html
        assert f'name="next" value="{next_path}"' in html
    assert page(client, "/").count('action="/basket/add"') == len(
        constants.SEED_PRODUCTS
    )
    assert html.count('action="/basket/add"') == 1


def test_anonymous_header_has_no_badge(client: FlaskClient) -> None:
    assert "basket-badge" not in page(client, "/")


def test_basket_page_shows_the_real_button_texts(client: FlaskClient) -> None:
    sign_up(client)
    post(client, "/basket/add", product_id="1")
    html = page(client)
    assert f">{constants.TEXT_BASKET_UPDATE}</button>" in html
    assert f">{constants.TEXT_BASKET_REMOVE}</button>" in html
    assert "<built-in" not in html
