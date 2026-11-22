"""@brief The use case that shows the order board."""

from online_shop import constants
from online_shop.application.dto import BoardCardDto, BoardColumnDto, BoardDto
from online_shop.domain.order import Order, OrderStatus
from online_shop.domain.order_repository import OrderRepository
from online_shop.domain.user_repository import UserRepository


def item_summary(order: Order) -> tuple[str, ...]:
    """@brief One text per order line, for example "2 x Mug"."""
    return tuple(
        constants.ORDER_ITEM_FORMAT.format(
            quantity=line.quantity, name=line.product_name
        )
        for line in order.lines
    )


class ViewBoard:
    """@brief Builds the five columns with the cards of the orders."""

    def __init__(self, orders: OrderRepository, users: UserRepository) -> None:
        """@param orders The order store.  @param users The user store."""
        self._orders = orders
        self._users = users

    def execute(self) -> BoardDto:
        """@brief Return one column per status, cards in position order."""
        emails: dict[int, str] = {}
        cards: dict[OrderStatus, list[BoardCardDto]] = {s: [] for s in OrderStatus}
        for order in self._orders.list_board():
            if order.user_id not in emails:
                user = self._users.get(order.user_id)
                emails[order.user_id] = (
                    constants.UNKNOWN_CUSTOMER if user is None else user.email
                )
            cards[order.status].append(
                BoardCardDto(
                    order.id,
                    emails[order.user_id],
                    item_summary(order),
                    order.total.cents,
                    order.created_at,
                )
            )
        return BoardDto(
            tuple(BoardColumnDto(s.value, tuple(cards[s])) for s in OrderStatus)
        )
