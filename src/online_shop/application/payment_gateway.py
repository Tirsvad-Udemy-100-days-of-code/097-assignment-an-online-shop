"""@brief The port through which the business takes payment, and its data."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class CheckoutLineItem:
    """@brief One line to pay: name, price of one piece in cents, pieces."""

    name: str
    unit_amount_cents: int
    quantity: int


@dataclass(frozen=True, slots=True)
class CheckoutRequest:
    """@brief What the gateway needs to open a payment page.

    @param line_items The lines to pay.
    @param currency The lower case ISO currency code.
    @param success_url Where the customer returns after paying.
    @param cancel_url Where the customer returns after cancelling.
    @param client_reference_id The shop's own reference, the user id.
    """

    line_items: tuple[CheckoutLineItem, ...]
    currency: str
    success_url: str
    cancel_url: str
    client_reference_id: str


@dataclass(frozen=True, slots=True)
class CheckoutSession:
    """@brief An open payment page: its id and the address to send the customer to."""

    id: str
    url: str


@dataclass(frozen=True, slots=True)
class SessionResult:
    """@brief The state of a payment session as the provider reports it.

    @param id The session id.
    @param paid True only when the money was taken.
    @param amount_total The amount in minor units.
    @param currency The lower case ISO currency code.
    @param client_reference_id The reference sent when the session was made.
    """

    id: str
    paid: bool
    amount_total: int
    currency: str
    client_reference_id: str | None


class PaymentGateway(Protocol):
    """@brief Opens and reads payment sessions; an adapter implements it."""

    def create_checkout_session(self, request: CheckoutRequest) -> CheckoutSession:
        """@brief Open a payment page.

        @raises PaymentGatewayError When the provider fails.
        """
        ...

    def retrieve_session(self, session_id: str) -> SessionResult:
        """@brief Read a session back from the provider.

        @raises PaymentGatewayError When the provider fails.
        """
        ...
