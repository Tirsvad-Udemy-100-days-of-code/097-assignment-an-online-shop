"""@brief The port through which the business stores and reads users."""

from typing import Protocol

from online_shop.domain.user import User, UserRole


class UserRepository(Protocol):
    """@brief Stores users; an adapter implements it."""

    def add(self, email: str, password_hash: str, role: UserRole) -> User:
        """@brief Store a new user.

        @raises DuplicateEmailError When the email is already taken, in any case.
        """
        ...

    def get(self, user_id: int) -> User | None:
        """@brief Return the user with this id, or None."""
        ...

    def get_by_email(self, email: str) -> User | None:
        """@brief Return the user with this email (any case), or None."""
        ...
