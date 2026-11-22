"""@brief The controller of the home page: a blueprint with one route."""

from flask import Blueprint, render_template

from online_shop import constants
from online_shop.application.list_products import ListProducts


def create_home_blueprint(list_products: ListProducts) -> Blueprint:
    """@brief Build the blueprint of the home page.

    @param list_products The use case that lists the catalog.
    @return A blueprint named "home" with the route "/".
    """
    blueprint = Blueprint("home", __name__)

    @blueprint.get("/")
    def show() -> str:
        return render_template(
            "home/index.html",
            title="Home",
            current=constants.NAV_HOME,
            products=list_products.execute(),
        )

    return blueprint
