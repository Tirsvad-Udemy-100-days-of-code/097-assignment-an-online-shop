"""Tests of Money and Product."""

import dataclasses

import pytest

from online_shop.domain.errors import (
    DomainError,
    InvalidMoneyError,
    InvalidProductError,
)
from online_shop.domain.money import Money
from online_shop.domain.product import Product


@pytest.mark.parametrize("cents", [0, 1, 1250])
def test_money_accepts_whole_non_negative_cents(cents: int) -> None:
    assert Money(cents).cents == cents


@pytest.mark.parametrize("cents", [-1, 1.5, "12", True, None])
def test_money_rejects_invalid_amount(cents: object) -> None:
    with pytest.raises(InvalidMoneyError):
        Money(cents)  # type: ignore[arg-type]


def test_money_is_immutable_and_comparable_by_value() -> None:
    assert Money(5) == Money(5)
    with pytest.raises(dataclasses.FrozenInstanceError):
        Money(5).cents = 6  # type: ignore[misc]


def test_domain_errors_are_value_errors() -> None:
    assert issubclass(InvalidMoneyError, DomainError)
    assert issubclass(DomainError, ValueError)


def test_product_holds_its_fields() -> None:
    product = Product(1, "Mug", "Ceramic", Money(1200), "mug.svg")
    assert product.price.cents == 1200


@pytest.mark.parametrize("product_id", [0, -3])
def test_product_rejects_non_positive_id(product_id: int) -> None:
    with pytest.raises(InvalidProductError):
        Product(product_id, "Mug", "", Money(1), "mug.svg")


@pytest.mark.parametrize("name", ["", "   "])
def test_product_rejects_blank_name(name: str) -> None:
    with pytest.raises(InvalidProductError):
        Product(1, name, "", Money(1), "mug.svg")
