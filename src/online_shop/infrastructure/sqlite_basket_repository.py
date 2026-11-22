"""@brief The SQLite adapter of the BasketRepository port."""

from contextlib import closing
from pathlib import Path

from online_shop.domain.basket import Basket, BasketLine
from online_shop.infrastructure.database import connect

_SELECT_LINES = (
    "SELECT product_id, quantity FROM basket_lines WHERE user_id = ? ORDER BY id"
)
_ENSURE_BASKET = "INSERT OR IGNORE INTO baskets (user_id) VALUES (?)"
_DELETE_LINES = "DELETE FROM basket_lines WHERE user_id = ?"
_INSERT_LINE = (
    "INSERT INTO basket_lines (user_id, product_id, quantity) VALUES (?, ?, ?)"
)


class SqliteBasketRepository:
    """@brief Keeps baskets in a SQLite file; one connection per call."""

    def __init__(self, database_path: Path) -> None:
        """@param database_path The SQLite file, already migrated."""
        self._database_path = database_path

    def get(self, user_id: int) -> Basket:
        """@brief Return the basket of the user; empty when none was saved."""
        with closing(connect(self._database_path)) as connection:
            rows = connection.execute(_SELECT_LINES, (user_id,)).fetchall()
        return Basket(user_id, tuple(BasketLine(product, qty) for product, qty in rows))

    def save(self, basket: Basket) -> None:
        """@brief Replace the stored lines of the owner in one transaction."""
        with closing(connect(self._database_path)) as connection, connection:
            connection.execute(_ENSURE_BASKET, (basket.user_id,))
            connection.execute(_DELETE_LINES, (basket.user_id,))
            connection.executemany(
                _INSERT_LINE,
                [
                    (basket.user_id, line.product_id, line.quantity)
                    for line in basket.lines
                ],
            )
