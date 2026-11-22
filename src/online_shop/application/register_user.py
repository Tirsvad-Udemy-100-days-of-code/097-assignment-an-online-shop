"""@brief The use case that creates an account."""

from online_shop.application.dto import UserDto, to_user_dto
from online_shop.domain.credentials import normalize_email, validate_password
from online_shop.domain.password_hasher import PasswordHasher
from online_shop.domain.user import UserRole
from online_shop.domain.user_repository import UserRepository


class RegisterUser:
    """@brief Validates the input, hashes the password and stores the user."""

    def __init__(self, users: UserRepository, hasher: PasswordHasher) -> None:
        """@param users The user store.  @param hasher The password hasher."""
        self._users = users
        self._hasher = hasher

    def execute(
        self, email: str, password: str, role: UserRole = UserRole.CUSTOMER
    ) -> UserDto:
        """@brief Create an account.

        The web layer never passes a role; only the start-up admin set-up does.

        @param email The address as typed.
        @param password The password as typed.
        @param role The role of the new account.
        @raises InvalidEmailError When the address is not acceptable.
        @raises InvalidPasswordError When the password is not acceptable.
        @raises DuplicateEmailError When the email is already taken.
        """
        normalized = normalize_email(email)
        validate_password(password)
        user = self._users.add(normalized, self._hasher.hash(password), role)
        return to_user_dto(user)
