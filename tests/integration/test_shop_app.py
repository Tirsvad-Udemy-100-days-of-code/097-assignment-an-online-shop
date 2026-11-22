"""Tests of the whole Flask application over a temporary SQLite file."""

from pathlib import Path

import pytest
from flask.testing import FlaskClient

from online_shop import constants
from online_shop.presentation.app import create_app

STATIC_DIR = Path(__file__).resolve().parents[2] / "src/online_shop/presentation/static"


@pytest.fixture
def client(tmp_path: Path) -> FlaskClient:
    return create_app(tmp_path / "shop.sqlite3").test_client()


def test_home_page_lists_every_seeded_product(client: FlaskClient) -> None:
    response = client.get("/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert constants.APP_TITLE in body
    for name, _, _, image in constants.SEED_PRODUCTS:
        assert name in body
        assert f"/static/{image}" in body


def test_product_detail_page_is_served(client: FlaskClient) -> None:
    body = client.get("/products/1").get_data(as_text=True)
    assert constants.SEED_PRODUCTS[0][0] in body


@pytest.mark.parametrize(
    "path", ["/products/999", "/products/abc", "/products/1" + "0" * 30, "/missing"]
)
def test_unknown_page_gives_404(client: FlaskClient, path: str) -> None:
    assert client.get(path).status_code == 404


def test_stylesheet_and_hero_are_served(client: FlaskClient) -> None:
    css = client.get("/static/style.css")
    hero = client.get(f"/static/{constants.HERO_IMAGE}")
    assert css.status_code == 200
    assert css.mimetype == "text/css"
    assert hero.status_code == 200
    assert hero.mimetype == "image/svg+xml"
    css.close()
    hero.close()


def test_every_seeded_image_is_a_static_file(client: FlaskClient) -> None:
    for seed in constants.SEED_PRODUCTS:
        assert (STATIC_DIR / seed[3]).is_file()
        response = client.get(f"/static/{seed[3]}")
        assert response.status_code == 200
        response.close()


def test_unknown_static_file_gives_404(client: FlaskClient) -> None:
    assert client.get("/static/nothing.js").status_code == 404


def test_data_survives_a_restart(tmp_path: Path) -> None:
    database = tmp_path / "shop.sqlite3"
    create_app(database)
    again = create_app(database).test_client().get("/")
    assert again.get_data(as_text=True).count('class="product-card"') == len(
        constants.SEED_PRODUCTS
    )
