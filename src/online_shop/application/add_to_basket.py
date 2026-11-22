"""@brief The use case that puts a product into the basket of a user."""

from online_shop import constants
from online_shop.application.errors import ProductNotFoundError
from online_shop.domain.basket_repository import BasketRepository
from online_shop.domain.product_repository import ProductRepository


class AddToBasket:
    """@brief Adds pieces of a product; adding it again increases the quantity."""

    def __init__(self, baskets: BasketRepository, products: ProductRepository) -> None:
        """@param baskets The basket store.  @param products The catalog."""
        self._baskets = baskets
        self._products = products

    def execute(
        self,
        user_id: int,
        product_id: int,
        quantity: int = constants.BASKET_DEFAULT_ADD_QUANTITY,
    ) -> None:
        """@brief Add the product to the basket of the user.

        @raises ProductNotFoundError When no product has this id.
        @raises InvalidQuantityError When the quantity or the new line total
            is outside the limits.
        """
        if self._products.get(product_id) is None:
            raise ProductNotFoundError(product_id)
        basket = self._baskets.get(user_id).add(product_id, quantity)
        self._baskets.save(basket)
