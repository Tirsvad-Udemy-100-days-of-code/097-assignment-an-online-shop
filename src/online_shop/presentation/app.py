"""@brief The Flask application factory and the composition root of the shop."""

from http import HTTPStatus
from pathlib import Path

from flask import Flask
from werkzeug.exceptions import HTTPException

from online_shop import constants
from online_shop.application.get_product import GetProduct
from online_shop.application.list_products import ListProducts
from online_shop.domain.product_repository import ProductRepository
from online_shop.infrastructure.database import migrate, seed_products
from online_shop.infrastructure.sqlite_product_repository import (
    SqliteProductRepository,
)
from online_shop.presentation.features.catalog.catalog_controller import (
    create_catalog_blueprint,
)
from online_shop.presentation.features.home.home_controller import (
    create_home_blueprint,
)
from online_shop.presentation.shared.errors import error_page
from online_shop.presentation.shared.formatting import format_price

_ERROR_MESSAGES = {
    HTTPStatus.NOT_FOUND: constants.ERROR_NOT_FOUND,
    HTTPStatus.METHOD_NOT_ALLOWED: constants.ERROR_METHOD_NOT_ALLOWED,
}


def _site_context() -> dict[str, object]:
    """@brief The constants every template needs, as the variable `site`."""
    return {
        "site": {
            "title": constants.APP_TITLE,
            "tagline": constants.APP_TAGLINE,
            "nav_links": constants.NAV_LINKS,
            "label_search": constants.LABEL_SEARCH,
            "label_basket": constants.LABEL_BASKET,
            "label_menu": constants.LABEL_MENU,
            "hero_label": constants.HERO_LABEL,
            "hero_title": constants.HERO_TITLE,
            "hero_button": constants.HERO_BUTTON,
            "hero_image": constants.HERO_IMAGE,
            "hero_image_alt": constants.HERO_IMAGE_ALT,
            "featured_title": constants.FEATURED_TITLE,
            "featured_subtitle": constants.FEATURED_SUBTITLE,
            "sale_tag": constants.SALE_TAG,
            "brand_tiles": range(constants.BRAND_TILE_COUNT),
            "brand_tile_label": constants.BRAND_TILE_LABEL,
        }
    }


def _handle_http_error(error: HTTPException) -> tuple[str, int]:
    status = HTTPStatus(error.code or HTTPStatus.INTERNAL_SERVER_ERROR)
    return error_page(status, _ERROR_MESSAGES.get(status, status.phrase))


def create_app_for(products: ProductRepository) -> Flask:
    """@brief Wire the use cases, blueprints and templates around a catalog port.

    @param products The port that reads the catalog.
    @return The Flask application.
    """
    app = Flask(__name__)
    app.context_processor(_site_context)
    app.add_template_filter(format_price, "price")
    app.register_blueprint(create_home_blueprint(ListProducts(products)))
    app.register_blueprint(create_catalog_blueprint(GetProduct(products)))
    app.register_error_handler(HTTPException, _handle_http_error)
    return app


def create_app(database_path: Path) -> Flask:
    """@brief Prepare the database and build the shop on top of it.

    This is the composition root: the only place that builds the SQLite adapter.

    @param database_path The SQLite file; it is migrated and seeded here.
    @return The Flask application.
    """
    migrate(database_path)
    seed_products(database_path)
    return create_app_for(SqliteProductRepository(database_path))
