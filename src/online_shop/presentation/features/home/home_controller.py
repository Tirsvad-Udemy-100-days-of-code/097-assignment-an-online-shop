"""@brief The controller of the home page: a blueprint with one route."""

from flask import Blueprint, render_template

from online_shop import constants
from online_shop.application.list_products import ListProducts


class HomeController:
    """@brief Maps a request for the home page to the use case and a page."""

    def __init__(self, list_products: ListProducts) -> None:
        """@brief Create the controller.

        @param list_products The use case that lists the catalog.
        """
        self._list_products = list_products

    def show(self) -> str:
        """@brief Render the home page with the catalog.

        @return The page body.
        """
        return render_template(
            "home/index.html",
            title="Home",
            current=constants.NAV_HOME,
            products=self._list_products.execute(),
        )


def create_home_blueprint(list_products: ListProducts) -> Blueprint:
    """@brief Build the blueprint of the home page.

    @param list_products The use case that lists the catalog.
    @return A blueprint named "home" with the route "/".
    """
    blueprint = Blueprint("home", __name__)
    controller = HomeController(list_products)
    blueprint.add_url_rule(
        "/", endpoint="show", view_func=controller.show, methods=["GET"]
    )
    return blueprint
