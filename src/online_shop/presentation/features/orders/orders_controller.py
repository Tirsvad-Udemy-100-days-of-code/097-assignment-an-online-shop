"""@brief The controller of the customer's order history."""

from http import HTTPStatus

from flask import Blueprint, redirect, render_template, url_for
from flask.typing import ResponseReturnValue

from online_shop import constants
from online_shop.application.list_my_orders import ListMyOrders
from online_shop.presentation.shared.current_user import CurrentUser


class OrdersController:
    """@brief Shows the signed-in customer's own orders."""

    def __init__(self, current_user: CurrentUser, list_orders: ListMyOrders) -> None:
        """@param current_user The signed-in user.  @param list_orders The use case."""
        self._current_user = current_user
        self._list_orders = list_orders

    def index(self) -> ResponseReturnValue:
        """@brief The order list; anonymous goes to login and back."""
        user = self._current_user.get()
        if user is None:
            return redirect(
                url_for("auth.login", next=url_for("orders.index")),
                HTTPStatus.SEE_OTHER,
            )
        return render_template(
            "orders/index.html",
            title=constants.TEXT_ORDERS_TITLE,
            orders=self._list_orders.execute(user.id),
            texts={
                "heading": constants.TEXT_ORDERS_TITLE,
                "empty": constants.TEXT_ORDERS_EMPTY,
                "number": constants.TEXT_CHECKOUT_ORDER_NUMBER,
                "date": constants.TEXT_ORDERS_DATE,
                "total": constants.TEXT_BASKET_TOTAL,
                "continue": constants.TEXT_BASKET_CONTINUE,
            },
        )


def create_orders_blueprint(
    current_user: CurrentUser, list_orders: ListMyOrders
) -> Blueprint:
    """@brief Build the blueprint "orders" with the route "/orders"."""
    blueprint = Blueprint("orders", __name__)
    controller = OrdersController(current_user, list_orders)
    blueprint.add_url_rule(
        "/orders", endpoint="index", view_func=controller.index, methods=["GET"]
    )
    return blueprint
