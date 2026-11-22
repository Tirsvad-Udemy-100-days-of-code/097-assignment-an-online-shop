"""@brief The use case for a customer who left the payment page."""

import logging

from online_shop.domain.basket_repository import BasketRepository

_LOG = logging.getLogger(__name__)


class CancelCheckout:
    """@brief Keeps the basket as it was and creates no order."""

    def __init__(self, baskets: BasketRepository) -> None:
        """@param baskets The basket store."""
        self._baskets = baskets

    def execute(self, user_id: int) -> int:
        """@brief Note the cancellation.

        @return The pieces still in the basket.
        """
        _LOG.info("Checkout cancelled by user %s; the basket is kept.", user_id)
        return self._baskets.get(user_id).item_count
