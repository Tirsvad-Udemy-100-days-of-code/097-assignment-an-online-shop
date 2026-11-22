"""@brief The SQLite adapter of the OrderRepository port."""

import sqlite3
from collections import defaultdict
from contextlib import closing
from datetime import datetime
from pathlib import Path

from online_shop.domain.board_placement import place_order
from online_shop.domain.errors import DuplicateOrderError
from online_shop.domain.money import Money
from online_shop.domain.order import Order, OrderLine, OrderStatus
from online_shop.infrastructure.database import connect

_INSERT_ORDER = (
    "INSERT INTO orders (user_id, status, stripe_session_id, total_cents, currency,"
    " created_at, position) VALUES (?, ?, ?, ?, ?, ?,"
    " (SELECT COALESCE(MAX(position) + 1, 0) FROM orders WHERE status = ?))"
)
_INSERT_LINE = (
    "INSERT INTO order_lines (order_id, product_name, unit_price_cents, quantity)"
    " VALUES (?, ?, ?, ?)"
)
_SELECT_POSITION = "SELECT position FROM orders WHERE id = ?"
_SELECT_BY_SESSION = (
    "SELECT id, user_id, status, stripe_session_id, total_cents, currency,"
    " created_at, position FROM orders WHERE stripe_session_id = ?"
)
_SELECT_BOARD = (
    "SELECT id, user_id, status, stripe_session_id, total_cents, currency,"
    " created_at, position FROM orders ORDER BY position, id"
)
_SELECT_FOR_USER = (
    "SELECT id, user_id, status, stripe_session_id, total_cents, currency,"
    " created_at, position FROM orders WHERE user_id = ?"
    " ORDER BY created_at DESC, id DESC"
)
_SELECT_ALL_LINES = (
    "SELECT order_id, product_name, unit_price_cents, quantity FROM order_lines"
    " ORDER BY id"
)
_SELECT_ORDER_LINES = (
    "SELECT order_id, product_name, unit_price_cents, quantity FROM order_lines"
    " WHERE order_id = ? ORDER BY id"
)
_SELECT_PLACES = "SELECT id, status FROM orders ORDER BY position, id"
_UPDATE_PLACE = "UPDATE orders SET status = ?, position = ? WHERE id = ?"
_DUPLICATE_COLUMN = "orders.stripe_session_id"


def _to_order(row: tuple[object, ...], lines: tuple[OrderLine, ...]) -> Order:
    return Order(
        int(str(row[0])),
        int(str(row[1])),
        OrderStatus(str(row[2])),
        str(row[3]),
        Money(int(str(row[4]))),
        str(row[5]),
        datetime.fromisoformat(str(row[6])),
        lines,
        int(str(row[7])),
    )


def _lines_by_order(
    connection: sqlite3.Connection, only_order: int | None = None
) -> dict[int, list[OrderLine]]:
    """The lines of every order, or of one, grouped by order id."""
    grouped: dict[int, list[OrderLine]] = defaultdict(list)
    if only_order is None:
        found = connection.execute(_SELECT_ALL_LINES)
    else:
        found = connection.execute(_SELECT_ORDER_LINES, (only_order,))
    for order_id, name, price, quantity in found:
        grouped[order_id].append(OrderLine(name, Money(price), quantity))
    return grouped


class SqliteOrderRepository:
    """@brief Keeps orders in a SQLite file; one connection per call."""

    def __init__(self, database_path: Path) -> None:
        """@param database_path The SQLite file, already migrated."""
        self._database_path = database_path

    def add(
        self,
        user_id: int,
        stripe_session_id: str,
        total: Money,
        currency: str,
        created_at: datetime,
        lines: tuple[OrderLine, ...],
    ) -> Order:
        """@brief Store the order and its lines in one transaction."""
        status = OrderStatus.NEEDS_CONFIRMATION
        try:
            with closing(connect(self._database_path)) as connection, connection:
                cursor = connection.execute(
                    _INSERT_ORDER,
                    (
                        user_id,
                        status.value,
                        stripe_session_id,
                        total.cents,
                        currency,
                        created_at.isoformat(),
                        status.value,
                    ),
                )
                order_id = int(cursor.lastrowid or 0)
                connection.executemany(
                    _INSERT_LINE,
                    [
                        (
                            order_id,
                            line.product_name,
                            line.unit_price.cents,
                            line.quantity,
                        )
                        for line in lines
                    ],
                )
                position = int(
                    connection.execute(_SELECT_POSITION, (order_id,)).fetchone()[0]
                )
        except sqlite3.IntegrityError as error:
            if _DUPLICATE_COLUMN in str(error):
                raise DuplicateOrderError(stripe_session_id) from None
            raise
        return Order(
            order_id,
            user_id,
            status,
            stripe_session_id,
            total,
            currency,
            created_at,
            lines,
            position,
        )

    def get_by_session(self, stripe_session_id: str) -> Order | None:
        """@brief Return the order of a payment session, or None."""
        with closing(connect(self._database_path)) as connection:
            row = connection.execute(_SELECT_BY_SESSION, (stripe_session_id,))
            found = row.fetchone()
            if found is None:
                return None
            lines = _lines_by_order(connection, found[0]).get(found[0], [])
        return _to_order(found, tuple(lines))

    def list_board(self) -> list[Order]:
        """@brief Return every order in position order."""
        return self._list(_SELECT_BOARD, ())

    def list_for_user(self, user_id: int) -> list[Order]:
        """@brief Return the orders of one user, newest first."""
        return self._list(_SELECT_FOR_USER, (user_id,))

    def move(self, order_id: int, status: OrderStatus, index: int) -> bool:
        """@brief Place the order and renumber both columns in one transaction."""
        with closing(connect(self._database_path)) as connection, connection:
            # BEGIN IMMEDIATE takes the write lock before reading, so two moves
            # cannot both renumber from the same old state.
            connection.execute("BEGIN IMMEDIATE")
            columns: dict[OrderStatus, list[int]] = {s: [] for s in OrderStatus}
            source: OrderStatus | None = None
            for found_id, found_status in connection.execute(_SELECT_PLACES):
                columns[OrderStatus(found_status)].append(found_id)
                if found_id == order_id:
                    source = OrderStatus(found_status)
            if source is None:
                return False
            placed = place_order(columns, order_id, status, index)
            connection.executemany(
                _UPDATE_PLACE,
                [
                    (column.value, position, placed_id)
                    for column in {source, status}
                    for position, placed_id in enumerate(placed[column])
                ],
            )
        return True

    def _list(self, query: str, parameters: tuple[int, ...]) -> list[Order]:
        with closing(connect(self._database_path)) as connection:
            rows = connection.execute(query, parameters).fetchall()
            lines = _lines_by_order(connection)
        return [_to_order(row, tuple(lines.get(row[0], []))) for row in rows]
