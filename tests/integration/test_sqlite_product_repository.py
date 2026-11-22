"""Tests of the SQLite adapter against a real file database."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from online_shop import constants
from online_shop.infrastructure.database import migrate, seed_products
from online_shop.infrastructure.sqlite_product_repository import (
    SqliteProductRepository,
)


@pytest.fixture
def database(tmp_path: Path) -> Path:
    path = tmp_path / "shop.sqlite3"
    migrate(path)
    seed_products(path)
    return path


def test_seeded_products_are_listed_in_order(database: Path) -> None:
    products = SqliteProductRepository(database).list_all()
    assert [p.name for p in products] == [s[0] for s in constants.SEED_PRODUCTS]
    assert [p.id for p in products] == list(range(1, len(products) + 1))
    assert products[0].price.cents == constants.SEED_PRODUCTS[0][2]
    assert products[0].image == constants.SEED_PRODUCTS[0][3]


def test_get_returns_one_product(database: Path) -> None:
    product = SqliteProductRepository(database).get(2)
    assert product is not None
    assert product.name == constants.SEED_PRODUCTS[1][0]


@pytest.mark.parametrize("product_id", [0, 999, 2**70])
def test_get_returns_none_for_unknown_id(database: Path, product_id: int) -> None:
    assert SqliteProductRepository(database).get(product_id) is None


def test_data_survives_a_restart_without_duplicating_the_seed(database: Path) -> None:
    with closing(sqlite3.connect(database)) as connection, connection:
        connection.execute("UPDATE products SET name = 'Renamed' WHERE id = 1")
    migrate(database)
    seed_products(database)
    products = SqliteProductRepository(database).list_all()
    assert len(products) == len(constants.SEED_PRODUCTS)
    assert products[0].name == "Renamed"


def test_migration_records_the_schema_version(database: Path) -> None:
    with closing(sqlite3.connect(database)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 3
