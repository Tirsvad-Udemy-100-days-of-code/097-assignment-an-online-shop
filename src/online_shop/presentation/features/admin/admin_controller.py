"""@brief The controller of the admin-only page."""

from http import HTTPStatus

from flask import Blueprint, redirect, render_template, url_for
from flask.typing import ResponseReturnValue

from online_shop import constants
from online_shop.presentation.shared.current_user import CurrentUser
from online_shop.presentation.shared.errors import error_page


class AdminController:
    """@brief Serves admin pages to admins only."""

    def __init__(self, current_user: CurrentUser) -> None:
        """@param current_user The signed-in user of the request."""
        self._current_user = current_user

    def show(self) -> ResponseReturnValue:
        """@brief Admin page; anonymous goes to login, a customer gets 403."""
        user = self._current_user.get()
        if user is None:
            return redirect(url_for("auth.login"), HTTPStatus.SEE_OTHER)
        if not user.is_admin:
            return error_page(HTTPStatus.FORBIDDEN, constants.ERROR_FORBIDDEN)
        return render_template("admin/index.html", title=constants.TEXT_ADMIN)


def create_admin_blueprint(current_user: CurrentUser) -> Blueprint:
    """@brief Build the blueprint "admin" with the route "/admin"."""
    blueprint = Blueprint("admin", __name__)
    controller = AdminController(current_user)
    blueprint.add_url_rule(
        "/admin", endpoint="show", view_func=controller.show, methods=["GET"]
    )
    return blueprint
