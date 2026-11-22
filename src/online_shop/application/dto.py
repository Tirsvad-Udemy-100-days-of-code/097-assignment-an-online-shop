"""@brief The plain data the use cases hand to the presentation layer."""

from dataclasses import dataclass
from datetime import datetime

from online_shop.domain.order import Order
from online_shop.domain.product import Product
from online_shop.domain.user import User, UserRole


@dataclass(frozen=True, slots=True)
class ProductDto:
    """@brief A product as the presentation layer sees it.

    @param id The key of the product.
    @param name The name shown to the customer.
    @param description The text that describes the product.
    @param price_cents The price in cents.
    @param image The file name of the product image.
    """

    id: int
    name: str
    description: str
    price_cents: int
    image: str


def to_product_dto(product: Product) -> ProductDto:
    """@brief Map a product entity to its DTO."""
    return ProductDto(
        product.id,
        product.name,
        product.description,
        product.price.cents,
        product.image,
    )


@dataclass(frozen=True, slots=True)
class UserDto:
    """@brief A user as the presentation layer sees it; no password hash.

    @param id The key of the user.
    @param email The normalized email address.
    @param role The role as text, "customer" or "admin".
    """

    id: int
    email: str
    role: str

    @property
    def is_admin(self) -> bool:
        """@brief True when the user has the admin role."""
        return self.role == UserRole.ADMIN


def to_user_dto(user: User) -> UserDto:
    """@brief Map a user entity to its DTO, leaving the hash behind."""
    return UserDto(user.id, user.email, user.role.value)


@dataclass(frozen=True, slots=True)
class BasketLineDto:
    """@brief A basket line with the product data read at view time.

    @param product_id The key of the product.
    @param name The product name.
    @param image The file name of the product image.
    @param unit_price_cents The price of one piece in cents.
    @param quantity The pieces in the basket.
    @param line_total_cents Unit price times quantity, in cents.
    """

    product_id: int
    name: str
    image: str
    unit_price_cents: int
    quantity: int
    line_total_cents: int


@dataclass(frozen=True, slots=True)
class BasketDto:
    """@brief A basket as the presentation layer sees it.

    @param lines The lines whose product still exists.
    @param total_cents The sum of the line totals in cents.
    @param item_count The sum of the quantities of the listed lines.
    @param unavailable_count The lines skipped because their product vanished.
    """

    lines: tuple[BasketLineDto, ...]
    total_cents: int
    item_count: int
    unavailable_count: int


@dataclass(frozen=True, slots=True)
class OrderLineDto:
    """@brief An order line as bought: name, price of one piece in cents, pieces."""

    product_name: str
    unit_price_cents: int
    quantity: int


@dataclass(frozen=True, slots=True)
class OrderDto:
    """@brief An order as the presentation layer sees it.

    @param id The order number.
    @param status The status as text.
    @param total_cents The amount paid in cents.
    @param currency The lower case ISO currency code.
    @param lines The lines as bought.
    @param created_at When the order was made; timezone aware.
    """

    id: int
    status: str
    total_cents: int
    currency: str
    lines: tuple[OrderLineDto, ...]
    created_at: datetime


def to_order_dto(order: Order) -> OrderDto:
    """@brief Map an order entity to its DTO."""
    return OrderDto(
        order.id,
        order.status.value,
        order.total.cents,
        order.currency,
        tuple(
            OrderLineDto(line.product_name, line.unit_price.cents, line.quantity)
            for line in order.lines
        ),
        order.created_at,
    )


@dataclass(frozen=True, slots=True)
class BoardCardDto:
    """@brief An order card of the board.

    @param order_id The order number.
    @param customer_email The email of the customer, or a label when removed.
    @param items One text per line, for example "2 x Mug".
    @param total_cents The amount paid in cents.
    @param created_at When the order was made.
    """

    order_id: int
    customer_email: str
    items: tuple[str, ...]
    total_cents: int
    created_at: datetime


@dataclass(frozen=True, slots=True)
class BoardColumnDto:
    """@brief One board column: a status and its cards in position order."""

    status: str
    cards: tuple[BoardCardDto, ...]


@dataclass(frozen=True, slots=True)
class BoardDto:
    """@brief The whole board: one column per status, in the order of the flow."""

    columns: tuple[BoardColumnDto, ...]
