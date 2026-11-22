"""@brief The HTTP server: reads a request, asks the router, writes the response."""

import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from online_shop import constants
from online_shop.presentation.router import Router

_LOGGER = logging.getLogger(__name__)


def create_server(host: str, port: int, router: Router) -> ThreadingHTTPServer:
    """@brief Create, but do not start, the HTTP server.

    @param host The interface to listen on.
    @param port The port to listen on; 0 lets the system choose one.
    @param router The router that answers every request.
    @return The server, ready for serve_forever.
    """

    class Handler(BaseHTTPRequestHandler):
        """@brief Handles the requests of one connection."""

        def _handle(self) -> None:
            length = min(
                int(self.headers.get("Content-Length") or 0), constants.MAX_BODY_BYTES
            )
            body = self.rfile.read(length) if length else b""
            headers = {name.lower(): value for name, value in self.headers.items()}
            response = router.dispatch(self.command, self.path, body, headers)
            payload = response.body.encode(constants.ENCODING)
            self.send_response(response.status)
            self.send_header("Content-Type", response.content_type)
            self.send_header("Content-Length", str(len(payload)))
            for name, value in response.headers:
                self.send_header(name, value)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(payload)

        do_GET = _handle  # noqa: N815 - names fixed by BaseHTTPRequestHandler
        do_POST = _handle  # noqa: N815

        def log_message(self, format: str, *args: object) -> None:
            """@brief Send the access log to the logging module."""
            _LOGGER.info(format, *args)

    return ThreadingHTTPServer((host, port), Handler)
