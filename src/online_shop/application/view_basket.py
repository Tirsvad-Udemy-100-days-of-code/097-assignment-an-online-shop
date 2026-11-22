"""@brief The use case that shows a basket with prices and totals."""

from online_shop.application.dto import BasketDto, BasketLineDto
from online_shop.domain.basket_repository import BasketRepository
from online_shop.domain.product import Product
from online_shop.domain.product_repository import ProductRepository


class ViewBasket:
    """@brief Joins the basket with the products it holds, at today's prices."""

    def __init__(self, baskets: BasketRepository, products: ProductRepository) -> None:
        """@param baskets The basket store.  @param products The catalog."""
        self._baskets = baskets
        self._products = products

    def execute(self, user_id: int) -> BasketDto:
        """@brief Return the lines, their totals and the basket total.

        A line whose product no longer exists is left out and counted.
        """
        basket = self._baskets.get(user_id)
        found: dict[int, Product] = {}
        for line in basket.lines:
            product = self._products.get(line.product_id)
            if product is not None:
                found[line.product_id] = product
        lines = tuple(
            BasketLineDto(
                line.product_id,
                found[line.product_id].name,
                found[line.product_id].image,
                found[line.product_id].price.cents,
                line.quantity,
                line.total(found[line.product_id].price).cents,
            )
            for line in basket.lines
            if line.product_id in found
        )
        total = basket.total({key: product.price for key, product in found.items()})
        return BasketDto(
            lines,
            total.cents,
            sum(line.quantity for line in lines),
            len(basket.lines) - len(lines),
        )
