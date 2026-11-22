"""@brief The use case that removes a product from the basket."""

from online_shop.domain.basket_repository import BasketRepository


class RemoveFromBasket:
    """@brief Drops a line; a product that is not in the basket is ignored."""

    def __init__(self, baskets: BasketRepository) -> None:
        """@param baskets The basket store."""
        self._baskets = baskets

    def execute(self, user_id: int, product_id: int) -> None:
        """@brief Remove the product from the basket of the user."""
        self._baskets.save(self._baskets.get(user_id).remove(product_id))
