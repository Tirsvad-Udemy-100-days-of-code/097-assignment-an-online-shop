"""Tests of the home page and the shared HTML helpers."""

from online_shop import constants
from online_shop.presentation.features.home.home_controller import HomeController
from online_shop.presentation.features.home.home_view import render_home
from online_shop.presentation.shared.html import page, text
from online_shop.presentation.shared.http_request import HttpRequest


def test_text_escapes_markup() -> None:
    assert text("<b>&\"'") == "&lt;b&gt;&amp;&quot;&#x27;"


def test_page_wraps_content_with_title_and_navigation() -> None:
    html = page("Basket", "<p>x</p>", "<a href='/'>Home</a>")
    assert "<title>Basket - " + constants.APP_TITLE in html
    assert "<p>x</p>" in html
    assert "<a href='/'>Home</a>" in html


def test_home_page_welcomes_the_visitor() -> None:
    assert constants.APP_TITLE in render_home()


def test_controller_returns_the_home_page() -> None:
    response = HomeController().show(HttpRequest("GET", "/", {}, b""))
    assert response.status == constants.STATUS_OK
    assert response.content_type == constants.CONTENT_TYPE_HTML
