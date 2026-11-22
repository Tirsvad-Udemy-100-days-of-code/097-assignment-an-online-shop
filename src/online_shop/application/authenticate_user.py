"""@brief The use case that checks an email and a password."""

import secrets

from online_shop import constants
from online_shop.application.dto import UserDto, to_user_dto
from online_shop.application.errors import AuthenticationFailedError
from online_shop.domain.credentials import normalize_email
from online_shop.domain.errors import InvalidEmailError
from online_shop.domain.password_hasher import PasswordHasher
from online_shop.domain.user import User
from online_shop.domain.user_repository import UserRepository


class AuthenticateUser:
    """@brief Signs a user in, with one generic failure for every cause."""

    def __init__(self, users: UserRepository, hasher: PasswordHasher) -> None:
        """@param users The user store.  @param hasher The password hasher."""
        self._users = users
        self._hasher = hasher
        # Hashed once so an unknown email costs the same time as a wrong password.
        dummy_password = secrets.token_urlsafe(constants.DUMMY_PASSWORD_BYTES)
        self._dummy_hash = hasher.hash(dummy_password)

    def execute(self, email: str, password: str) -> UserDto:
        """@brief Return the user when the credentials are right.

        @param email The address as typed.
        @param password The password as typed.
        @raises AuthenticationFailedError For an unknown email or a wrong password.
        """
        user = self._find(email)
        stored = user.password_hash if user else self._dummy_hash
        matches = self._hasher.verify(password, stored)
        if user is None or not matches:
            raise AuthenticationFailedError(constants.ERROR_BAD_CREDENTIALS)
        return to_user_dto(user)

    def _find(self, email: str) -> User | None:
        try:
            return self._users.get_by_email(normalize_email(email))
        except InvalidEmailError:
            return None
