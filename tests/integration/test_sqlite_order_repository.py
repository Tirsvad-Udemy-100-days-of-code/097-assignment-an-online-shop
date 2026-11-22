"""Tests of migration 4 and the SQLite order repository."""

import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

import pytest

from online_shop.domain.errors import DuplicateOrderError
from online_shop.domain.money import Money
from online_shop.domain.order import OrderLine, OrderStatus
from online_shop.domain.user import UserRole
from online_shop.infrastructure.database import connect, migrate
from online_shop.infrastructure.sqlite_order_repository import SqliteOrderRepository
from online_shop.infrastructure.sqlite_user_repository import SqliteUserRepository

NOW = datetime(2026, 5, 6, 7, 8, 9, tzinfo=UTC)
LINES = (OrderLine("Mug", Money(1200), 2), OrderLine("Lamp", Money(3490), 1))


@pytest.fixture
def database(tmp_path: Path) -> Path:
    path = tmp_path / "orders.sqlite3"
    migrate(path)
    SqliteUserRepository(path).add("a@example.com", "hash", UserRole.CUSTOMER)
    return path


def test_added_order_is_read_back_by_session(database: Path) -> None:
    repo = SqliteOrderRepository(database)
    order = repo.add(1, "cs_1", Money(5890), "eur", NOW, LINES)
    assert order.status is OrderStatus.NEEDS_CONFIRMATION
    assert repo.get_by_session("cs_1") == order
    assert order.created_at == NOW


def test_unknown_session_has_no_order(database: Path) -> None:
    assert SqliteOrderRepository(database).get_by_session("nope") is None


def test_same_session_twice_is_a_duplicate_and_leaves_one_order(
    database: Path,
) -> None:
    repo = SqliteOrderRepository(database)
    repo.add(1, "cs_1", Money(1), "eur", NOW, LINES)
    with pytest.raises(DuplicateOrderError):
        repo.add(1, "cs_1", Money(1), "eur", NOW, LINES)
    with closing(connect(database)) as connection:
        assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 1
        assert connection.execute("SELECT COUNT(*) FROM order_lines").fetchone()[0] == 2


def test_unknown_user_is_refused_by_the_foreign_key(database: Path) -> None:
    with pytest.raises(sqlite3.IntegrityError):
        SqliteOrderRepository(database).add(99, "cs_1", Money(1), "eur", NOW, LINES)


def test_status_outside_the_enum_is_refused(database: Path) -> None:
    with (
        closing(connect(database)) as connection,
        pytest.raises(sqlite3.IntegrityError),
    ):
        connection.execute(
            "INSERT INTO orders (user_id, status, stripe_session_id, total_cents,"
            " currency, created_at) VALUES (1, 'Lost', 's', 1, 'eur', 'x')"
        )


def test_migration_four_keeps_earlier_data(database: Path) -> None:
    migrate(database)
    with closing(connect(database)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 4
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
