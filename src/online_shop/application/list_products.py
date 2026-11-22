"""@brief The use case that lists the catalog."""

from online_shop.application.dto import ProductDto, to_product_dto
from online_shop.domain.product_repository import ProductRepository


class ListProducts:
    """@brief Returns every product of the catalog."""

    def __init__(self, products: ProductRepository) -> None:
        """@param products The port that reads the catalog."""
        self._products = products

    def execute(self) -> list[ProductDto]:
        """@brief Return all products, ordered by id."""
        return [to_product_dto(product) for product in self._products.list_all()]
