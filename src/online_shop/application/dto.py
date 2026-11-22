"""@brief The plain data the use cases hand to the presentation layer."""

from dataclasses import dataclass

from online_shop.domain.product import Product


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
