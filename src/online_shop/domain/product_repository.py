"""@brief The port through which the business reads products."""

from typing import Protocol

from online_shop.domain.product import Product


class ProductRepository(Protocol):
    """@brief Reads the product catalog; an adapter implements it."""

    def list_all(self) -> list[Product]:
        """@brief Return every product, ordered by id."""
        ...

    def get(self, product_id: int) -> Product | None:
        """@brief Return one product, or None when no product has this id."""
        ...
