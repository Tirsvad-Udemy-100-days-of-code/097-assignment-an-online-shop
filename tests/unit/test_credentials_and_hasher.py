"""Tests of the email and password rules, the User entity and the scrypt hasher."""

import pytest

from online_shop import constants
from online_shop.domain.credentials import normalize_email, validate_password
from online_shop.domain.errors import (
    InvalidEmailError,
    InvalidPasswordError,
    InvalidUserError,
)
from online_shop.domain.user import User, UserRole
from online_shop.infrastructure.scrypt_password_hasher import ScryptPasswordHasher


def test_normalize_email_trims_and_lowercases() -> None:
    assert normalize_email("  Ann@Example.COM ") == "ann@example.com"


@pytest.mark.parametrize(
    "raw",
    ["", "ann", "ann@", "@example.com", "ann@example", "a b@example.com", "a@@b.c"]
    + ["a" * constants.EMAIL_MAX_LENGTH + "@example.com"],
)
def test_normalize_email_rejects_bad_address(raw: str) -> None:
    with pytest.raises(InvalidEmailError):
        normalize_email(raw)


def test_password_length_boundaries() -> None:
    validate_password("x" * constants.PASSWORD_MIN_LENGTH)
    validate_password("x" * constants.PASSWORD_MAX_LENGTH)
    with pytest.raises(InvalidPasswordError):
        validate_password("x" * (constants.PASSWORD_MIN_LENGTH - 1))
    with pytest.raises(InvalidPasswordError):
        validate_password("x" * (constants.PASSWORD_MAX_LENGTH + 1))


def test_user_needs_positive_id() -> None:
    assert User(1, "a@b.co", "h", UserRole.ADMIN).role == "admin"
    with pytest.raises(InvalidUserError):
        User(0, "a@b.co", "h", UserRole.CUSTOMER)


def test_hash_is_salted_and_carries_its_parameters() -> None:
    hasher = ScryptPasswordHasher()
    first, second = hasher.hash("secret-pw"), hasher.hash("secret-pw")
    assert first != second
    scheme, n, r, p, _, _ = first.split(constants.HASH_SEPARATOR)
    assert (scheme, int(n), int(r), int(p)) == (
        constants.SCRYPT_SCHEME,
        constants.SCRYPT_N,
        constants.SCRYPT_R,
        constants.SCRYPT_P,
    )
    assert "secret-pw" not in first


def test_verify_accepts_right_and_refuses_wrong_password() -> None:
    hasher = ScryptPasswordHasher()
    stored = hasher.hash("pässword-ü")
    assert hasher.verify("pässword-ü", stored)
    assert not hasher.verify("password-u", stored)


@pytest.mark.parametrize(
    "stored",
    ["", "plain", "md5$1$2$3$a$b", "scrypt$x$8$1$AA==$AA==", "scrypt$16384$8$1$!!$!!"],
)
def test_verify_refuses_malformed_hash(stored: str) -> None:
    assert not ScryptPasswordHasher().verify("secret-pw", stored)


def test_verify_honours_old_parameters() -> None:
    hasher = ScryptPasswordHasher()
    stored = hasher.hash("secret-pw")
    parts = stored.split(constants.HASH_SEPARATOR)
    parts[1] = str(constants.SCRYPT_N * 2)  # a different cost: key no longer matches
    assert not hasher.verify("secret-pw", constants.HASH_SEPARATOR.join(parts))
