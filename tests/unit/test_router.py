"""Tests of the router."""

from online_shop import constants
from online_shop.presentation.router import Router
from online_shop.presentation.shared.http_request import HttpRequest
from online_shop.presentation.shared.http_response import (
    HttpResponse,
    html_response,
    redirect,
)


def echo(request: HttpRequest) -> HttpResponse:
    return html_response(f"{request.params.get('id')}|{request.query.get('q')}")


def test_dispatch_calls_the_handler_with_params_and_query() -> None:
    router = Router()
    router.add("GET", "/items/{id}", echo)
    response = router.dispatch("GET", "/items/42?q=tea", b"")
    assert response.status == constants.STATUS_OK
    assert response.body == "42|tea"


def test_unknown_path_gives_404() -> None:
    response = Router().dispatch("GET", "/nothing", b"")
    assert response.status == constants.STATUS_NOT_FOUND


def test_wrong_method_gives_405() -> None:
    router = Router()
    router.add("GET", "/items/{id}", echo)
    response = router.dispatch("POST", "/items/1", b"")
    assert response.status == constants.STATUS_METHOD_NOT_ALLOWED


def test_redirect_sets_location_and_extra_headers() -> None:
    response = redirect("/next", (("Set-Cookie", "a=b"),))
    assert response.status == constants.STATUS_SEE_OTHER
    assert ("Location", "/next") in response.headers
    assert ("Set-Cookie", "a=b") in response.headers
