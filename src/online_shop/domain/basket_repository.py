"""@brief The port through which the business keeps baskets."""

from typing import Protocol

from online_shop.domain.basket import Basket


class BasketRepository(Protocol):
    """@brief Stores one basket per user; an adapter implements it."""

    def get(self, user_id: int) -> Basket:
        """@brief Return the basket of the user; empty when none was saved."""
        ...

    def save(self, basket: Basket) -> None:
        """@brief Replace the stored basket of its owner."""
        ...
