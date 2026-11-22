"""Tests of the basket use cases with fake ports."""

import pytest

from fakes import FakeBasketRepository
from online_shop import constants
from online_shop.application.add_to_basket import AddToBasket
from online_shop.application.count_basket_items import CountBasketItems
from online_shop.application.errors import ProductNotFoundError
from online_shop.application.remove_from_basket import RemoveFromBasket
from online_shop.application.update_basket_line import UpdateBasketLine
from online_shop.application.view_basket import ViewBasket
from online_shop.domain.errors import InvalidQuantityError
from online_shop.domain.money import Money
from online_shop.domain.product import Product

MUG = Product(1, "Mug", "Ceramic", Money(1200), "mug.svg")
LAMP = Product(2, "Lamp", "LED", Money(3490), "lamp.svg")
USER = 1


class FakeProducts:
    def __init__(self, *products: Product) -> None:
        self._products = {p.id: p for p in products}

    def list_all(self) -> list[Product]:
        return list(self._products.values())

    def get(self, product_id: int) -> Product | None:
        return self._products.get(product_id)


@pytest.fixture
def baskets() -> FakeBasketRepository:
    return FakeBasketRepository()


@pytest.fixture
def products() -> FakeProducts:
    return FakeProducts(MUG, LAMP)


def test_add_defaults_to_one_and_twice_increases(
    baskets: FakeBasketRepository, products: FakeProducts
) -> None:
    add = AddToBasket(baskets, products)
    add.execute(USER, 1)
    add.execute(USER, 1)
    assert baskets.get(USER).quantity_of(1) == 2


def test_add_unknown_product_is_not_found(
    baskets: FakeBasketRepository, products: FakeProducts
) -> None:
    with pytest.raises(ProductNotFoundError):
        AddToBasket(baskets, products).execute(USER, 99)
    assert baskets.get(USER).lines == ()


def test_add_over_the_limit_is_rejected_and_keeps_the_basket(
    baskets: FakeBasketRepository, products: FakeProducts
) -> None:
    add = AddToBasket(baskets, products)
    add.execute(USER, 1, constants.BASKET_MAX_QUANTITY)
    with pytest.raises(InvalidQuantityError):
        add.execute(USER, 1, 1)
    assert baskets.get(USER).quantity_of(1) == constants.BASKET_MAX_QUANTITY


def test_update_sets_and_zero_removes(
    baskets: FakeBasketRepository, products: FakeProducts
) -> None:
    AddToBasket(baskets, products).execute(USER, 1)
    update = UpdateBasketLine(baskets, products)
    update.execute(USER, 1, 5)
    assert baskets.get(USER).quantity_of(1) == 5
    update.execute(USER, 1, 0)
    assert baskets.get(USER).lines == ()


def test_update_rejects_unknown_product_and_bad_quantity(
    baskets: FakeBasketRepository, products: FakeProducts
) -> None:
    update = UpdateBasketLine(baskets, products)
    with pytest.raises(ProductNotFoundError):
        update.execute(USER, 99, 1)
    with pytest.raises(InvalidQuantityError):
        update.execute(USER, 1, constants.BASKET_MAX_QUANTITY + 1)


def test_remove_drops_the_line(
    baskets: FakeBasketRepository, products: FakeProducts
) -> None:
    AddToBasket(baskets, products).execute(USER, 1)
    RemoveFromBasket(baskets).execute(USER, 1)
    assert baskets.get(USER).lines == ()


def test_baskets_are_per_user(
    baskets: FakeBasketRepository, products: FakeProducts
) -> None:
    AddToBasket(baskets, products).execute(USER, 1, 2)
    assert CountBasketItems(baskets).execute(USER) == 2
    assert CountBasketItems(baskets).execute(2) == 0


def test_view_has_lines_totals_and_count(
    baskets: FakeBasketRepository, products: FakeProducts
) -> None:
    add = AddToBasket(baskets, products)
    add.execute(USER, 1, 2)
    add.execute(USER, 2)
    view = ViewBasket(baskets, products).execute(USER)
    assert [line.name for line in view.lines] == ["Mug", "Lamp"]
    mug = view.lines[0]
    assert (mug.unit_price_cents, mug.quantity, mug.line_total_cents) == (
        1200,
        2,
        2400,
    )
    assert mug.image == "mug.svg"
    assert view.total_cents == 2400 + 3490
    assert view.item_count == 3
    assert view.unavailable_count == 0


def test_view_of_an_empty_basket(
    baskets: FakeBasketRepository, products: FakeProducts
) -> None:
    view = ViewBasket(baskets, products).execute(USER)
    assert (view.lines, view.total_cents, view.item_count) == ((), 0, 0)


def test_view_skips_and_counts_a_vanished_product(
    baskets: FakeBasketRepository, products: FakeProducts
) -> None:
    add = AddToBasket(baskets, products)
    add.execute(USER, 1)
    add.execute(USER, 2, 2)
    view = ViewBasket(baskets, FakeProducts(MUG)).execute(USER)
    assert [line.product_id for line in view.lines] == [1]
    assert view.unavailable_count == 1
    assert view.total_cents == 1200
    assert view.item_count == 1
