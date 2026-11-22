"""@brief The controller of the product detail page: a blueprint with one route."""

from http import HTTPStatus

from flask import Blueprint, render_template

from online_shop import constants
from online_shop.application.errors import ProductNotFoundError
from online_shop.application.get_product import GetProduct
from online_shop.presentation.shared.errors import error_page


def create_catalog_blueprint(get_product: GetProduct) -> Blueprint:
    """@brief Build the blueprint of the product pages.

    @param get_product The use case that fetches one product.
    @return A blueprint named "catalog" with the route "/products/<id>".
    """
    blueprint = Blueprint("catalog", __name__)

    @blueprint.get("/products/<int:product_id>")
    def show(product_id: int) -> str | tuple[str, int]:
        try:
            product = get_product.execute(product_id)
        except ProductNotFoundError:
            return error_page(HTTPStatus.NOT_FOUND, constants.ERROR_PRODUCT_NOT_FOUND)
        return render_template(
            "catalog/product.html",
            title=product.name,
            current=constants.NAV_SHOP,
            product=product,
        )

    return blueprint
