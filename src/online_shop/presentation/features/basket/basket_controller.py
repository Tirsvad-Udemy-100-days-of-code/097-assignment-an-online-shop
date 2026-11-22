"""@brief The controller of the basket page and its add, update, remove forms."""

from collections.abc import Callable
from http import HTTPStatus

from flask import Blueprint, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

from online_shop import constants
from online_shop.application.add_to_basket import AddToBasket
from online_shop.application.errors import ProductNotFoundError
from online_shop.application.remove_from_basket import RemoveFromBasket
from online_shop.application.update_basket_line import UpdateBasketLine
from online_shop.application.view_basket import ViewBasket
from online_shop.domain.errors import InvalidQuantityError
from online_shop.presentation.shared.current_user import CurrentUser
from online_shop.presentation.shared.errors import error_page
from online_shop.presentation.shared.redirects import local_path_or


def _int_field(name: str, default: int | None = None) -> int | None:
    """The whole number in a form field, the default when it is absent, else None."""
    text = request.form.get(name)
    if text is None or not text.strip():
        return default
    try:
        return int(text)
    except ValueError:
        return None


class BasketController:
    """@brief Maps the basket forms to the use cases and the basket page."""

    def __init__(
        self,
        current_user: CurrentUser,
        view: ViewBasket,
        add: AddToBasket,
        update: UpdateBasketLine,
        remove: RemoveFromBasket,
    ) -> None:
        """@param current_user The signed-in user of the request.
        @param view The use case that shows the basket.
        @param add The use case that adds a product.
        @param update The use case that sets a quantity.
        @param remove The use case that removes a product.
        """
        self._current_user = current_user
        self._view = view
        self._add = add
        self._update = update
        self._remove = remove

    def show(self) -> ResponseReturnValue:
        """@brief Render the basket; anonymous visitors go to the login page."""
        user = self._current_user.get()
        if user is None:
            return self._to_login(url_for("basket.show"))
        return self._page(user.id, None, HTTPStatus.OK)

    def add(self) -> ResponseReturnValue:
        """@brief Add a product (default one piece), then go back to `next`."""
        return self._run(self._do_add)

    def update(self) -> ResponseReturnValue:
        """@brief Set the quantity of a line; 0 removes it."""
        return self._run(self._do_update)

    def remove(self) -> ResponseReturnValue:
        """@brief Remove a line from the basket."""
        return self._run(self._do_remove)

    def _do_add(self, user_id: int) -> None:
        quantity = _int_field(
            constants.FIELD_QUANTITY, constants.BASKET_DEFAULT_ADD_QUANTITY
        )
        self._add.execute(user_id, self._product_id(), self._checked(quantity))

    def _do_update(self, user_id: int) -> None:
        quantity = _int_field(constants.FIELD_QUANTITY)
        self._update.execute(user_id, self._product_id(), self._checked(quantity))

    def _do_remove(self, user_id: int) -> None:
        self._remove.execute(user_id, self._product_id())

    @staticmethod
    def _product_id() -> int:
        product_id = _int_field(constants.FIELD_PRODUCT_ID)
        if product_id is None:
            raise ProductNotFoundError(request.form.get(constants.FIELD_PRODUCT_ID))
        return product_id

    @staticmethod
    def _checked(quantity: int | None) -> int:
        if quantity is None:
            raise InvalidQuantityError(constants.ERROR_QUANTITY_INVALID)
        return quantity

    def _run(self, action: Callable[[int], None]) -> ResponseReturnValue:
        target = local_path_or(
            request.form.get(constants.FIELD_NEXT), url_for("basket.show")
        )
        user = self._current_user.get()
        if user is None:
            return self._to_login(target)
        try:
            action(user.id)
        except ProductNotFoundError:
            return error_page(HTTPStatus.NOT_FOUND, constants.ERROR_PRODUCT_NOT_FOUND)
        except InvalidQuantityError as error:
            return self._page(user.id, str(error), HTTPStatus.BAD_REQUEST)
        return redirect(target, HTTPStatus.SEE_OTHER)

    @staticmethod
    def _to_login(target: str) -> ResponseReturnValue:
        login = url_for("auth.login", next=target)
        return redirect(login, HTTPStatus.SEE_OTHER)

    def _page(
        self, user_id: int, error: str | None, status: HTTPStatus
    ) -> tuple[str, int]:
        body = render_template(
            "basket/index.html",
            title=constants.TEXT_BASKET_TITLE,
            basket=self._view.execute(user_id),
            form_error=error,
        )
        return body, status


def create_basket_blueprint(
    current_user: CurrentUser,
    view: ViewBasket,
    add: AddToBasket,
    update: UpdateBasketLine,
    remove: RemoveFromBasket,
) -> Blueprint:
    """@brief Build the blueprint "basket" with /basket and its three forms."""
    blueprint = Blueprint("basket", __name__)
    controller = BasketController(current_user, view, add, update, remove)
    routes = (
        ("/basket", "show", controller.show),
        ("/basket/add", "add", controller.add),
        ("/basket/update", "update", controller.update),
        ("/basket/remove", "remove", controller.remove),
    )
    for rule, endpoint, handler in routes:
        methods = ["GET"] if endpoint == "show" else ["POST"]
        blueprint.add_url_rule(
            rule, endpoint=endpoint, view_func=handler, methods=methods
        )
    return blueprint
