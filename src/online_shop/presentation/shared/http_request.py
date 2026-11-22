"""@brief The request a controller receives from the router."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from urllib.parse import parse_qsl

from online_shop import constants


@dataclass(frozen=True)
class HttpRequest:
    """@brief Method, path, query, path parameters, headers and body of one request.

    @param method The HTTP method, for example GET.
    @param path The path without the query string.
    @param params The values taken from the path pattern, for example id.
    @param body The raw request body.
    @param query The query string, parsed.
    @param headers The request headers, with lower-case names.
    """

    method: str
    path: str
    params: Mapping[str, str]
    body: bytes
    query: Mapping[str, str] = field(default_factory=dict)
    headers: Mapping[str, str] = field(default_factory=dict)

    def form(self) -> dict[str, str]:
        """@brief Parse the body as an HTML form.

        @return The fields of the form; the last value of a repeated field wins.
        """
        text = self.body.decode(constants.ENCODING, errors="replace")
        return dict(parse_qsl(text, keep_blank_values=True))

    def cookies(self) -> dict[str, str]:
        """@brief Parse the Cookie header.

        @return The cookie names and their values.
        """
        cookie: SimpleCookie = SimpleCookie()
        cookie.load(self.headers.get("cookie", ""))
        return {name: morsel.value for name, morsel in cookie.items()}

    def path_id(self) -> int:
        """@brief Return the id taken from the path."""
        return int(self.params["id"])
