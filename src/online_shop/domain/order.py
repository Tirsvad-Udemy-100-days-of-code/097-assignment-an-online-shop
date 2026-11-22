"""@brief The Order entity, its status and its lines."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from online_shop import constants
from online_shop.domain.errors import InvalidOrderError
from online_shop.domain.money import Money


class OrderStatus(StrEnum):
    """@brief Where an order is on its way to the customer."""

    NEEDS_CONFIRMATION = "Needs confirmation"
    CONFIRMED = "Confirmed"
    BEING_PACKED = "Being packed"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"


@dataclass(frozen=True, slots=True)
class OrderLine:
    """@brief What was bought, copied at the time of the order.

    @param product_name The product name then.
    @param unit_price The price of one piece then.
    @param quantity The pieces, at least one.
    """

    product_name: str
    unit_price: Money
    quantity: int

    def __post_init__(self) -> None:
        """@brief Reject a blank name or a quantity below one."""
        if not self.product_name.strip() or self.quantity < 1:
            raise InvalidOrderError(constants.ERROR_ORDER_INVALID)

    def total(self) -> Money:
        """@brief The price of the whole line."""
        return Money(self.unit_price.cents * self.quantity)


@dataclass(frozen=True, slots=True)
class Order:
    """@brief A paid order.

    @param id The unique key of the order, positive.
    @param user_id The customer, positive.
    @param status The step the order is in.
    @param stripe_session_id The payment session that paid it; one order each.
    @param total The amount paid.
    @param currency The lower case ISO currency code of the payment.
    @param created_at When the order was made; timezone aware.
    @param lines The lines as bought.
    @param position Place inside the status column of the board, from 0.
    """

    id: int
    user_id: int
    status: OrderStatus
    stripe_session_id: str
    total: Money
    currency: str
    created_at: datetime
    lines: tuple[OrderLine, ...] = ()
    position: int = 0

    def __post_init__(self) -> None:
        """@brief Reject bad keys, a blank payment reference or a naive time."""
        if (
            self.id < 1
            or self.position < 0
            or self.user_id < 1
            or not self.stripe_session_id.strip()
            or not self.currency.strip()
            or self.created_at.tzinfo is None
        ):
            raise InvalidOrderError(constants.ERROR_ORDER_INVALID)
