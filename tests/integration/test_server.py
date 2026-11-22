"""Tests of the HTTP server over a real local socket."""

import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from online_shop import constants
from online_shop.main import build_router_for
from online_shop.presentation.http_server import create_server


@pytest.fixture
def base_url(tmp_path: Path) -> Iterator[str]:
    server: ThreadingHTTPServer = create_server(
        "127.0.0.1", 0, build_router_for(tmp_path / "shop.sqlite3")
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    yield f"http://{host!s}:{port}"
    server.shutdown()
    server.server_close()


def test_home_page_is_served(base_url: str) -> None:
    with urllib.request.urlopen(base_url + "/") as response:  # noqa: S310
        body = response.read().decode(constants.ENCODING)
        assert response.status == 200
    assert constants.APP_TITLE in body


def test_stylesheet_is_served(base_url: str) -> None:
    with urllib.request.urlopen(base_url + "/static/style.css") as response:  # noqa: S310
        assert response.headers["Content-Type"] == constants.CONTENT_TYPE_CSS


def test_unknown_static_file_gives_404(base_url: str) -> None:
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(base_url + "/static/nothing.js")  # noqa: S310
    assert error.value.code == 404
    error.value.close()


def test_unknown_page_gives_404(base_url: str) -> None:
    with pytest.raises(urllib.error.HTTPError) as error:
        urllib.request.urlopen(base_url + "/missing")  # noqa: S310
    assert error.value.code == 404
    error.value.close()
