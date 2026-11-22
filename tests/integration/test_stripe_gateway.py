"""Tests of the Stripe adapter against a local fake Stripe server (no network)."""

import json
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest

from fakes import fake_key
from online_shop.application.errors import PaymentGatewayError
from online_shop.application.payment_gateway import CheckoutLineItem, CheckoutRequest
from online_shop.infrastructure.stripe_gateway import StripeGateway, encode_form

KEY = fake_key("sk", "test", "unit" * 8)
REQUEST = CheckoutRequest(
    (CheckoutLineItem("Mug & co", 1205, 2), CheckoutLineItem("Lamp", 3490, 1)),
    "eur",
    "https://shop.test/ok?session_id={CHECKOUT_SESSION_ID}",
    "https://shop.test/cancel",
    "7",
)


class FakeStripe(ThreadingHTTPServer):
    """Answers with whatever `reply` holds and records what it was asked."""

    def __init__(self) -> None:
        super().__init__(("127.0.0.1", 0), _Handler)
        self.reply: tuple[int, bytes] = (200, b"{}")
        self.seen: list[tuple[str, str, dict[str, str], bytes]] = []
        self.hold: threading.Event | None = None
        self.redirect_to: str | None = None


class _Handler(BaseHTTPRequestHandler):
    server: FakeStripe

    def _answer(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length)
        headers = {k.lower(): v for k, v in self.headers.items()}
        if self.server.hold is not None:
            self.server.hold.wait(5)
        self.server.seen.append((self.command, self.path, headers, body))
        if self.server.redirect_to:
            self.send_response(302)
            self.send_header("Location", self.server.redirect_to)
            self.end_headers()
            return
        status, payload = self.server.reply
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802 - the name http.server looks up
        self._answer()

    def do_POST(self) -> None:  # noqa: N802 - the name http.server looks up
        self._answer()

    def log_message(self, format: str, *args: object) -> None:
        return None


@pytest.fixture
def stripe() -> Iterator[FakeStripe]:
    server = FakeStripe()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()


def gateway_for(server: FakeStripe, timeout: float = 5) -> StripeGateway:
    port = server.server_address[1]
    return StripeGateway(KEY, f"http://127.0.0.1:{port}", timeout)


def reply(server: FakeStripe, status: int, body: object) -> None:
    server.reply = (status, json.dumps(body).encode())


def test_create_session_posts_the_form_with_the_bearer_key(stripe: FakeStripe) -> None:
    reply(stripe, 200, {"id": "cs_test_1", "url": "http://127.0.0.1/pay"})
    session = gateway_for(stripe).create_checkout_session(REQUEST)
    assert (session.id, session.url) == ("cs_test_1", "http://127.0.0.1/pay")
    method, path, headers, body = stripe.seen[0]
    assert (method, path) == ("POST", "/v1/checkout/sessions")
    assert headers["authorization"] == f"Bearer {KEY}"
    assert headers["content-type"] == "application/x-www-form-urlencoded"
    form = {k: v[0] for k, v in parse_qs(body.decode(), strict_parsing=True).items()}
    assert form == {
        "mode": "payment",
        "success_url": REQUEST.success_url,
        "cancel_url": REQUEST.cancel_url,
        "client_reference_id": "7",
        "line_items[0][price_data][currency]": "eur",
        "line_items[0][price_data][unit_amount]": "1205",
        "line_items[0][price_data][product_data][name]": "Mug & co",
        "line_items[0][quantity]": "2",
        "line_items[1][price_data][currency]": "eur",
        "line_items[1][price_data][unit_amount]": "3490",
        "line_items[1][price_data][product_data][name]": "Lamp",
        "line_items[1][quantity]": "1",
    }


def test_encode_form_escapes_reserved_characters() -> None:
    assert encode_form({"a[b]": "x y&z=1"}) == b"a%5Bb%5D=x%20y%26z%3D1"


def test_retrieve_session_reads_a_paid_session(stripe: FakeStripe) -> None:
    reply(
        stripe,
        200,
        {
            "id": "cs_test_1",
            "payment_status": "paid",
            "amount_total": 5900,
            "currency": "EUR",
            "client_reference_id": "7",
        },
    )
    result = gateway_for(stripe).retrieve_session("cs_test_1")
    assert result.paid
    assert (result.amount_total, result.currency) == (5900, "eur")
    assert result.client_reference_id == "7"
    method, path, headers, _ = stripe.seen[0]
    assert (method, path) == ("GET", "/v1/checkout/sessions/cs_test_1")
    assert headers["authorization"] == f"Bearer {KEY}"


@pytest.mark.parametrize("status", ["unpaid", "no_payment_required", None])
def test_retrieve_session_is_unpaid_unless_stripe_says_paid(
    stripe: FakeStripe, status: str | None
) -> None:
    reply(
        stripe,
        200,
        {
            "id": "cs_1",
            "payment_status": status,
            "amount_total": 1,
            "currency": "eur",
            "client_reference_id": None,
        },
    )
    result = gateway_for(stripe).retrieve_session("cs_1")
    assert not result.paid
    assert result.client_reference_id is None


def test_session_id_is_quoted_in_the_path(stripe: FakeStripe) -> None:
    reply(stripe, 404, {"error": {"message": "nope"}})
    with pytest.raises(PaymentGatewayError):
        gateway_for(stripe).retrieve_session("../x?y=1")
    assert urlsplit(stripe.seen[0][1]).path == "/v1/checkout/sessions/..%2Fx%3Fy%3D1"


def test_http_error_becomes_a_safe_message(stripe: FakeStripe) -> None:
    reply(stripe, 401, {"error": {"message": f"Invalid API Key {KEY}"}})
    with pytest.raises(PaymentGatewayError) as error:
        gateway_for(stripe).create_checkout_session(REQUEST)
    assert "401" in str(error.value)
    assert KEY not in str(error.value)
    assert "Invalid API Key" not in str(error.value)


def test_unreadable_json_is_an_error(stripe: FakeStripe) -> None:
    stripe.reply = (200, b"<html>not json " + KEY.encode())
    with pytest.raises(PaymentGatewayError) as error:
        gateway_for(stripe).create_checkout_session(REQUEST)
    assert KEY not in str(error.value)


@pytest.mark.parametrize(
    "body",
    [
        [],
        {"id": "cs"},
        {"id": 1, "url": "http://127.0.0.1/x"},
        {"id": "cs", "url": "javascript:alert(1)"},
        {"id": "cs", "url": "ftp://x/y"},
    ],
)
def test_create_rejects_a_bad_answer(stripe: FakeStripe, body: object) -> None:
    reply(stripe, 200, body)
    with pytest.raises(PaymentGatewayError):
        gateway_for(stripe).create_checkout_session(REQUEST)


@pytest.mark.parametrize(
    "body",
    [
        {"id": "other", "amount_total": 1, "currency": "eur"},
        {"id": "cs_1", "amount_total": "1", "currency": "eur"},
        {"id": "cs_1", "amount_total": True, "currency": "eur"},
        {"id": "cs_1", "amount_total": 1, "currency": 3},
        {"id": "cs_1", "amount_total": 1, "currency": "eur", "client_reference_id": 5},
    ],
)
def test_retrieve_rejects_a_bad_answer(stripe: FakeStripe, body: object) -> None:
    reply(stripe, 200, body)
    with pytest.raises(PaymentGatewayError):
        gateway_for(stripe).retrieve_session("cs_1")


def test_a_slow_server_times_out(stripe: FakeStripe) -> None:
    stripe.hold = threading.Event()
    try:
        with pytest.raises(PaymentGatewayError):
            gateway_for(stripe, timeout=0.2).create_checkout_session(REQUEST)
    finally:
        stripe.hold.set()


def test_a_refused_connection_is_an_error() -> None:
    server = FakeStripe()
    gateway = gateway_for(server)
    server.server_close()
    with pytest.raises(PaymentGatewayError) as error:
        gateway.retrieve_session("cs_1")
    assert KEY not in str(error.value)


def test_a_redirect_is_not_followed_so_the_key_stays_put(stripe: FakeStripe) -> None:
    other = FakeStripe()
    thread = threading.Thread(target=other.serve_forever, daemon=True)
    thread.start()
    try:
        stripe.redirect_to = f"http://127.0.0.1:{other.server_address[1]}/steal"
        with pytest.raises(PaymentGatewayError):
            gateway_for(stripe).retrieve_session("cs_1")
        assert other.seen == []
    finally:
        other.shutdown()
        other.server_close()


@pytest.mark.parametrize(
    "base",
    [
        "http://api.stripe.com",
        "http://localhost:1",
        "ftp://127.0.0.1",
        "file:///etc/passwd",
        "//127.0.0.1",
    ],
)
def test_base_address_must_be_https_or_local_http(base: str) -> None:
    with pytest.raises(PaymentGatewayError):
        StripeGateway(KEY, base)


def test_https_base_address_is_accepted_and_the_key_is_not_in_repr() -> None:
    gateway = StripeGateway(KEY)
    assert "api.stripe.com" in repr(gateway)
    assert KEY not in repr(gateway)
