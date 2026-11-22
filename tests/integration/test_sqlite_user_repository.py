"""Tests of the SQLite user repository and the user-table migration."""

import sqlite3
from pathlib import Path

import pytest

from online_shop.application.authenticate_user import AuthenticateUser
from online_shop.application.errors import AuthenticationFailedError
from online_shop.application.register_user import RegisterUser
from online_shop.domain.errors import DuplicateEmailError
from online_shop.domain.user import UserRole
from online_shop.infrastructure.database import connect, migrate
from online_shop.infrastructure.scrypt_password_hasher import ScryptPasswordHasher
from online_shop.infrastructure.sqlite_user_repository import SqliteUserRepository


@pytest.fixture
def database(tmp_path: Path) -> Path:
    path = tmp_path / "users.sqlite3"
    migrate(path)
    return path


def test_add_then_get_by_id_and_by_email_any_case(database: Path) -> None:
    repository = SqliteUserRepository(database)
    user = repository.add("ann@example.com", "hash", UserRole.ADMIN)
    assert repository.get(user.id) == user
    assert repository.get_by_email("ANN@Example.com") == user


def test_unknown_user_is_none(database: Path) -> None:
    repository = SqliteUserRepository(database)
    assert repository.get(1) is None
    assert repository.get(10**30) is None
    assert repository.get_by_email("nobody@example.com") is None


def test_duplicate_email_is_refused_case_insensitively(database: Path) -> None:
    repository = SqliteUserRepository(database)
    repository.add("ann@example.com", "hash", UserRole.CUSTOMER)
    with pytest.raises(DuplicateEmailError):
        repository.add("ANN@example.com", "hash", UserRole.CUSTOMER)


def test_database_refuses_an_unknown_role(database: Path) -> None:
    with connect(database) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO users (email, password_hash, role) VALUES ('a@b.co', 'h', 'x')"
        )


def test_migration_keeps_users_across_restarts(database: Path) -> None:
    SqliteUserRepository(database).add("ann@example.com", "hash", UserRole.CUSTOMER)
    migrate(database)
    assert SqliteUserRepository(database).get_by_email("ann@example.com") is not None


def test_register_then_authenticate_with_real_hasher(database: Path) -> None:
    repository = SqliteUserRepository(database)
    hasher = ScryptPasswordHasher()
    RegisterUser(repository, hasher).execute("ann@example.com", "correct horse")
    stored = repository.get_by_email("ann@example.com")
    assert stored is not None
    assert "correct horse" not in stored.password_hash
    authenticate = AuthenticateUser(repository, hasher)
    assert authenticate.execute("ann@example.com", "correct horse").id == stored.id
    with pytest.raises(AuthenticationFailedError):
        authenticate.execute("ann@example.com", "wrong horse!")
