"""@brief Serves the files in the static folder."""

from pathlib import Path

from online_shop import constants
from online_shop.presentation.shared.http_request import HttpRequest
from online_shop.presentation.shared.http_response import HttpResponse, html_response

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def serve_static(request: HttpRequest) -> HttpResponse:
    """@brief Return a static file; only the names in constants.STATIC_FILES exist."""
    name = request.params["name"]
    content_type = constants.STATIC_FILES.get(name)
    if content_type is None:
        return html_response(constants.ERROR_NOT_FOUND, constants.STATUS_NOT_FOUND)
    body = (_STATIC_DIR / name).read_text(encoding=constants.ENCODING)
    return HttpResponse(constants.STATUS_OK, content_type, body)
