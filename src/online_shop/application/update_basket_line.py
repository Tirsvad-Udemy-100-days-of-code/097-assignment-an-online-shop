"""@brief The use case that sets the quantity of a basket line."""

from online_shop.application.errors import ProductNotFoundError
from online_shop.domain.basket_repository import BasketRepository
from online_shop.domain.product_repository import ProductRepository


class UpdateBasketLine:
    """@brief Sets the pieces of a product; zero removes the line."""

    def __init__(self, baskets: BasketRepository, products: ProductRepository) -> None:
        """@param baskets The basket store.  @param products The catalog."""
        self._baskets = baskets
        self._products = products

    def execute(self, user_id: int, product_id: int, quantity: int) -> None:
        """@brief Set the quantity of the product in the basket of the user.

        @raises ProductNotFoundError When no product has this id.
        @raises InvalidQuantityError When the quantity is outside the limits.
        """
        if self._products.get(product_id) is None:
            raise ProductNotFoundError(product_id)
        basket = self._baskets.get(user_id).set_quantity(product_id, quantity)
        self._baskets.save(basket)
