"""@brief The Flask application factory and the composition root of the shop."""

import logging
import secrets
from http import HTTPStatus
from pathlib import Path

from flask import Flask
from werkzeug.exceptions import HTTPException

from online_shop import constants
from online_shop.application.add_to_basket import AddToBasket
from online_shop.application.authenticate_user import AuthenticateUser
from online_shop.application.count_basket_items import CountBasketItems
from online_shop.application.ensure_admin import EnsureAdmin
from online_shop.application.get_product import GetProduct
from online_shop.application.get_user import GetUser
from online_shop.application.list_products import ListProducts
from online_shop.application.register_user import RegisterUser
from online_shop.application.remove_from_basket import RemoveFromBasket
from online_shop.application.update_basket_line import UpdateBasketLine
from online_shop.application.view_basket import ViewBasket
from online_shop.domain.basket_repository import BasketRepository
from online_shop.domain.password_hasher import PasswordHasher
from online_shop.domain.product_repository import ProductRepository
from online_shop.domain.user_repository import UserRepository
from online_shop.infrastructure.database import migrate, seed_products
from online_shop.infrastructure.scrypt_password_hasher import ScryptPasswordHasher
from online_shop.infrastructure.settings import Settings
from online_shop.infrastructure.sqlite_basket_repository import (
    SqliteBasketRepository,
)
from online_shop.infrastructure.sqlite_product_repository import (
    SqliteProductRepository,
)
from online_shop.infrastructure.sqlite_user_repository import SqliteUserRepository
from online_shop.presentation.features.admin.admin_controller import (
    create_admin_blueprint,
)
from online_shop.presentation.features.auth.auth_controller import (
    create_auth_blueprint,
)
from online_shop.presentation.features.basket.basket_controller import (
    create_basket_blueprint,
)
from online_shop.presentation.features.catalog.catalog_controller import (
    create_catalog_blueprint,
)
from online_shop.presentation.features.home.home_controller import (
    create_home_blueprint,
)
from online_shop.presentation.shared.basket_count import BasketCount
from online_shop.presentation.shared.csrf import CsrfGuard
from online_shop.presentation.shared.current_user import CurrentUser
from online_shop.presentation.shared.errors import error_page
from online_shop.presentation.shared.formatting import format_price
from online_shop.presentation.shared.session import SessionManager, configure_sessions

_LOG = logging.getLogger(__name__)

_ERROR_MESSAGES = {
    HTTPStatus.NOT_FOUND: constants.ERROR_NOT_FOUND,
    HTTPStatus.METHOD_NOT_ALLOWED: constants.ERROR_METHOD_NOT_ALLOWED,
    HTTPStatus.FORBIDDEN: constants.ERROR_FORBIDDEN,
}

_BASKET_TEXTS = {
    "title": constants.TEXT_BASKET_TITLE,
    "add": constants.TEXT_BASKET_ADD,
    "update_label": constants.TEXT_BASKET_UPDATE,
    "remove": constants.TEXT_BASKET_REMOVE,
    "total": constants.TEXT_BASKET_TOTAL,
    "quantity": constants.TEXT_BASKET_QUANTITY,
    "empty": constants.TEXT_BASKET_EMPTY,
    "continue": constants.TEXT_BASKET_CONTINUE,
    "unavailable": constants.TEXT_BASKET_UNAVAILABLE,
    "max_quantity": constants.BASKET_MAX_QUANTITY,
}

_AUTH_TEXTS = {
    "login": constants.TEXT_LOGIN,
    "register": constants.TEXT_REGISTER,
    "logout": constants.TEXT_LOGOUT,
    "admin": constants.TEXT_ADMIN,
    "email": constants.TEXT_EMAIL,
    "password": constants.TEXT_PASSWORD,
    "login_title": constants.TEXT_LOGIN_TITLE,
    "register_title": constants.TEXT_REGISTER_TITLE,
    "password_hint": constants.TEXT_PASSWORD_HINT,
    "no_account": constants.TEXT_NO_ACCOUNT,
    "have_account": constants.TEXT_HAVE_ACCOUNT,
    "signed_in_as": constants.TEXT_SIGNED_IN_AS,
    "admin_title": constants.TEXT_ADMIN_TITLE,
    "admin_body": constants.TEXT_ADMIN_BODY,
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
            "auth": _AUTH_TEXTS,
            "basket": _BASKET_TEXTS,
        }
    }


def _handle_http_error(error: HTTPException) -> tuple[str, int]:
    status = HTTPStatus(error.code or HTTPStatus.INTERNAL_SERVER_ERROR)
    return error_page(status, _ERROR_MESSAGES.get(status, status.phrase))


def create_app_for(
    products: ProductRepository,
    users: UserRepository,
    baskets: BasketRepository,
    hasher: PasswordHasher,
    secret_key: str,
) -> Flask:
    """@brief Wire the use cases, blueprints and templates around the ports.

    @param products The port that reads the catalog.
    @param users The port that stores users.
    @param baskets The port that stores baskets.
    @param hasher The port that hashes passwords.
    @param secret_key The key that signs the session cookie.
    @return The Flask application.
    """
    app = Flask(__name__)
    configure_sessions(app, secret_key)
    sessions = SessionManager()
    current_user = CurrentUser(GetUser(users), sessions)
    app.before_request(CsrfGuard(sessions).check)
    app.context_processor(_site_context)
    app.context_processor(current_user.template_context)
    app.context_processor(
        BasketCount(CountBasketItems(baskets), sessions).template_context
    )
    app.add_template_filter(format_price, "price")
    app.register_blueprint(create_home_blueprint(ListProducts(products)))
    app.register_blueprint(create_catalog_blueprint(GetProduct(products)))
    app.register_blueprint(
        create_auth_blueprint(
            RegisterUser(users, hasher), AuthenticateUser(users, hasher), sessions
        )
    )
    app.register_blueprint(create_admin_blueprint(current_user))
    app.register_blueprint(
        create_basket_blueprint(
            current_user,
            ViewBasket(baskets, products),
            AddToBasket(baskets, products),
            UpdateBasketLine(baskets, products),
            RemoveFromBasket(baskets),
        )
    )
    app.register_error_handler(HTTPException, _handle_http_error)
    return app


def create_app(database_path: Path, settings: Settings | None = None) -> Flask:
    """@brief Prepare the database and build the shop on top of it.

    This is the composition root: the only place that builds the adapters.

    @param database_path The SQLite file; it is migrated and seeded here.
    @param settings Secret key and optional admin account; defaults to none,
        which gives a random secret key and no admin.
    @return The Flask application.
    """
    settings = settings or Settings()
    migrate(database_path)
    seed_products(database_path)
    secret_key = settings.secret_key
    if secret_key is None:
        _LOG.warning(
            "%s is not set; sessions end when the server restarts.",
            constants.ENV_SECRET_KEY,
        )
        secret_key = secrets.token_urlsafe(constants.SECRET_KEY_BYTES)
    users = SqliteUserRepository(database_path)
    hasher = ScryptPasswordHasher()
    if settings.admin_email and settings.admin_password:
        EnsureAdmin(users, RegisterUser(users, hasher)).execute(
            settings.admin_email, settings.admin_password
        )
    return create_app_for(
        SqliteProductRepository(database_path),
        users,
        SqliteBasketRepository(database_path),
        hasher,
        secret_key,
    )
