"""@brief The Stripe adapter of the PaymentGateway port, on the standard library."""

import json
import logging
import urllib.error
import urllib.request
from collections.abc import Mapping
from http import HTTPStatus
from typing import Any
from urllib.parse import quote, urlencode, urlsplit

from online_shop import constants
from online_shop.application.errors import PaymentGatewayError
from online_shop.application.payment_gateway import (
    CheckoutRequest,
    CheckoutSession,
    SessionResult,
)

_LOG = logging.getLogger(__name__)

_MSG_UNREACHABLE = "Stripe could not be reached."
_MSG_UNREADABLE = "Stripe sent an answer that could not be read."
_MSG_BAD_URL = "Stripe sent an address that is not allowed."
_MSG_BAD_BASE_URL = "The Stripe base address must be https (http only on 127.0.0.1)."


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect: it would carry the secret key to another host."""

    def redirect_request(self, *args: object, **kwargs: object) -> None:
        return None


def _phrase(code: int) -> str:
    return HTTPStatus(code).phrase if code in HTTPStatus else "error"


def _is_local_http(scheme: str, host: str | None) -> bool:
    return (
        scheme == constants.STRIPE_LOCAL_SCHEME and host in constants.STRIPE_LOCAL_HOSTS
    )


def encode_form(params: Mapping[str, str | int]) -> bytes:
    """@brief Encode flat or bracketed parameters as an urlencoded body."""
    return urlencode(list(params.items()), quote_via=quote).encode("ascii")


def _request_params(request: CheckoutRequest) -> dict[str, str | int]:
    params: dict[str, str | int] = {
        "mode": constants.STRIPE_MODE_PAYMENT,
        "success_url": request.success_url,
        "cancel_url": request.cancel_url,
        "client_reference_id": request.client_reference_id,
    }
    for index, item in enumerate(request.line_items):
        prefix = f"line_items[{index}]"
        params[f"{prefix}[price_data][currency]"] = request.currency
        params[f"{prefix}[price_data][unit_amount]"] = item.unit_amount_cents
        params[f"{prefix}[price_data][product_data][name]"] = item.name
        params[f"{prefix}[quantity]"] = item.quantity
    return params


class StripeGateway:
    """@brief Creates and reads Checkout Sessions through the Stripe REST API."""

    def __init__(
        self,
        secret_key: str,
        base_url: str = constants.STRIPE_API_BASE_URL,
        timeout_seconds: float = constants.STRIPE_TIMEOUT_SECONDS,
    ) -> None:
        """@param secret_key The secret test key; never logged or put in an error.
        @param base_url The API address; https, or http on 127.0.0.1 for tests.
        @param timeout_seconds The limit of each call.
        @raises PaymentGatewayError When the base address is not allowed.
        """
        parts = urlsplit(base_url)
        local = _is_local_http(parts.scheme, parts.hostname)
        if parts.scheme not in constants.STRIPE_ALLOWED_SCHEMES and not local:
            raise PaymentGatewayError(_MSG_BAD_BASE_URL)
        self._allowed_schemes = (
            constants.STRIPE_ALLOWED_SCHEMES | {parts.scheme}
            if local
            else constants.STRIPE_ALLOWED_SCHEMES
        )
        self._base_url = base_url.rstrip("/")
        self._secret_key = secret_key
        self._timeout = timeout_seconds
        self._opener = urllib.request.build_opener(_NoRedirect)

    def __repr__(self) -> str:
        """@brief The class name and base address; the key is left out."""
        return f"StripeGateway(base_url={self._base_url!r})"

    def create_checkout_session(self, request: CheckoutRequest) -> CheckoutSession:
        """@brief Open a Checkout Session whose line items are the request's."""
        data = self._call(
            "POST",
            constants.STRIPE_SESSIONS_PATH,
            encode_form(_request_params(request)),
        )
        session_id, url = data.get("id"), data.get("url")
        if not isinstance(session_id, str) or not isinstance(url, str):
            raise PaymentGatewayError(_MSG_UNREADABLE)
        if urlsplit(url).scheme not in self._allowed_schemes:
            raise PaymentGatewayError(_MSG_BAD_URL)
        return CheckoutSession(session_id, url)

    def retrieve_session(self, session_id: str) -> SessionResult:
        """@brief Read a Checkout Session; paid only when Stripe says `paid`."""
        path = f"{constants.STRIPE_SESSIONS_PATH}/{quote(session_id, safe='')}"
        data = self._call("GET", path, None)
        amount, currency = data.get("amount_total"), data.get("currency")
        reference = data.get("client_reference_id")
        if (
            data.get("id") != session_id
            or isinstance(amount, bool)
            or not isinstance(amount, int)
            or not isinstance(currency, str)
            or not (reference is None or isinstance(reference, str))
        ):
            raise PaymentGatewayError(_MSG_UNREADABLE)
        paid = data.get("payment_status") == constants.STRIPE_PAID_STATUS
        return SessionResult(session_id, paid, amount, currency.lower(), reference)

    def _call(self, method: str, path: str, body: bytes | None) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self._secret_key}"}
        if body is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        http_request = urllib.request.Request(
            self._base_url + path, data=body, headers=headers, method=method
        )
        try:
            with self._opener.open(http_request, timeout=self._timeout) as response:
                raw = response.read(constants.STRIPE_MAX_RESPONSE_BYTES)
        except urllib.error.HTTPError as error:
            _LOG.warning(
                "Stripe answered %s %s with HTTP %s.", method, path, error.code
            )
            error.close()
            raise PaymentGatewayError(
                f"Stripe answered with HTTP {error.code} ({_phrase(error.code)})."
            ) from None
        except (urllib.error.URLError, OSError, ValueError) as error:
            _LOG.warning(
                "Stripe call %s %s failed: %s.", method, path, type(error).__name__
            )
            raise PaymentGatewayError(_MSG_UNREACHABLE) from None
        return self._parse(raw)

    @staticmethod
    def _parse(raw: bytes) -> dict[str, Any]:
        try:
            data = json.loads(raw)
        except ValueError:
            raise PaymentGatewayError(_MSG_UNREADABLE) from None
        if not isinstance(data, dict):
            raise PaymentGatewayError(_MSG_UNREADABLE)
        return data
