"""@brief The use case that counts the pieces in a basket."""

from online_shop.domain.basket_repository import BasketRepository


class CountBasketItems:
    """@brief Returns the sum of the quantities of a basket."""

    def __init__(self, baskets: BasketRepository) -> None:
        """@param baskets The basket store."""
        self._baskets = baskets

    def execute(self, user_id: int) -> int:
        """@brief Return the pieces in the basket of the user."""
        return self._baskets.get(user_id).item_count
