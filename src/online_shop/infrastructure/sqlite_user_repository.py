"""@brief The SQLite adapter of the UserRepository port."""

import sqlite3
from contextlib import closing
from pathlib import Path

from online_shop.domain.errors import DuplicateEmailError
from online_shop.domain.user import User, UserRole
from online_shop.infrastructure.database import connect

_INSERT = "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)"
_SELECT_ONE = "SELECT id, email, password_hash, role FROM users WHERE id = ?"
_SELECT_BY_EMAIL = "SELECT id, email, password_hash, role FROM users WHERE email = ?"


def _to_user(row: tuple[int, str, str, str]) -> User:
    user_id, email, password_hash, role = row
    return User(user_id, email, password_hash, UserRole(role))


class SqliteUserRepository:
    """@brief Stores users in a SQLite file; one connection per call."""

    def __init__(self, database_path: Path) -> None:
        """@param database_path The SQLite file, already migrated."""
        self._database_path = database_path

    def add(self, email: str, password_hash: str, role: UserRole) -> User:
        """@brief Store a user; the email is unique regardless of case."""
        with closing(connect(self._database_path)) as connection:
            try:
                with connection:
                    cursor = connection.execute(
                        _INSERT, (email, password_hash, role.value)
                    )
            except sqlite3.IntegrityError as error:
                raise DuplicateEmailError(email) from error
            user_id = cursor.lastrowid
        if user_id is None:
            raise RuntimeError("SQLite gave no key for the new user.")
        return User(user_id, email, password_hash, role)

    def get(self, user_id: int) -> User | None:
        """@brief Return the user with this id, or None."""
        return self._fetch(_SELECT_ONE, user_id)

    def get_by_email(self, email: str) -> User | None:
        """@brief Return the user with this email (any case), or None."""
        return self._fetch(_SELECT_BY_EMAIL, email)

    def _fetch(self, query: str, value: int | str) -> User | None:
        with closing(connect(self._database_path)) as connection:
            try:
                row = connection.execute(query, (value,)).fetchone()
            except OverflowError:
                # An id larger than SQLite's integer cannot exist.
                return None
        return None if row is None else _to_user(row)
