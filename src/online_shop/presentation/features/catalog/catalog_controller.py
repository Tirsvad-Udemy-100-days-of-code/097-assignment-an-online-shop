"""@brief The controller of the product detail page: a blueprint with one route."""

from http import HTTPStatus

from flask import Blueprint, render_template

from online_shop import constants
from online_shop.application.errors import ProductNotFoundError
from online_shop.application.get_product import GetProduct
from online_shop.presentation.shared.errors import error_page


class CatalogController:
    """@brief Maps a request for one product to the use case and a page."""

    def __init__(self, get_product: GetProduct) -> None:
        """@brief Create the controller.

        @param get_product The use case that fetches one product.
        """
        self._get_product = get_product

    def show(self, product_id: int) -> str | tuple[str, int]:
        """@brief Render the page of one product, or the not-found page.

        @param product_id The key of the product.
        @return The page body, with a status code when it is an error page.
        """
        try:
            product = self._get_product.execute(product_id)
        except ProductNotFoundError:
            return error_page(HTTPStatus.NOT_FOUND, constants.ERROR_PRODUCT_NOT_FOUND)
        return render_template(
            "catalog/product.html",
            title=product.name,
            current=constants.NAV_SHOP,
            product=product,
        )


def create_catalog_blueprint(get_product: GetProduct) -> Blueprint:
    """@brief Build the blueprint of the product pages.

    @param get_product The use case that fetches one product.
    @return A blueprint named "catalog" with the route "/products/<id>".
    """
    blueprint = Blueprint("catalog", __name__)
    controller = CatalogController(get_product)
    blueprint.add_url_rule(
        "/products/<int:product_id>",
        endpoint="show",
        view_func=controller.show,
        methods=["GET"],
    )
    return blueprint
