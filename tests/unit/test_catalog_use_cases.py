"""Tests of the catalog use cases with a fake repository."""

import pytest

from online_shop.application.dto import ProductDto
from online_shop.application.errors import ProductNotFoundError
from online_shop.application.get_product import GetProduct
from online_shop.application.list_products import ListProducts
from online_shop.domain.money import Money
from online_shop.domain.product import Product


class FakeProductRepository:
    def __init__(self, products: list[Product]) -> None:
        self._products = products

    def list_all(self) -> list[Product]:
        return list(self._products)

    def get(self, product_id: int) -> Product | None:
        return next((p for p in self._products if p.id == product_id), None)


MUG = Product(1, "Mug", "Ceramic", Money(1200), "mug.svg")
LAMP = Product(2, "Lamp", "LED", Money(3490), "lamp.svg")


def test_list_products_returns_dtos_in_order() -> None:
    result = ListProducts(FakeProductRepository([MUG, LAMP])).execute()
    assert result == [
        ProductDto(1, "Mug", "Ceramic", 1200, "mug.svg"),
        ProductDto(2, "Lamp", "LED", 3490, "lamp.svg"),
    ]


def test_list_products_returns_empty_list_for_empty_catalog() -> None:
    assert ListProducts(FakeProductRepository([])).execute() == []


def test_get_product_returns_dto() -> None:
    result = GetProduct(FakeProductRepository([MUG, LAMP])).execute(2)
    assert result == ProductDto(2, "Lamp", "LED", 3490, "lamp.svg")


def test_get_product_raises_for_unknown_id() -> None:
    with pytest.raises(ProductNotFoundError):
        GetProduct(FakeProductRepository([MUG])).execute(99)
