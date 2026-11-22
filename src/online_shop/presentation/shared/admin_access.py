"""@brief The admin check shared by the admin page and the board."""

from http import HTTPStatus

from flask import jsonify, redirect, url_for
from flask.typing import ResponseReturnValue

from online_shop import constants
from online_shop.presentation.shared.current_user import CurrentUser
from online_shop.presentation.shared.errors import error_page


class AdminAccess:
    """@brief Says whether the request may use an admin route, and how to refuse."""

    def __init__(self, current_user: CurrentUser) -> None:
        """@param current_user The signed-in user of the request."""
        self._current_user = current_user

    def page_denial(self) -> ResponseReturnValue | None:
        """@brief For a page: login redirect when anonymous, 403 page for a customer.

        @return The refusal, or None when the user is an admin.
        """
        user = self._current_user.get()
        if user is None:
            return redirect(url_for("auth.login"), HTTPStatus.SEE_OTHER)
        if not user.is_admin:
            return error_page(HTTPStatus.FORBIDDEN, constants.ERROR_FORBIDDEN)
        return None

    def api_denial(self) -> ResponseReturnValue | None:
        """@brief For the API: 401 JSON when anonymous, 403 JSON for a customer.

        @return The refusal, or None when the user is an admin.
        """
        user = self._current_user.get()
        if user is None:
            return jsonify(error=constants.ERROR_UNAUTHORIZED), HTTPStatus.UNAUTHORIZED
        if not user.is_admin:
            return jsonify(error=constants.ERROR_FORBIDDEN), HTTPStatus.FORBIDDEN
        return None
