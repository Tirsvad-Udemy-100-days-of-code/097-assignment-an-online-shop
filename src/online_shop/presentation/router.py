"""@brief The router: maps a method and a path to a controller function."""

import re
from collections.abc import Callable, Mapping
from http import HTTPStatus
from urllib.parse import parse_qsl

from online_shop import constants
from online_shop.presentation.shared.html import page, text
from online_shop.presentation.shared.http_request import HttpRequest
from online_shop.presentation.shared.http_response import HttpResponse, html_response

Handler = Callable[[HttpRequest], HttpResponse]

_PLACEHOLDERS = {"{id}": r"(?P<id>[0-9]+)", "{name}": r"(?P<name>[A-Za-z0-9_.\-]+)"}


def error_page(status: HTTPStatus, message: str) -> HttpResponse:
    """@brief Build an HTML page that shows an error message."""
    content = (
        f'<section class="error"><h1>{status.value}</h1>'
        f"<p>{text(message)}</p></section>"
    )
    return html_response(page("Error", content), status)


class Router:
    """@brief Holds the routes and answers requests."""

    def __init__(self) -> None:
        """@brief Start with no routes."""
        self._routes: list[tuple[str, re.Pattern[str], Handler]] = []

    def add(self, method: str, pattern: str, handler: Handler) -> None:
        """@brief Register a route.

        @param method The HTTP method.
        @param pattern A path that may hold {id} (digits) or {name} (a file name).
        @param handler The controller function.
        """
        regex = re.escape(pattern)
        for placeholder, replacement in _PLACEHOLDERS.items():
            regex = regex.replace(re.escape(placeholder), replacement)
        self._routes.append((method, re.compile(f"^{regex}$"), handler))

    def dispatch(
        self,
        method: str,
        raw_path: str,
        body: bytes,
        headers: Mapping[str, str] | None = None,
    ) -> HttpResponse:
        """@brief Answer one request.

        @param method The HTTP method.
        @param raw_path The path, with or without a query string.
        @param body The request body.
        @param headers The request headers, with lower-case names.
        @return The response; 404 for an unknown path, 405 for a wrong method.
        """
        path, _, query_text = raw_path.partition("?")
        query = dict(parse_qsl(query_text, keep_blank_values=True))
        path_known = False
        for route_method, pattern, handler in self._routes:
            match = pattern.match(path)
            if match is None:
                continue
            path_known = True
            if route_method == method:
                request = HttpRequest(
                    method, path, match.groupdict(), body, query, headers or {}
                )
                return handler(request)
        if path_known:
            return error_page(
                constants.STATUS_METHOD_NOT_ALLOWED, constants.ERROR_METHOD_NOT_ALLOWED
            )
        return error_page(constants.STATUS_NOT_FOUND, constants.ERROR_NOT_FOUND)
