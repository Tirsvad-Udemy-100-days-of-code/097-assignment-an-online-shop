"""@brief The port through which the business keeps orders."""

from datetime import datetime
from typing import Protocol

from online_shop.domain.money import Money
from online_shop.domain.order import Order, OrderLine


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
        """@brief Store a new order that needs confirmation and return it.

        @raises DuplicateOrderError When the payment session has an order.
        """
        ...

    def get_by_session(self, stripe_session_id: str) -> Order | None:
        """@brief Return the order of a payment session, or None."""
        ...
