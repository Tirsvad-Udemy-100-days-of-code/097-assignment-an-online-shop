"""@brief The Basket aggregate and its lines."""

from collections.abc import Mapping
from dataclasses import dataclass

from online_shop import constants
from online_shop.domain.errors import InvalidBasketError, InvalidQuantityError
from online_shop.domain.money import Money


def _check_quantity(quantity: int, minimum: int) -> None:
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise InvalidQuantityError(constants.ERROR_QUANTITY_INVALID)
    if quantity < minimum:
        raise InvalidQuantityError(constants.ERROR_QUANTITY_INVALID)
    if quantity > constants.BASKET_MAX_QUANTITY:
        raise InvalidQuantityError(constants.ERROR_QUANTITY_LIMIT)


@dataclass(frozen=True, slots=True)
class BasketLine:
    """@brief One product in a basket; the price is read from the product.

    @param product_id The key of the product, positive.
    @param quantity The pieces, from BASKET_MIN_QUANTITY to BASKET_MAX_QUANTITY.
    """

    product_id: int
    quantity: int

    def __post_init__(self) -> None:
        """@brief Reject a bad product key or a quantity outside the limits."""
        if self.product_id < 1:
            raise InvalidBasketError(constants.ERROR_PRODUCT_NOT_FOUND)
        _check_quantity(self.quantity, constants.BASKET_MIN_QUANTITY)

    def total(self, unit_price: Money) -> Money:
        """@brief The price of the whole line."""
        return Money(unit_price.cents * self.quantity)


@dataclass(frozen=True, slots=True)
class Basket:
    """@brief The products a user collected; immutable, every change returns a copy.

    @param user_id The owner, positive.
    @param lines The lines, at most one per product, in the order they were added.
    """

    user_id: int
    lines: tuple[BasketLine, ...] = ()

    def __post_init__(self) -> None:
        """@brief Reject an owner without a positive id."""
        if self.user_id < 1:
            raise InvalidBasketError(constants.ERROR_BASKET_INVALID)

    @property
    def item_count(self) -> int:
        """@brief The sum of the quantities of all lines."""
        return sum(line.quantity for line in self.lines)

    def quantity_of(self, product_id: int) -> int:
        """@brief The pieces of a product in the basket, 0 when absent."""
        return next(
            (line.quantity for line in self.lines if line.product_id == product_id),
            0,
        )

    def add(self, product_id: int, quantity: int) -> Basket:
        """@brief Add pieces; an existing line grows.

        @raises InvalidQuantityError When the quantity is below 1 or the line
            would pass the maximum.
        """
        _check_quantity(quantity, constants.BASKET_MIN_QUANTITY)
        return self._with_line(product_id, self.quantity_of(product_id) + quantity)

    def set_quantity(self, product_id: int, quantity: int) -> Basket:
        """@brief Set the pieces of a line; BASKET_REMOVE_QUANTITY removes it.

        @raises InvalidQuantityError When the quantity is outside the limits.
        """
        _check_quantity(quantity, constants.BASKET_REMOVE_QUANTITY)
        return self._with_line(product_id, quantity)

    def remove(self, product_id: int) -> Basket:
        """@brief Drop a line; a product that is not in the basket is ignored."""
        return self._with_line(product_id, constants.BASKET_REMOVE_QUANTITY)

    def total(self, prices: Mapping[int, Money]) -> Money:
        """@brief The sum of price times quantity of the lines with a known price.

        @param prices The unit price per product key; a line without one is skipped.
        """
        return Money(
            sum(
                line.total(prices[line.product_id]).cents
                for line in self.lines
                if line.product_id in prices
            )
        )

    def _with_line(self, product_id: int, quantity: int) -> Basket:
        """Replace, append or drop the line of a product, keeping the order."""
        others = tuple(line for line in self.lines if line.product_id != product_id)
        if quantity == constants.BASKET_REMOVE_QUANTITY:
            return Basket(self.user_id, others)
        new_line = BasketLine(product_id, quantity)
        lines = tuple(
            new_line if line.product_id == product_id else line for line in self.lines
        )
        if new_line in lines:
            return Basket(self.user_id, lines)
        return Basket(self.user_id, (*others, new_line))
