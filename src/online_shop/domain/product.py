"""@brief The Product entity."""

from dataclasses import dataclass

from online_shop.domain.errors import InvalidProductError
from online_shop.domain.money import Money


@dataclass(frozen=True, slots=True)
class Product:
    """@brief An item the shop sells.

    @param id The unique key of the product, positive.
    @param name The name shown to the customer; not blank.
    @param description The text that describes the product.
    @param price The price of one piece.
    @param image The file name of the product image.
    """

    id: int
    name: str
    description: str
    price: Money
    image: str

    def __post_init__(self) -> None:
        """@brief Reject a product without a positive id or without a name."""
        if self.id < 1:
            raise InvalidProductError("A product id must be positive.")
        if not self.name.strip():
            raise InvalidProductError("A product needs a name.")
