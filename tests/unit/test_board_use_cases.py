"""Tests of the board rule and the board use cases with fakes of every port."""

from datetime import UTC, datetime, timedelta

import pytest

from fakes import FakeOrderRepository, FakeUserRepository
from online_shop import constants
from online_shop.application.errors import InvalidMoveError, OrderNotFoundError
from online_shop.application.list_my_orders import ListMyOrders
from online_shop.application.move_order import MoveOrder
from online_shop.application.view_board import ViewBoard
from online_shop.domain.board_placement import place_order
from online_shop.domain.errors import InvalidOrderError
from online_shop.domain.money import Money
from online_shop.domain.order import Order, OrderLine, OrderStatus
from online_shop.domain.user import UserRole

NOW = datetime(2026, 3, 4, 5, 6, tzinfo=UTC)
NEW = OrderStatus.NEEDS_CONFIRMATION
CONFIRMED = OrderStatus.CONFIRMED
SHIPPED = OrderStatus.SHIPPED
LINES = (OrderLine("Mug", Money(1200), 2), OrderLine("Lamp", Money(3490), 1))


class Shop:
    def __init__(self) -> None:
        self.orders = FakeOrderRepository()
        self.users = FakeUserRepository()
        self.users.add("ann@example.com", "h", UserRole.CUSTOMER)
        self.users.add("bob@example.com", "h", UserRole.CUSTOMER)
        self.move = MoveOrder(self.orders)
        self.view = ViewBoard(self.orders, self.users)

    def order(self, user_id: int = 1, minutes: int = 0) -> Order:
        number = len(self.orders.orders) + 1
        return self.orders.add(
            user_id,
            f"cs_{number}",
            Money(5890),
            "eur",
            NOW + timedelta(minutes=minutes),
            LINES,
        )

    def ids(self, status: OrderStatus) -> list[int]:
        column = next(c for c in self.view.execute().columns if c.status == status)
        return [card.order_id for card in column.cards]


def test_place_order_inserts_into_another_column_and_closes_the_gap() -> None:
    columns = {NEW: [1, 2, 3], CONFIRMED: [4, 5]}
    placed = place_order(columns, 2, CONFIRMED, 1)
    assert placed == {NEW: [1, 3], CONFIRMED: [4, 2, 5]}
    assert columns == {NEW: [1, 2, 3], CONFIRMED: [4, 5]}


@pytest.mark.parametrize(
    ("index", "expected"),
    [(0, [3, 1, 2]), (1, [1, 3, 2]), (2, [1, 2, 3]), (99, [1, 2, 3]), (-5, [3, 1, 2])],
)
def test_place_order_inside_a_column_counts_without_the_moved_card(
    index: int, expected: list[int]
) -> None:
    assert place_order({NEW: [1, 2, 3]}, 3, NEW, index) == {NEW: expected}


def test_place_order_creates_a_missing_target_column() -> None:
    assert place_order({NEW: [1]}, 1, SHIPPED, 0) == {NEW: [], SHIPPED: [1]}


def test_new_orders_go_to_the_end_of_needs_confirmation() -> None:
    shop = Shop()
    first, second = shop.order(), shop.order()
    assert (first.position, second.position) == (0, 1)
    assert shop.ids(NEW) == [1, 2]


def test_move_to_another_column_renumbers_both_columns() -> None:
    shop = Shop()
    for _ in range(3):
        shop.order()
    shop.move.execute(1, CONFIRMED.value, 0)
    shop.move.execute(2, CONFIRMED.value, 0)
    assert shop.ids(CONFIRMED) == [2, 1]
    assert shop.ids(NEW) == [3]
    assert [o.position for o in shop.orders.list_board() if o.status is NEW] == [0]
    assert sorted(o.position for o in shop.orders.orders) == [0, 0, 1]


def test_move_may_skip_steps_and_reopen_an_order() -> None:
    shop = Shop()
    shop.order()
    shop.move.execute(1, OrderStatus.DELIVERED.value, 0)
    assert shop.ids(OrderStatus.DELIVERED) == [1]
    shop.move.execute(1, NEW.value, 5)
    assert shop.ids(NEW) == [1]


def test_move_within_a_column_changes_the_order() -> None:
    shop = Shop()
    for _ in range(3):
        shop.order()
    shop.move.execute(1, NEW.value, 2)
    assert shop.ids(NEW) == [2, 3, 1]


def test_move_of_an_unknown_order_is_not_found() -> None:
    with pytest.raises(OrderNotFoundError):
        Shop().move.execute(9, CONFIRMED.value, 0)


@pytest.mark.parametrize(("status", "index"), [("Lost", 0), ("", 0), ("Shipped", -1)])
def test_move_with_bad_input_is_a_validation_error(status: str, index: int) -> None:
    shop = Shop()
    shop.order()
    with pytest.raises(InvalidMoveError):
        shop.move.execute(1, status, index)
    assert shop.ids(NEW) == [1]


def test_board_has_five_columns_in_the_order_of_the_flow() -> None:
    columns = Shop().view.execute().columns
    assert [c.status for c in columns] == [s.value for s in OrderStatus]
    assert all(c.cards == () for c in columns)


def test_board_cards_carry_customer_items_total_and_time() -> None:
    shop = Shop()
    shop.order(2)
    card = shop.view.execute().columns[0].cards[0]
    assert card.order_id == 1
    assert card.customer_email == "bob@example.com"
    assert card.items == ("2 x Mug", "1 x Lamp")
    assert card.total_cents == 5890
    assert card.created_at == NOW


def test_board_labels_a_customer_that_was_removed() -> None:
    shop = Shop()
    shop.order(7)
    card = shop.view.execute().columns[0].cards[0]
    assert card.customer_email == constants.UNKNOWN_CUSTOMER


def test_list_my_orders_shows_only_own_orders_newest_first() -> None:
    shop = Shop()
    shop.order(1, 0)
    shop.order(2, 5)
    shop.order(1, 10)
    shop.move.execute(1, SHIPPED.value, 0)
    mine = ListMyOrders(shop.orders).execute(1)
    assert [o.id for o in mine] == [3, 1]
    assert [o.status for o in mine] == [NEW.value, SHIPPED.value]
    assert mine[0].lines[0].product_name == "Mug"
    assert mine[0].total_cents == 5890
    assert ListMyOrders(shop.orders).execute(5) == ()


def test_order_rejects_a_negative_position() -> None:
    with pytest.raises(InvalidOrderError):
        Order(1, 1, NEW, "cs", Money(1), "eur", NOW, (), -1)
