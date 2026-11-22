"""@brief The SQLite adapter of the ProductRepository port."""

from contextlib import closing
from pathlib import Path

from online_shop.domain.money import Money
from online_shop.domain.product import Product
from online_shop.infrastructure.database import connect

_SELECT_ALL = (
    "SELECT id, name, description, price_cents, image FROM products ORDER BY id"
)
_SELECT_ONE = (
    "SELECT id, name, description, price_cents, image FROM products WHERE id = ?"
)


def _to_product(row: tuple[int, str, str, int, str]) -> Product:
    product_id, name, description, price_cents, image = row
    return Product(product_id, name, description, Money(price_cents), image)


class SqliteProductRepository:
    """@brief Reads products from a SQLite file; one connection per call."""

    def __init__(self, database_path: Path) -> None:
        """@brief Remember the file.

        @param database_path The SQLite file, already migrated.
        """
        self._database_path = database_path

    def list_all(self) -> list[Product]:
        """@brief Return every product, ordered by id."""
        with closing(connect(self._database_path)) as connection:
            return [_to_product(row) for row in connection.execute(_SELECT_ALL)]

    def get(self, product_id: int) -> Product | None:
        """@brief Return one product, or None when no product has this id."""
        with closing(connect(self._database_path)) as connection:
            try:
                row = connection.execute(_SELECT_ONE, (product_id,)).fetchone()
            except OverflowError:
                # An id larger than SQLite's integer cannot exist.
                return None
        return None if row is None else _to_product(row)
