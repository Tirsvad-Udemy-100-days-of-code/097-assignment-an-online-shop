"""@brief The port through which the business keeps orders."""

from datetime import datetime
from typing import Protocol

from online_shop.domain.money import Money
from online_shop.domain.order import Order, OrderLine, OrderStatus


class OrderRepository(Protocol):
    """@brief Stores orders; an adapter implements it."""

    def add(
        self,
        user_id: int,
        stripe_session_id: str,
        total: Money,
        currency: str,
        created_at: datetime,
        lines: tuple[OrderLine, ...],
    ) -> Order:
        """@brief Store a new order at the end of Needs confirmation; return it.

        @raises DuplicateOrderError When the payment session has an order.
        """
        ...

    def get_by_session(self, stripe_session_id: str) -> Order | None:
        """@brief Return the order of a payment session, or None."""
        ...

    def list_board(self) -> list[Order]:
        """@brief Return every order, each status in position order."""
        ...

    def list_for_user(self, user_id: int) -> list[Order]:
        """@brief Return the orders of one user, newest first."""
        ...

    def move(self, order_id: int, status: OrderStatus, index: int) -> bool:
        """@brief Put an order in a column at an index and renumber the columns.

        The source and target columns are renumbered together, all or nothing.

        @return False when no order has this id, else True.
        """
        ...
