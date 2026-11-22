"""Tests of migration 5 and the board queries of the SQLite order repository."""

import sqlite3
from contextlib import closing
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from online_shop.domain.money import Money
from online_shop.domain.order import OrderLine, OrderStatus
from online_shop.domain.user import UserRole
from online_shop.infrastructure import database
from online_shop.infrastructure.database import connect, migrate
from online_shop.infrastructure.sqlite_order_repository import SqliteOrderRepository
from online_shop.infrastructure.sqlite_user_repository import SqliteUserRepository

NOW = datetime(2026, 5, 6, 7, 8, 9, tzinfo=UTC)
LINE = (OrderLine("Mug", Money(1200), 2),)
NEW = OrderStatus.NEEDS_CONFIRMATION
CONFIRMED = OrderStatus.CONFIRMED


@pytest.fixture
def database_path(tmp_path: Path) -> Path:
    path = tmp_path / "board.sqlite3"
    migrate(path)
    users = SqliteUserRepository(path)
    users.add("a@example.com", "hash", UserRole.CUSTOMER)
    users.add("b@example.com", "hash", UserRole.CUSTOMER)
    return path


def add(repo: SqliteOrderRepository, number: int, user_id: int = 1) -> int:
    order = repo.add(
        user_id,
        f"cs_{number}",
        Money(2400),
        "eur",
        NOW + timedelta(minutes=number),
        LINE,
    )
    return order.id


def column(repo: SqliteOrderRepository, status: OrderStatus) -> list[int]:
    return [o.id for o in repo.list_board() if o.status is status]


def test_new_orders_are_numbered_at_the_end_of_needs_confirmation(
    database_path: Path,
) -> None:
    repo = SqliteOrderRepository(database_path)
    ids = [add(repo, n) for n in range(3)]
    assert [repo.list_board()[i].position for i in range(3)] == [0, 1, 2]
    assert column(repo, NEW) == ids


def test_move_persists_and_renumbers_source_and_target(database_path: Path) -> None:
    repo = SqliteOrderRepository(database_path)
    first, second, third = (add(repo, n) for n in range(3))
    assert repo.move(first, CONFIRMED, 0)
    assert repo.move(third, CONFIRMED, 0)
    fresh = SqliteOrderRepository(database_path)
    assert column(fresh, CONFIRMED) == [third, first]
    assert column(fresh, NEW) == [second]
    positions = {o.id: o.position for o in fresh.list_board()}
    assert positions == {third: 0, first: 1, second: 0}


def test_move_inside_a_column_and_past_the_end(database_path: Path) -> None:
    repo = SqliteOrderRepository(database_path)
    first, second, third = (add(repo, n) for n in range(3))
    assert repo.move(first, NEW, 99)
    assert column(repo, NEW) == [second, third, first]
    assert repo.move(first, NEW, 0)
    assert column(repo, NEW) == [first, second, third]


def test_move_of_an_unknown_order_changes_nothing(database_path: Path) -> None:
    repo = SqliteOrderRepository(database_path)
    first = add(repo, 1)
    assert not repo.move(99, CONFIRMED, 0)
    assert column(repo, NEW) == [first]


def test_a_new_order_after_a_move_goes_behind_the_waiting_ones(
    database_path: Path,
) -> None:
    repo = SqliteOrderRepository(database_path)
    first, second = add(repo, 1), add(repo, 2)
    repo.move(first, CONFIRMED, 0)
    third = add(repo, 3)
    assert column(repo, NEW) == [second, third]
    assert repo.get_by_session("cs_3") is not None
    assert [o.position for o in repo.list_board() if o.id == third] == [1]


def test_list_for_user_is_newest_first_with_lines(database_path: Path) -> None:
    repo = SqliteOrderRepository(database_path)
    old, other, new = add(repo, 1), add(repo, 2, 2), add(repo, 3)
    mine = repo.list_for_user(1)
    assert [o.id for o in mine] == [new, old]
    assert mine[0].lines == LINE
    assert [o.id for o in repo.list_for_user(2)] == [other]
    assert repo.list_for_user(9) == []


def test_move_rolls_back_when_a_write_fails(database_path: Path) -> None:
    repo = SqliteOrderRepository(database_path)
    first, second = add(repo, 1), add(repo, 2)
    with closing(connect(database_path)) as connection, connection:
        connection.execute(
            "CREATE TRIGGER refuse BEFORE UPDATE ON orders "
            "WHEN NEW.position = 1 BEGIN SELECT RAISE(ABORT, 'refused'); END"
        )
    with pytest.raises(sqlite3.IntegrityError):
        repo.move(first, NEW, 1)
    assert column(repo, NEW) == [first, second]


def test_migration_five_numbers_orders_that_exist_at_version_four(
    tmp_path: Path,
) -> None:
    path = tmp_path / "old.sqlite3"
    with closing(sqlite3.connect(path)) as connection:
        for script in database._MIGRATIONS[:4]:
            connection.executescript(script)
        connection.execute(
            "INSERT INTO users VALUES (1, 'a@example.com', 'h', 'customer')"
        )
        for number, status in enumerate(["Confirmed", "Needs confirmation"] * 2):
            connection.execute(
                "INSERT INTO orders (user_id, status, stripe_session_id, total_cents,"
                " currency, created_at) VALUES (1, ?, ?, 1, 'eur', ?)",
                (status, f"s{number}", NOW.isoformat()),
            )
        connection.commit()
    migrate(path)
    repo = SqliteOrderRepository(path)
    assert [(o.id, o.status, o.position) for o in repo.list_board()] == [
        (1, CONFIRMED, 0),
        (2, NEW, 0),
        (3, CONFIRMED, 1),
        (4, NEW, 1),
    ]
