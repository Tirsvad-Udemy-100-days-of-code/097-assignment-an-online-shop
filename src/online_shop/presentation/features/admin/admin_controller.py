"""@brief The controller of the admin-only page."""

from flask import Blueprint, render_template
from flask.typing import ResponseReturnValue

from online_shop import constants
from online_shop.presentation.shared.admin_access import AdminAccess


class AdminController:
    """@brief Serves admin pages to admins only."""

    def __init__(self, access: AdminAccess) -> None:
        """@param access The admin check."""
        self._access = access

    def show(self) -> ResponseReturnValue:
        """@brief Admin page; anonymous goes to login, a customer gets 403."""
        denied = self._access.page_denial()
        if denied is not None:
            return denied
        return render_template("admin/index.html", title=constants.TEXT_ADMIN)


def create_admin_blueprint(access: AdminAccess) -> Blueprint:
    """@brief Build the blueprint "admin" with the route "/admin"."""
    blueprint = Blueprint("admin", __name__)
    controller = AdminController(access)
    blueprint.add_url_rule(
        "/admin", endpoint="show", view_func=controller.show, methods=["GET"]
    )
    return blueprint
