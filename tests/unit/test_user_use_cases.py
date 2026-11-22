"""Tests of the account use cases over fake ports."""

import pytest

from fakes import FakePasswordHasher, FakeUserRepository
from online_shop import constants
from online_shop.application.authenticate_user import AuthenticateUser
from online_shop.application.ensure_admin import EnsureAdmin
from online_shop.application.errors import AuthenticationFailedError
from online_shop.application.get_user import GetUser
from online_shop.application.register_user import RegisterUser
from online_shop.domain.errors import (
    DuplicateEmailError,
    InvalidEmailError,
    InvalidPasswordError,
)
from online_shop.domain.user import UserRole

PASSWORD = "correct horse"


@pytest.fixture
def users() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def register(users: FakeUserRepository) -> RegisterUser:
    return RegisterUser(users, FakePasswordHasher())


def test_register_stores_a_hash_and_returns_a_dto_without_it(
    register: RegisterUser, users: FakeUserRepository
) -> None:
    dto = register.execute(" Ann@Example.com ", PASSWORD)
    assert (dto.email, dto.role, dto.is_admin) == ("ann@example.com", "customer", False)
    stored = users.get(dto.id)
    assert stored is not None
    assert stored.password_hash != PASSWORD


def test_register_refuses_duplicate_email_in_any_case(register: RegisterUser) -> None:
    register.execute("ann@example.com", PASSWORD)
    with pytest.raises(DuplicateEmailError):
        register.execute("ANN@example.com", PASSWORD)


def test_register_refuses_bad_input(register: RegisterUser) -> None:
    with pytest.raises(InvalidEmailError):
        register.execute("nope", PASSWORD)
    with pytest.raises(InvalidPasswordError):
        register.execute("ann@example.com", "short")


def test_authenticate_returns_the_user(
    register: RegisterUser, users: FakeUserRepository
) -> None:
    created = register.execute("ann@example.com", PASSWORD)
    found = AuthenticateUser(users, FakePasswordHasher()).execute(
        "Ann@example.com", PASSWORD
    )
    assert found == created


@pytest.mark.parametrize(
    ("email", "password"),
    [("ann@example.com", "wrong password"), ("bob@example.com", PASSWORD), ("x", "y")],
)
def test_authenticate_gives_one_generic_failure(
    register: RegisterUser, users: FakeUserRepository, email: str, password: str
) -> None:
    register.execute("ann@example.com", PASSWORD)
    with pytest.raises(AuthenticationFailedError) as caught:
        AuthenticateUser(users, FakePasswordHasher()).execute(email, password)
    assert str(caught.value) == constants.ERROR_BAD_CREDENTIALS


def test_unknown_email_still_verifies_a_hash() -> None:
    calls: list[str] = []

    class CountingHasher(FakePasswordHasher):
        def verify(self, password: str, password_hash: str) -> bool:
            calls.append(password_hash)
            return super().verify(password, password_hash)

    use_case = AuthenticateUser(FakeUserRepository(), CountingHasher())
    with pytest.raises(AuthenticationFailedError):
        use_case.execute("nobody@example.com", PASSWORD)
    assert len(calls) == 1


def test_get_user_returns_dto_or_none(
    register: RegisterUser, users: FakeUserRepository
) -> None:
    created = register.execute("ann@example.com", PASSWORD)
    assert GetUser(users).execute(created.id) == created
    assert GetUser(users).execute(99) is None


def test_ensure_admin_is_idempotent(
    register: RegisterUser, users: FakeUserRepository
) -> None:
    ensure = EnsureAdmin(users, register)
    assert ensure.execute("Root@example.com", PASSWORD) is True
    assert ensure.execute("root@example.com", "another password") is False
    admin = users.get_by_email("root@example.com")
    assert admin is not None
    assert admin.role is UserRole.ADMIN
    assert admin.password_hash == FakePasswordHasher().hash(PASSWORD)
