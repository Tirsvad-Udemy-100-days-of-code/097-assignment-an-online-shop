"""Fakes of the user ports, shared by the unit tests."""

from online_shop.domain.basket import Basket
from online_shop.domain.errors import DuplicateEmailError
from online_shop.domain.user import User, UserRole


class FakePasswordHasher:
    """Reversible and instant; only for tests that do not test hashing."""

    def hash(self, password: str) -> str:
        return "fake$" + password[::-1]

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == self.hash(password)


class FakeUserRepository:
    def __init__(self) -> None:
        self._users: list[User] = []

    def add(self, email: str, password_hash: str, role: UserRole) -> User:
        if self.get_by_email(email) is not None:
            raise DuplicateEmailError(email)
        user = User(len(self._users) + 1, email, password_hash, role)
        self._users.append(user)
        return user

    def get(self, user_id: int) -> User | None:
        return next((u for u in self._users if u.id == user_id), None)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users if u.email.lower() == email.lower()), None)


class FakeBasketRepository:
    def __init__(self) -> None:
        self._baskets: dict[int, Basket] = {}

    def get(self, user_id: int) -> Basket:
        return self._baskets.get(user_id, Basket(user_id))

    def save(self, basket: Basket) -> None:
        self._baskets[basket.user_id] = basket
