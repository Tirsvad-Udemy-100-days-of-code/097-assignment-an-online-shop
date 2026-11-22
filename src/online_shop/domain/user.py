"""@brief The User entity and its role."""

from dataclasses import dataclass
from enum import StrEnum

from online_shop import constants
from online_shop.domain.errors import InvalidUserError


class UserRole(StrEnum):
    """@brief What an account may do: shop as a customer, or administer."""

    CUSTOMER = "customer"
    ADMIN = "admin"


@dataclass(frozen=True, slots=True)
class User:
    """@brief A person with an account.

    @param id The unique key of the user, positive.
    @param email The normalized email address.
    @param password_hash The salted password hash; never the password.
    @param role The role of the account.
    """

    id: int
    email: str
    password_hash: str
    role: UserRole

    def __post_init__(self) -> None:
        """@brief Reject a user without a positive id."""
        if self.id < 1:
            raise InvalidUserError(constants.ERROR_USER_INVALID)
