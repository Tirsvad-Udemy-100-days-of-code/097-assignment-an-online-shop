"""Tests of the Basket and BasketLine rules: limits, merging and totals."""

import pytest

from online_shop import constants
from online_shop.domain.basket import Basket, BasketLine
from online_shop.domain.errors import (
    DomainError,
    InvalidBasketError,
    InvalidQuantityError,
)
from online_shop.domain.money import Money

MAX = constants.BASKET_MAX_QUANTITY


def test_new_basket_is_empty() -> None:
    basket = Basket(1)
    assert basket.lines == ()
    assert basket.item_count == 0
    assert basket.total({}) == Money(0)


def test_adding_a_product_twice_increases_the_quantity() -> None:
    basket = Basket(1).add(7, 1).add(7, 2)
    assert basket.lines == (BasketLine(7, 3),)
    assert basket.quantity_of(7) == 3


def test_add_keeps_the_order_of_first_adding() -> None:
    basket = Basket(1).add(7, 1).add(3, 1).add(7, 1)
    assert [line.product_id for line in basket.lines] == [7, 3]


def test_set_quantity_changes_the_line() -> None:
    assert Basket(1).add(7, 1).set_quantity(7, 5).quantity_of(7) == 5


def test_set_quantity_to_zero_removes_the_line() -> None:
    assert Basket(1).add(7, 2).set_quantity(7, 0).lines == ()


def test_set_quantity_on_a_new_product_adds_a_line() -> None:
    assert Basket(1).set_quantity(4, 2).lines == (BasketLine(4, 2),)


def test_set_quantity_zero_on_an_absent_product_does_nothing() -> None:
    assert Basket(1).set_quantity(4, 0) == Basket(1)


def test_remove_drops_only_that_line_and_ignores_absent_ones() -> None:
    basket = Basket(1).add(1, 1).add(2, 1)
    assert basket.remove(1).lines == (BasketLine(2, 1),)
    assert basket.remove(9) == basket


def test_basket_is_immutable() -> None:
    basket = Basket(1)
    basket.add(1, 1)
    assert basket.lines == ()


@pytest.mark.parametrize("quantity", [1, 2, MAX])
def test_add_accepts_quantities_up_to_the_maximum(quantity: int) -> None:
    assert Basket(1).add(1, quantity).item_count == quantity


@pytest.mark.parametrize("quantity", [0, -1])
def test_add_rejects_a_quantity_below_one(quantity: int) -> None:
    with pytest.raises(InvalidQuantityError, match="whole number"):
        Basket(1).add(1, quantity)


def test_add_rejects_a_quantity_above_the_maximum() -> None:
    with pytest.raises(InvalidQuantityError) as error:
        Basket(1).add(1, MAX + 1)
    assert str(error.value) == constants.ERROR_QUANTITY_LIMIT


def test_adding_beyond_the_maximum_in_two_steps_is_rejected() -> None:
    basket = Basket(1).add(1, MAX)
    with pytest.raises(InvalidQuantityError):
        basket.add(1, 1)


@pytest.mark.parametrize("quantity", [-1, MAX + 1])
def test_set_quantity_rejects_values_outside_zero_to_maximum(quantity: int) -> None:
    with pytest.raises(InvalidQuantityError):
        Basket(1).set_quantity(1, quantity)


def test_set_quantity_accepts_the_maximum() -> None:
    assert Basket(1).set_quantity(1, MAX).quantity_of(1) == MAX


@pytest.mark.parametrize("quantity", [True, 1.5, "2"])
def test_quantity_must_be_an_integer(quantity: object) -> None:
    with pytest.raises(InvalidQuantityError):
        Basket(1).add(1, quantity)  # type: ignore[arg-type]


def test_line_rejects_a_bad_product_id() -> None:
    with pytest.raises(InvalidBasketError):
        BasketLine(0, 1)


def test_basket_rejects_a_bad_owner() -> None:
    with pytest.raises(InvalidBasketError):
        Basket(0)


def test_errors_are_domain_errors() -> None:
    assert issubclass(InvalidQuantityError, DomainError)
    assert issubclass(InvalidBasketError, DomainError)


def test_total_is_the_sum_of_price_times_quantity_in_cents() -> None:
    basket = Basket(1).add(1, 2).add(2, 3)
    prices = {1: Money(1250), 2: Money(199)}
    assert basket.total(prices) == Money(2 * 1250 + 3 * 199)
    assert BasketLine(1, 2).total(Money(1250)) == Money(2500)


def test_total_skips_a_line_without_a_price() -> None:
    basket = Basket(1).add(1, 2).add(2, 3)
    assert basket.total({1: Money(100)}) == Money(200)


def test_item_count_is_the_sum_of_quantities() -> None:
    assert Basket(1).add(1, 2).add(2, 3).item_count == 5
