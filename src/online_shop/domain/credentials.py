"""@brief The rules for email addresses and passwords."""

import re

from online_shop import constants
from online_shop.domain.errors import InvalidEmailError, InvalidPasswordError

_EMAIL = re.compile(constants.EMAIL_PATTERN)


def normalize_email(raw: str) -> str:
    """@brief Trim and lower-case an email address after checking its shape.

    @param raw The address as typed.
    @return The address as it is stored and compared.
    @raises InvalidEmailError When it is not a plausible address.
    """
    email = raw.strip().lower()
    if len(email) > constants.EMAIL_MAX_LENGTH or not _EMAIL.fullmatch(email):
        raise InvalidEmailError(constants.ERROR_EMAIL_INVALID)
    return email


def validate_password(password: str) -> None:
    """@brief Check the length of a new password.

    @param password The password as typed.
    @raises InvalidPasswordError When it is too short or too long.
    """
    if len(password) < constants.PASSWORD_MIN_LENGTH:
        raise InvalidPasswordError(constants.ERROR_PASSWORD_TOO_SHORT)
    if len(password) > constants.PASSWORD_MAX_LENGTH:
        raise InvalidPasswordError(constants.ERROR_PASSWORD_TOO_LONG)
