"""Fakes of the user ports, shared by the unit tests."""

from datetime import datetime

from online_shop.application.errors import PaymentGatewayError
from online_shop.application.payment_gateway import (
    CheckoutRequest,
    CheckoutSession,
    SessionResult,
)
from online_shop.domain.basket import Basket
from online_shop.domain.errors import DuplicateEmailError, DuplicateOrderError
from online_shop.domain.money import Money
from online_shop.domain.order import Order, OrderLine, OrderStatus
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


class FakeOrderRepository:
    def __init__(self) -> None:
        self.orders: list[Order] = []

    def add(
        self,
        user_id: int,
        stripe_session_id: str,
        total: Money,
        currency: str,
        created_at: datetime,
        lines: tuple[OrderLine, ...],
    ) -> Order:
        if self.get_by_session(stripe_session_id) is not None:
            raise DuplicateOrderError(stripe_session_id)
        order = Order(
            len(self.orders) + 1,
            user_id,
            OrderStatus.NEEDS_CONFIRMATION,
            stripe_session_id,
            total,
            currency,
            created_at,
            lines,
        )
        self.orders.append(order)
        return order

    def get_by_session(self, stripe_session_id: str) -> Order | None:
        return next(
            (o for o in self.orders if o.stripe_session_id == stripe_session_id), None
        )


class FakePaymentGateway:
    """No network: sessions live in memory and the test decides who paid."""

    def __init__(self) -> None:
        self.requests: list[CheckoutRequest] = []
        self.sessions: dict[str, SessionResult] = {}
        self.fail = False

    def create_checkout_session(self, request: CheckoutRequest) -> CheckoutSession:
        if self.fail:
            raise PaymentGatewayError("fake failure")
        self.requests.append(request)
        session_id = f"cs_test_{len(self.requests)}"
        total = sum(i.unit_amount_cents * i.quantity for i in request.line_items)
        self.sessions[session_id] = SessionResult(
            session_id, False, total, request.currency, request.client_reference_id
        )
        return CheckoutSession(session_id, f"https://pay.example/{session_id}")

    def retrieve_session(self, session_id: str) -> SessionResult:
        if self.fail:
            raise PaymentGatewayError("fake failure")
        try:
            return self.sessions[session_id]
        except KeyError:
            raise PaymentGatewayError("unknown session") from None

    def pay(self, session_id: str) -> None:
        old = self.sessions[session_id]
        self.sessions[session_id] = SessionResult(
            old.id, True, old.amount_total, old.currency, old.client_reference_id
        )


FAKE_KEY_BODY_LENGTH = 30


def fake_key(kind: str, mode: str, body: str = "x" * FAKE_KEY_BODY_LENGTH) -> str:
    """A key-shaped value built at run time, so no key literal sits in the source."""
    return f"{kind}_{mode}_{body}"
