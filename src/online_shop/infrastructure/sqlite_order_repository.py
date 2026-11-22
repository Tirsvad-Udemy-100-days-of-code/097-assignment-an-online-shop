"""@brief The SQLite adapter of the OrderRepository port."""

import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

from online_shop.domain.errors import DuplicateOrderError
from online_shop.domain.money import Money
from online_shop.domain.order import Order, OrderLine, OrderStatus
from online_shop.infrastructure.database import connect

_INSERT_ORDER = (
    "INSERT INTO orders (user_id, status, stripe_session_id, total_cents, currency,"
    " created_at) VALUES (?, ?, ?, ?, ?, ?)"
)
_INSERT_LINE = (
    "INSERT INTO order_lines (order_id, product_name, unit_price_cents, quantity)"
    " VALUES (?, ?, ?, ?)"
)
_SELECT_ORDER = (
    "SELECT id, user_id, status, stripe_session_id, total_cents, currency, created_at"
    " FROM orders WHERE stripe_session_id = ?"
)
_SELECT_LINES = (
    "SELECT product_name, unit_price_cents, quantity FROM order_lines"
    " WHERE order_id = ? ORDER BY id"
)
_DUPLICATE_COLUMN = "orders.stripe_session_id"


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
        )

    def get_by_session(self, stripe_session_id: str) -> Order | None:
        """@brief Return the order of a payment session, or None."""
        with closing(connect(self._database_path)) as connection:
            row = connection.execute(_SELECT_ORDER, (stripe_session_id,)).fetchone()
            if row is None:
                return None
            lines = connection.execute(_SELECT_LINES, (row[0],)).fetchall()
        return Order(
            row[0],
            row[1],
            OrderStatus(row[2]),
            row[3],
            Money(row[4]),
            row[5],
            datetime.fromisoformat(row[6]),
            tuple(OrderLine(name, Money(price), qty) for name, price, qty in lines),
        )
