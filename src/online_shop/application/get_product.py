"""@brief The use case that fetches one product."""

from online_shop.application.dto import ProductDto, to_product_dto
from online_shop.application.errors import ProductNotFoundError
from online_shop.domain.product_repository import ProductRepository


class GetProduct:
    """@brief Returns one product of the catalog."""

    def __init__(self, products: ProductRepository) -> None:
        """@param products The port that reads the catalog."""
        self._products = products

    def execute(self, product_id: int) -> ProductDto:
        """@brief Return the product with this id.

        @param product_id The key of the product.
        @raises ProductNotFoundError When no product has this id.
        """
        product = self._products.get(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return to_product_dto(product)
