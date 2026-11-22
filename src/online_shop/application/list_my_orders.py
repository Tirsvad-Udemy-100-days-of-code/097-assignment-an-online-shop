"""@brief The use case that lists the orders of one customer."""

from online_shop.application.dto import OrderDto, to_order_dto
from online_shop.domain.order_repository import OrderRepository


class ListMyOrders:
    """@brief Returns the orders of one user, newest first."""

    def __init__(self, orders: OrderRepository) -> None:
        """@param orders The order store."""
        self._orders = orders

    def execute(self, user_id: int) -> tuple[OrderDto, ...]:
        """@brief Return only this user's orders, with lines, total and status."""
        return tuple(
            to_order_dto(order) for order in self._orders.list_for_user(user_id)
        )
