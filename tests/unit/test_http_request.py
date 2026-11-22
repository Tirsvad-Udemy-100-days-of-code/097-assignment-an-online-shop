"""Tests of the request object."""

from online_shop.presentation.shared.http_request import HttpRequest


def make(body: bytes = b"", headers: dict[str, str] | None = None) -> HttpRequest:
    return HttpRequest("POST", "/x", {"id": "7"}, body, {}, headers or {})


def test_form_parses_fields_and_keeps_blank_values() -> None:
    request = make(b"email=a%40b.dk&note=")
    assert request.form() == {"email": "a@b.dk", "note": ""}


def test_cookies_are_read_from_the_cookie_header() -> None:
    request = make(headers={"cookie": "session=abc; theme=dark"})
    assert request.cookies() == {"session": "abc", "theme": "dark"}


def test_cookies_are_empty_without_a_header() -> None:
    assert make().cookies() == {}


def test_path_id_returns_a_number() -> None:
    assert make().path_id() == 7
