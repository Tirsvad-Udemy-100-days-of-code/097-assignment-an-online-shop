"""@brief The use case that makes sure the configured admin account exists."""

import logging

from online_shop.application.register_user import RegisterUser
from online_shop.domain.credentials import normalize_email
from online_shop.domain.errors import DuplicateEmailError
from online_shop.domain.user import UserRole
from online_shop.domain.user_repository import UserRepository

_LOG = logging.getLogger(__name__)


class EnsureAdmin:
    """@brief Creates the admin account once; later calls change nothing."""

    def __init__(self, users: UserRepository, register: RegisterUser) -> None:
        """@param users The user store.  @param register The creation use case."""
        self._users = users
        self._register = register

    def execute(self, email: str, password: str) -> bool:
        """@brief Create the admin when no account has this email.

        The password is never logged. An existing account is left untouched.

        @return True when the account was created.
        """
        if self._users.get_by_email(normalize_email(email)) is not None:
            return False
        try:
            self._register.execute(email, password, UserRole.ADMIN)
        except DuplicateEmailError:
            return False
        _LOG.info("Created the admin account.")
        return True
