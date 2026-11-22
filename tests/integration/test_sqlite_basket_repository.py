"""Tests of the SQLite basket repository, the use cases on it and migration 3."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from online_shop import constants
from online_shop.application.add_to_basket import AddToBasket
from online_shop.application.errors import ProductNotFoundError
from online_shop.application.update_basket_line import UpdateBasketLine
from online_shop.application.view_basket import ViewBasket
from online_shop.domain.basket import Basket, BasketLine
from online_shop.domain.errors import InvalidQuantityError
from online_shop.domain.user import UserRole
from online_shop.infrastructure.database import connect, migrate, seed_products
from online_shop.infrastructure.sqlite_basket_repository import (
    SqliteBasketRepository,
)
from online_shop.infrastructure.sqlite_product_repository import (
    SqliteProductRepository,
)
from online_shop.infrastructure.sqlite_user_repository import SqliteUserRepository


@pytest.fixture
def database(tmp_path: Path) -> Path:
    path = tmp_path / "basket.sqlite3"
    migrate(path)
    seed_products(path)
    return path


@pytest.fixture
def user_id(database: Path) -> int:
    return SqliteUserRepository(database).add("a@b.co", "h", UserRole.CUSTOMER).id


def test_a_basket_that_was_never_saved_is_empty(database: Path, user_id: int) -> None:
    assert SqliteBasketRepository(database).get(user_id) == Basket(user_id)


def test_save_then_get_round_trips_and_replaces(database: Path, user_id: int) -> None:
    repository = SqliteBasketRepository(database)
    repository.save(Basket(user_id, (BasketLine(2, 3), BasketLine(1, 1))))
    assert repository.get(user_id).lines == (BasketLine(2, 3), BasketLine(1, 1))
    repository.save(Basket(user_id, (BasketLine(1, 5),)))
    assert repository.get(user_id).lines == (BasketLine(1, 5),)


def test_basket_is_kept_by_a_new_repository_instance(
    database: Path, user_id: int
) -> None:
    SqliteBasketRepository(database).save(Basket(user_id, (BasketLine(1, 2),)))
    assert SqliteBasketRepository(database).get(user_id).item_count == 2


def test_use_cases_on_sqlite(database: Path, user_id: int) -> None:
    baskets = SqliteBasketRepository(database)
    products = SqliteProductRepository(database)
    add = AddToBasket(baskets, products)
    add.execute(user_id, 1)
    add.execute(user_id, 1)
    add.execute(user_id, 2)
    view = ViewBasket(baskets, products).execute(user_id)
    assert view.item_count == 3
    expected = 2 * view.lines[0].unit_price_cents + view.lines[1].unit_price_cents
    assert view.total_cents == expected
    UpdateBasketLine(baskets, products).execute(user_id, 1, 0)
    assert [line.product_id for line in baskets.get(user_id).lines] == [2]


def test_unknown_product_is_not_found(database: Path, user_id: int) -> None:
    add = AddToBasket(
        SqliteBasketRepository(database), SqliteProductRepository(database)
    )
    with pytest.raises(ProductNotFoundError):
        add.execute(user_id, 999)


def test_quantity_over_the_limit_is_a_validation_error(
    database: Path, user_id: int
) -> None:
    add = AddToBasket(
        SqliteBasketRepository(database), SqliteProductRepository(database)
    )
    with pytest.raises(InvalidQuantityError):
        add.execute(user_id, 1, constants.BASKET_MAX_QUANTITY + 1)


def test_deleting_a_user_deletes_the_basket(database: Path, user_id: int) -> None:
    repository = SqliteBasketRepository(database)
    repository.save(Basket(user_id, (BasketLine(1, 2),)))
    with closing(connect(database)) as connection, connection:
        connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
        assert (
            connection.execute("SELECT COUNT(*) FROM basket_lines").fetchone()[0] == 0
        )
        assert connection.execute("SELECT COUNT(*) FROM baskets").fetchone()[0] == 0


def test_deleting_a_product_deletes_its_lines(database: Path, user_id: int) -> None:
    SqliteBasketRepository(database).save(Basket(user_id, (BasketLine(1, 2),)))
    with closing(connect(database)) as connection, connection:
        connection.execute("DELETE FROM products WHERE id = 1")
    assert SqliteBasketRepository(database).get(user_id).lines == ()


def test_a_line_for_an_unknown_user_is_refused(database: Path) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        SqliteBasketRepository(database).save(Basket(999, (BasketLine(1, 1),)))


INSERT_LINE = (
    "INSERT INTO basket_lines (user_id, product_id, quantity) VALUES (?, 1, ?)"
)


def test_the_table_refuses_a_duplicate_line(database: Path, user_id: int) -> None:
    SqliteBasketRepository(database).save(Basket(user_id))
    with closing(connect(database)) as connection, connection:
        connection.execute(INSERT_LINE, (user_id, 1))
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(INSERT_LINE, (user_id, 1))


@pytest.mark.parametrize("quantity", [0, constants.BASKET_MAX_QUANTITY + 1])
def test_the_table_refuses_a_quantity_outside_the_limits(
    database: Path, user_id: int, quantity: int
) -> None:
    SqliteBasketRepository(database).save(Basket(user_id))
    with (
        closing(connect(database)) as connection,
        connection,
        pytest.raises(sqlite3.IntegrityError),
    ):
        connection.execute(INSERT_LINE, (user_id, quantity))
