"""Tests of the checkout use cases with fakes of every port."""

from datetime import UTC, datetime

import pytest

from fakes import FakeBasketRepository, FakeOrderRepository, FakePaymentGateway
from online_shop import constants
from online_shop.application.cancel_checkout import CancelCheckout
from online_shop.application.complete_checkout import CompleteCheckout
from online_shop.application.errors import (
    EmptyBasketError,
    ForeignPaymentError,
    PaymentGatewayError,
    PaymentNotCompletedError,
)
from online_shop.application.start_checkout import StartCheckout
from online_shop.domain.basket import Basket
from online_shop.domain.errors import DuplicateOrderError, InvalidOrderError
from online_shop.domain.money import Money
from online_shop.domain.order import Order, OrderLine, OrderStatus
from online_shop.domain.product import Product

NOW = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)
SUCCESS = "https://shop.test/checkout/success"
CANCEL = "https://shop.test/checkout/cancel"
MUG = Product(1, "Mug", "d", Money(1200), "m.svg")
LAMP = Product(2, "Lamp", "d", Money(3490), "l.svg")


class Catalog:
    def __init__(self, *products: Product) -> None:
        self._products = {p.id: p for p in products}

    def list_all(self) -> list[Product]:
        return list(self._products.values())

    def get(self, product_id: int) -> Product | None:
        return self._products.get(product_id)


class Shop:
    def __init__(self) -> None:
        self.baskets = FakeBasketRepository()
        self.orders = FakeOrderRepository()
        self.payments = FakePaymentGateway()
        self.catalog = Catalog(MUG, LAMP)
        self.start = StartCheckout(self.baskets, self.catalog, self.payments)
        self.complete = CompleteCheckout(
            self.baskets, self.catalog, self.orders, self.payments, lambda: NOW
        )

    def fill(self, user_id: int = 1) -> None:
        basket = Basket(user_id).add(1, 2).add(2, 1)
        self.baskets.save(basket)

    def begin(self, user_id: int = 1) -> str:
        return self.start.execute(user_id, SUCCESS, CANCEL).id


def test_start_prices_the_lines_from_the_current_products() -> None:
    shop = Shop()
    shop.fill()
    session = shop.start.execute(1, SUCCESS, CANCEL)
    request = shop.payments.requests[0]
    assert session.url.endswith(session.id)
    assert [(i.name, i.unit_amount_cents, i.quantity) for i in request.line_items] == [
        ("Mug", 1200, 2),
        ("Lamp", 3490, 1),
    ]
    assert request.currency == constants.CURRENCY_CODE
    assert request.client_reference_id == "1"
    assert request.success_url == f"{SUCCESS}?session_id={{CHECKOUT_SESSION_ID}}"
    assert request.cancel_url == CANCEL


def test_start_appends_to_an_existing_query() -> None:
    shop = Shop()
    shop.fill()
    shop.start.execute(1, SUCCESS + "?a=b", CANCEL)
    assert shop.payments.requests[0].success_url.endswith(
        "?a=b&session_id={CHECKOUT_SESSION_ID}"
    )


def test_start_refuses_an_empty_basket() -> None:
    with pytest.raises(EmptyBasketError):
        Shop().start.execute(1, SUCCESS, CANCEL)


def test_start_refuses_a_basket_of_vanished_products() -> None:
    shop = Shop()
    shop.baskets.save(Basket(1).add(9, 1))
    with pytest.raises(EmptyBasketError):
        shop.start.execute(1, SUCCESS, CANCEL)


def test_start_propagates_a_gateway_failure() -> None:
    shop = Shop()
    shop.fill()
    shop.payments.fail = True
    with pytest.raises(PaymentGatewayError):
        shop.start.execute(1, SUCCESS, CANCEL)


def test_complete_creates_an_order_from_a_paid_session_and_empties_the_basket() -> None:
    shop = Shop()
    shop.fill()
    session_id = shop.begin()
    shop.payments.pay(session_id)
    order = shop.complete.execute(1, session_id)
    assert order.status == "Needs confirmation"
    assert order.total_cents == 2 * 1200 + 3490
    assert [(i.product_name, i.unit_price_cents, i.quantity) for i in order.lines] == [
        ("Mug", 1200, 2),
        ("Lamp", 3490, 1),
    ]
    assert shop.baskets.get(1).lines == ()
    assert len(shop.orders.orders) == 1


def test_complete_is_idempotent_per_session() -> None:
    shop = Shop()
    shop.fill()
    session_id = shop.begin()
    shop.payments.pay(session_id)
    first = shop.complete.execute(1, session_id)
    shop.fill()
    second = shop.complete.execute(1, session_id)
    assert second == first
    assert len(shop.orders.orders) == 1
    assert shop.baskets.get(1).item_count == 3


def test_complete_refuses_an_unpaid_session_and_keeps_the_basket() -> None:
    shop = Shop()
    shop.fill()
    session_id = shop.begin()
    with pytest.raises(PaymentNotCompletedError):
        shop.complete.execute(1, session_id)
    assert shop.orders.orders == []
    assert shop.baskets.get(1).item_count == 3


def test_complete_refuses_a_session_of_another_user() -> None:
    shop = Shop()
    shop.fill()
    session_id = shop.begin()
    shop.payments.pay(session_id)
    with pytest.raises(ForeignPaymentError):
        shop.complete.execute(2, session_id)
    assert shop.orders.orders == []


def test_complete_does_not_show_the_order_of_another_user() -> None:
    shop = Shop()
    shop.fill()
    session_id = shop.begin()
    shop.payments.pay(session_id)
    shop.complete.execute(1, session_id)
    with pytest.raises(ForeignPaymentError):
        shop.complete.execute(2, session_id)


@pytest.mark.parametrize("session_id", ["", "   "])
def test_complete_refuses_a_missing_session_id(session_id: str) -> None:
    with pytest.raises(PaymentNotCompletedError):
        Shop().complete.execute(1, session_id)


def test_complete_propagates_a_gateway_failure_and_keeps_the_basket() -> None:
    shop = Shop()
    shop.fill()
    session_id = shop.begin()
    shop.payments.fail = True
    with pytest.raises(PaymentGatewayError):
        shop.complete.execute(1, session_id)
    assert shop.baskets.get(1).item_count == 3


def test_complete_returns_the_order_that_won_a_race() -> None:
    shop = Shop()
    shop.fill()
    session_id = shop.begin()
    shop.payments.pay(session_id)

    class Racing(FakeOrderRepository):
        def __init__(self) -> None:
            super().__init__()
            self.hidden = True

        def get_by_session(self, stripe_session_id: str) -> Order | None:
            if self.hidden:
                self.hidden = False
                return None
            return super().get_by_session(stripe_session_id)

    racing = Racing()
    racing.add(1, session_id, Money(5), "eur", NOW, ())
    racing.hidden = True
    complete = CompleteCheckout(shop.baskets, shop.catalog, racing, shop.payments)
    assert complete.execute(1, session_id).id == 1


def test_complete_reraises_a_duplicate_that_cannot_be_found() -> None:
    shop = Shop()
    shop.fill()
    session_id = shop.begin()
    shop.payments.pay(session_id)

    class Broken(FakeOrderRepository):
        def get_by_session(self, stripe_session_id: str) -> Order | None:
            return None

        def add(self, *args: object, **kwargs: object) -> Order:
            raise DuplicateOrderError("x")

    complete = CompleteCheckout(shop.baskets, shop.catalog, Broken(), shop.payments)
    with pytest.raises(DuplicateOrderError):
        complete.execute(1, session_id)


def test_cancel_keeps_the_basket_and_reports_its_size() -> None:
    shop = Shop()
    shop.fill()
    assert CancelCheckout(shop.baskets).execute(1) == 3
    assert shop.baskets.get(1).item_count == 3
    assert shop.orders.orders == []


def test_order_status_values() -> None:
    assert OrderStatus.NEEDS_CONFIRMATION.value == "Needs confirmation"
    assert [s.value for s in OrderStatus][1:] == [
        "Confirmed",
        "Being packed",
        "Shipped",
        "Delivered",
    ]


def test_order_rejects_a_naive_time_and_bad_keys() -> None:
    naive = datetime(2026, 1, 1)  # noqa: DTZ001 - the point of the test
    with pytest.raises(InvalidOrderError):
        Order(1, 1, OrderStatus.CONFIRMED, "cs", Money(1), "eur", naive)
    with pytest.raises(InvalidOrderError):
        Order(0, 1, OrderStatus.CONFIRMED, "cs", Money(1), "eur", NOW)
    with pytest.raises(InvalidOrderError):
        OrderLine(" ", Money(1), 1)
    with pytest.raises(InvalidOrderError):
        OrderLine("x", Money(1), 0)


def test_order_line_total_multiplies() -> None:
    assert OrderLine("x", Money(250), 3).total() == Money(750)
