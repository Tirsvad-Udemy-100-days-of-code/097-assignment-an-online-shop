"""Tests of the Flask routes and templates, with a fake catalog."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from flask.testing import FlaskClient

from fakes import FakePasswordHasher, FakeUserRepository
from online_shop import constants
from online_shop.domain.money import Money
from online_shop.domain.product import Product
from online_shop.presentation.app import create_app, create_app_for
from online_shop.presentation.shared.formatting import format_price

HOSTILE = Product(2, "<script>x</script>", 'a "b" & c', Money(5), "x.svg")


class FakeProductRepository:
    def __init__(self, products: list[Product]) -> None:
        self._products = products

    def list_all(self) -> list[Product]:
        return list(self._products)

    def get(self, product_id: int) -> Product | None:
        return next((p for p in self._products if p.id == product_id), None)


def build_client(products: list[Product]) -> FlaskClient:
    """Create an app with the real templates and a fake repository."""
    app = create_app_for(
        FakeProductRepository(products),
        FakeUserRepository(),
        FakePasswordHasher(),
        "test-secret",
    )
    return app.test_client()


MUG = Product(1, "Mug", "Ceramic mug", Money(1205), "mug.svg")


@pytest.fixture
def client() -> Iterator[FlaskClient]:
    yield build_client([MUG])


def get_text(client: FlaskClient, path: str) -> tuple[int, str]:
    response = client.get(path)
    return response.status_code, response.get_data(as_text=True)


def test_format_price_writes_major_and_minor_units() -> None:
    assert format_price(1205) == constants.CURRENCY_SYMBOL + "12.05"
    assert format_price(0) == constants.CURRENCY_SYMBOL + "0.00"


def test_home_page_has_layout_and_marks_home_active(client: FlaskClient) -> None:
    status, html = get_text(client, "/")
    assert status == 200
    assert "<title>Home - " + constants.APP_TITLE in html
    assert constants.APP_TAGLINE in html
    assert 'id="nav-toggle"' in html
    assert '<a href="/" class="active" aria-current="page">Home</a>' in html
    assert '<a href="/#shop">Shop</a>' in html


def test_home_page_has_hero_and_brand_strip(client: FlaskClient) -> None:
    _, html = get_text(client, "/")
    assert 'class="hero"' in html
    assert constants.HERO_LABEL in html
    assert constants.HERO_BUTTON in html
    assert 'id="shop"' in html
    assert constants.FEATURED_TITLE in html
    assert f'src="/static/{constants.HERO_IMAGE}"' in html
    assert html.count('class="brand-tile"') == constants.BRAND_TILE_COUNT


def test_home_page_shows_the_product_grid(client: FlaskClient) -> None:
    _, html = get_text(client, "/")
    assert 'class="product-grid"' in html
    assert f'<span class="tag">{constants.SALE_TAG}</span>' in html
    assert "Mug" in html
    assert 'src="/static/mug.svg"' in html
    assert 'href="/products/1"' in html
    assert "12.05" in html


def test_home_page_without_products_says_so() -> None:
    _, html = get_text(build_client([]), "/")
    assert "no products" in html
    assert 'class="product-grid"' not in html


def test_home_page_escapes_product_text() -> None:
    _, html = get_text(build_client([HOSTILE]), "/")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_detail_page_shows_the_product_and_marks_shop_active(
    client: FlaskClient,
) -> None:
    status, html = get_text(client, "/products/1")
    assert status == 200
    assert "<title>Mug - " + constants.APP_TITLE in html
    assert "Ceramic mug" in html
    assert "12.05" in html
    assert '<a href="/#shop" class="active" aria-current="page">Shop</a>' in html


def test_detail_page_escapes_product_text() -> None:
    _, html = get_text(build_client([HOSTILE]), "/products/2")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


@pytest.mark.parametrize(
    "path", ["/products/9", "/products/abc", "/products/-1", "/products/1" + "0" * 30]
)
def test_unknown_product_gives_404(client: FlaskClient, path: str) -> None:
    status, html = get_text(client, path)
    assert status == 404
    assert 'class="error"' in html


def test_unknown_product_page_names_the_product_error(client: FlaskClient) -> None:
    _, html = get_text(client, "/products/9")
    assert constants.ERROR_PRODUCT_NOT_FOUND in html


def test_unknown_path_gives_404_page(client: FlaskClient) -> None:
    status, html = get_text(client, "/missing")
    assert status == 404
    assert constants.ERROR_NOT_FOUND in html


def test_wrong_method_gives_405_page(client: FlaskClient) -> None:
    with client.session_transaction() as session:
        session[constants.SESSION_CSRF_KEY] = "token"
    response = client.post("/", data={constants.CSRF_FORM_FIELD: "token"})
    assert response.status_code == 405
    assert constants.ERROR_METHOD_NOT_ALLOWED in response.get_data(as_text=True)


def test_create_app_builds_the_database(tmp_path: Path) -> None:
    app = create_app(tmp_path / "shop.sqlite3")
    assert app.test_client().get("/").status_code == 200
