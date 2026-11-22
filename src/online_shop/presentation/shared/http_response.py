"""@brief The response a controller hands to the HTTP server."""

from dataclasses import dataclass
from http import HTTPStatus

from online_shop import constants


@dataclass(frozen=True)
class HttpResponse:
    """@brief Status, content type, body and extra headers of one HTTP response.

    @param status The HTTP status code.
    @param content_type The value of the Content-Type header.
    @param body The response body as text.
    @param headers Extra headers, as name and value pairs.
    """

    status: HTTPStatus
    content_type: str
    body: str
    headers: tuple[tuple[str, str], ...] = ()


def html_response(
    body: str,
    status: HTTPStatus = constants.STATUS_OK,
    headers: tuple[tuple[str, str], ...] = (),
) -> HttpResponse:
    """@brief Build an HTML response."""
    return HttpResponse(status, constants.CONTENT_TYPE_HTML, body, headers)


def redirect(location: str, headers: tuple[tuple[str, str], ...] = ()) -> HttpResponse:
    """@brief Build a 303 response that sends the browser to another page.

    @param location The path to go to.
    @param headers Extra headers, for example a cookie.
    """
    return HttpResponse(
        constants.STATUS_SEE_OTHER,
        constants.CONTENT_TYPE_HTML,
        "",
        (("Location", location), *headers),
    )
