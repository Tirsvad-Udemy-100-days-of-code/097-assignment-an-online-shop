"""@brief The guard that refuses state-changing requests without a CSRF token."""

from http import HTTPStatus

from flask import request

from online_shop import constants
from online_shop.presentation.shared.errors import error_page
from online_shop.presentation.shared.session import SessionManager


class CsrfGuard:
    """@brief Runs before every request and rejects a missing or wrong token."""

    def __init__(self, sessions: SessionManager) -> None:
        """@param sessions The session of the request."""
        self._sessions = sessions

    def check(self) -> tuple[str, int] | None:
        """@brief Return the error page to refuse the request, or None to go on."""
        if request.method not in constants.CSRF_PROTECTED_METHODS:
            return None
        submitted = request.form.get(constants.CSRF_FORM_FIELD) or request.headers.get(
            constants.CSRF_HEADER, ""
        )
        if self._sessions.accepts_csrf_token(submitted):
            return None
        return error_page(HTTPStatus.FORBIDDEN, constants.ERROR_CSRF)
