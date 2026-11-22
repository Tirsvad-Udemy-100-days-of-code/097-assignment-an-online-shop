"""@brief The use case that moves an order card to a column and place."""

from online_shop import constants
from online_shop.application.errors import InvalidMoveError, OrderNotFoundError
from online_shop.domain.order import OrderStatus
from online_shop.domain.order_repository import OrderRepository


class MoveOrder:
    """@brief Puts an order in any column at any place, as the owner decides."""

    def __init__(self, orders: OrderRepository) -> None:
        """@param orders The order store."""
        self._orders = orders

    def execute(self, order_id: int, status: str, index: int) -> None:
        """@brief Move the order; the columns it leaves and enters are renumbered.

        @param order_id The order to move.
        @param status The label of the target column.
        @param index The place in the target column, from 0; a large value
            means last.
        @raises InvalidMoveError When the status or the index is not valid.
        @raises OrderNotFoundError When no order has this id.
        """
        try:
            target = OrderStatus(status)
        except ValueError:
            raise InvalidMoveError(constants.ERROR_MOVE_STATUS) from None
        if index < 0:
            raise InvalidMoveError(constants.ERROR_MOVE_INDEX)
        if not self._orders.move(order_id, target, index):
            raise OrderNotFoundError(constants.ERROR_ORDER_NOT_FOUND)
