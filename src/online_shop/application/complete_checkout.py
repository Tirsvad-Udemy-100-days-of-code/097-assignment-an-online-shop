"""@brief The use case that turns a paid payment session into an order."""

from collections.abc import Callable
from datetime import UTC, datetime

from online_shop import constants
from online_shop.application.dto import OrderDto, to_order_dto
from online_shop.application.errors import (
    ForeignPaymentError,
    PaymentNotCompletedError,
)
from online_shop.application.payment_gateway import PaymentGateway
from online_shop.domain.basket import Basket
from online_shop.domain.basket_repository import BasketRepository
from online_shop.domain.errors import DuplicateOrderError
from online_shop.domain.money import Money
from online_shop.domain.order import Order, OrderLine
from online_shop.domain.order_repository import OrderRepository
from online_shop.domain.product_repository import ProductRepository


def _utc_now() -> datetime:
    return datetime.now(UTC)


class CompleteCheckout:
    """@brief Reads the session back; only a paid one makes an order."""

    def __init__(
        self,
        baskets: BasketRepository,
        products: ProductRepository,
        orders: OrderRepository,
        payments: PaymentGateway,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        """@param baskets The basket store.  @param products The catalog.
        @param orders The order store.  @param payments The payment gateway.
        @param clock Gives the current time; replaced in tests.
        """
        self._baskets = baskets
        self._products = products
        self._orders = orders
        self._payments = payments
        self._clock = clock

    def execute(self, user_id: int, session_id: str) -> OrderDto:
        """@brief Create the order of a paid session, once per session.

        The basket is copied into the order and emptied only after the order
        is saved. Asking again for the same session returns the same order.

        @raises PaymentNotCompletedError When the session is missing or unpaid.
        @raises ForeignPaymentError When the session belongs to another user.
        @raises PaymentGatewayError When the provider fails.
        """
        if not session_id.strip():
            raise PaymentNotCompletedError(constants.ERROR_CHECKOUT_SESSION_MISSING)
        existing = self._orders.get_by_session(session_id)
        if existing is not None:
            return self._owned(existing, user_id)
        result = self._payments.retrieve_session(session_id)
        if result.client_reference_id != str(user_id):
            raise ForeignPaymentError(constants.ERROR_CHECKOUT_FOREIGN)
        if not result.paid:
            raise PaymentNotCompletedError(constants.ERROR_CHECKOUT_NOT_PAID)
        try:
            order = self._orders.add(
                user_id,
                session_id,
                Money(result.amount_total),
                result.currency,
                self._clock(),
                self._snapshot(user_id),
            )
        except DuplicateOrderError:
            # A second request for the same session won the race to save it.
            raced = self._orders.get_by_session(session_id)
            if raced is None:
                raise
            return self._owned(raced, user_id)
        self._baskets.save(Basket(user_id))
        return to_order_dto(order)

    @staticmethod
    def _owned(order: Order, user_id: int) -> OrderDto:
        if order.user_id != user_id:
            raise ForeignPaymentError(constants.ERROR_CHECKOUT_FOREIGN)
        return to_order_dto(order)

    def _snapshot(self, user_id: int) -> tuple[OrderLine, ...]:
        lines: list[OrderLine] = []
        for line in self._baskets.get(user_id).lines:
            product = self._products.get(line.product_id)
            if product is not None:
                lines.append(OrderLine(product.name, product.price, line.quantity))
        return tuple(lines)
