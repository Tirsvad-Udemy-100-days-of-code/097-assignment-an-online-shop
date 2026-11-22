"""@brief The one home of the project's constants.

Every literal that more than one place needs, or that a reader may want to
change, is defined here once.
"""

from http import HTTPStatus

## @brief Name of the shop shown in the browser tab and the page header.
APP_TITLE = "Online Shop"

## @brief Interface the server listens on; local use only.
DEFAULT_HOST = "127.0.0.1"

## @brief Port the server listens on.
DEFAULT_PORT = 8000

## @brief File name of the SQLite database.
DATABASE_FILE_NAME = "online_shop.sqlite3"

## @brief Path of the home page.
ROUTE_HOME = "/"

## @brief Content types of the responses.
CONTENT_TYPE_HTML = "text/html; charset=utf-8"
CONTENT_TYPE_CSS = "text/css; charset=utf-8"
CONTENT_TYPE_JS = "text/javascript; charset=utf-8"
CONTENT_TYPE_JSON = "application/json; charset=utf-8"
CONTENT_TYPE_FORM = "application/x-www-form-urlencoded"

## @brief Text encoding of every request and response body.
ENCODING = "utf-8"

## @brief Status codes the server answers with.
STATUS_OK = HTTPStatus.OK
STATUS_SEE_OTHER = HTTPStatus.SEE_OTHER
STATUS_BAD_REQUEST = HTTPStatus.BAD_REQUEST
STATUS_FORBIDDEN = HTTPStatus.FORBIDDEN
STATUS_NOT_FOUND = HTTPStatus.NOT_FOUND
STATUS_METHOD_NOT_ALLOWED = HTTPStatus.METHOD_NOT_ALLOWED

## @brief Static files served under /static/, with their content types.
STATIC_ROUTE_PREFIX = "/static/"
STATIC_FILES = {
    "style.css": CONTENT_TYPE_CSS,
}

## @brief Messages shown for errors.
ERROR_NOT_FOUND = "Not found."
ERROR_METHOD_NOT_ALLOWED = "Method not allowed."

## @brief Largest request body the server reads, in bytes.
MAX_BODY_BYTES = 65536
