"""@brief The use case that opens a payment page for the basket."""

from online_shop import constants
from online_shop.application.errors import EmptyBasketError
from online_shop.application.payment_gateway import (
    CheckoutLineItem,
    CheckoutRequest,
    CheckoutSession,
    PaymentGateway,
)
from online_shop.domain.basket_repository import BasketRepository
from online_shop.domain.product_repository import ProductRepository


def _success_url(base: str) -> str:
    separator = "&" if "?" in base else "?"
    return (
        f"{base}{separator}{constants.CHECKOUT_SESSION_QUERY}="
        f"{constants.CHECKOUT_SESSION_PLACEHOLDER}"
    )


class StartCheckout:
    """@brief Prices the basket at today's prices and asks the gateway to charge it."""

    def __init__(
        self,
        baskets: BasketRepository,
        products: ProductRepository,
        payments: PaymentGateway,
    ) -> None:
        """@param baskets The basket store.  @param products The catalog.
        @param payments The payment gateway.
        """
        self._baskets = baskets
        self._products = products
        self._payments = payments

    def execute(
        self, user_id: int, success_url: str, cancel_url: str
    ) -> CheckoutSession:
        """@brief Open the payment page for the basket of the user.

        @param user_id The signed-in user.
        @param success_url The return address after paying; the session id
            placeholder is appended here.
        @param cancel_url The return address after cancelling.
        @raises EmptyBasketError When no line has a product that is still sold.
        @raises PaymentGatewayError When the provider fails.
        """
        items: list[CheckoutLineItem] = []
        for line in self._baskets.get(user_id).lines:
            product = self._products.get(line.product_id)
            if product is not None:
                items.append(
                    CheckoutLineItem(product.name, product.price.cents, line.quantity)
                )
        if not items:
            raise EmptyBasketError(constants.ERROR_CHECKOUT_EMPTY)
        return self._payments.create_checkout_session(
            CheckoutRequest(
                tuple(items),
                constants.CURRENCY_CODE,
                _success_url(success_url),
                cancel_url,
                str(user_id),
            )
        )
