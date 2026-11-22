"""@brief The errors the use cases raise."""


class ProductNotFoundError(LookupError):
    """@brief No product has the requested id."""


class AuthenticationFailedError(Exception):
    """@brief The email or the password is wrong; the reason is never given."""


class EmptyBasketError(Exception):
    """@brief There is nothing to pay for."""


class PaymentGatewayError(Exception):
    """@brief The payment service failed; the message is safe to log."""


class PaymentNotCompletedError(Exception):
    """@brief The payment session is not paid, so no order may be made."""


class ForeignPaymentError(Exception):
    """@brief The payment session belongs to another user."""
