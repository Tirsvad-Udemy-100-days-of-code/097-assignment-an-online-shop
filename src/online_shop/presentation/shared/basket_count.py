"""@brief The basket item count of the signed-in user, for the header."""

from online_shop.application.count_basket_items import CountBasketItems
from online_shop.presentation.shared.session import SessionManager


class BasketCount:
    """@brief Supplies `basket_count` to every template."""

    def __init__(self, count_items: CountBasketItems, sessions: SessionManager) -> None:
        """@param count_items The use case.  @param sessions The session."""
        self._count_items = count_items
        self._sessions = sessions

    def template_context(self) -> dict[str, object]:
        """@brief The pieces in the basket; 0 for an anonymous visitor."""
        user_id = self._sessions.user_id()
        count = 0 if user_id is None else self._count_items.execute(user_id)
        return {"basket_count": count}
