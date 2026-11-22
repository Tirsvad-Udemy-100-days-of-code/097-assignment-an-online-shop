"""@brief The controller of the checkout button and the two pages Stripe returns to."""

import logging
from http import HTTPStatus

from flask import Blueprint, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

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
from online_shop.presentation.shared.current_user import CurrentUser
from online_shop.presentation.shared.errors import error_page
from online_shop.presentation.shared.redirects import local_path_or

_LOG = logging.getLogger(__name__)


class CheckoutController:
    """@brief Maps checkout requests to the use cases.

    Without payment use cases (Stripe not configured) every payment route
    answers 503 and the cancel page still works.
    """

    def __init__(
        self,
        current_user: CurrentUser,
        start: StartCheckout | None,
        complete: CompleteCheckout | None,
        cancel: CancelCheckout,
    ) -> None:
        """@param current_user The signed-in user of the request.
        @param start The use case that opens the payment page, or None.
        @param complete The use case that makes the order, or None.
        @param cancel The use case for a cancelled payment.
        """
        self._current_user = current_user
        self._start = start
        self._complete = complete
        self._cancel = cancel

    def begin(self) -> ResponseReturnValue:
        """@brief Open the Stripe payment page for the basket."""
        user = self._current_user.get()
        if user is None:
            return self._to_login(url_for("basket.show"))
        if self._start is None:
            return error_page(
                HTTPStatus.SERVICE_UNAVAILABLE, constants.ERROR_CHECKOUT_UNAVAILABLE
            )
        try:
            session = self._start.execute(
                user.id,
                url_for("checkout.success", _external=True),
                url_for("checkout.cancel", _external=True),
            )
        except EmptyBasketError:
            return error_page(HTTPStatus.BAD_REQUEST, constants.ERROR_CHECKOUT_EMPTY)
        except PaymentGatewayError as error:
            _LOG.warning("Checkout could not start: %s", error)
            return error_page(HTTPStatus.BAD_GATEWAY, constants.ERROR_CHECKOUT_GATEWAY)
        return redirect(session.url, HTTPStatus.SEE_OTHER)

    def success(self) -> ResponseReturnValue:
        """@brief Confirm the payment and show the order; unpaid shows an error."""
        session_id = request.args.get(constants.CHECKOUT_SESSION_QUERY, "")
        user = self._current_user.get()
        if user is None:
            here = local_path_or(request.full_path.rstrip("?"), url_for("basket.show"))
            return self._to_login(here)
        if self._complete is None:
            return error_page(
                HTTPStatus.SERVICE_UNAVAILABLE, constants.ERROR_CHECKOUT_UNAVAILABLE
            )
        try:
            order = self._complete.execute(user.id, session_id)
        except ForeignPaymentError:
            return error_page(HTTPStatus.FORBIDDEN, constants.ERROR_CHECKOUT_FOREIGN)
        except PaymentNotCompletedError as error:
            return error_page(HTTPStatus.BAD_REQUEST, str(error))
        except PaymentGatewayError as error:
            _LOG.warning("Checkout could not be confirmed: %s", error)
            return error_page(HTTPStatus.BAD_GATEWAY, constants.ERROR_CHECKOUT_GATEWAY)
        return render_template(
            "checkout/success.html",
            title=constants.TEXT_CHECKOUT_SUCCESS_TITLE,
            order=order,
            texts={
                "heading": constants.TEXT_CHECKOUT_SUCCESS_TITLE,
                "number": constants.TEXT_CHECKOUT_ORDER_NUMBER,
                "status": constants.TEXT_CHECKOUT_STATUS,
                "total": constants.TEXT_CHECKOUT_TOTAL,
                "continue": constants.TEXT_BASKET_CONTINUE,
                "orders": constants.TEXT_ORDERS_VIEW,
            },
        )

    def cancel(self) -> ResponseReturnValue:
        """@brief Say that nothing was paid and the basket is kept."""
        user = self._current_user.get()
        if user is None:
            return self._to_login(url_for("checkout.cancel"))
        kept = self._cancel.execute(user.id)
        return render_template(
            "checkout/cancel.html",
            title=constants.TEXT_CHECKOUT_CANCEL_TITLE,
            kept=kept,
            texts={
                "heading": constants.TEXT_CHECKOUT_CANCEL_TITLE,
                "body": constants.TEXT_CHECKOUT_CANCEL_BODY,
                "kept": constants.TEXT_CHECKOUT_CANCEL_KEPT,
                "to_basket": constants.TEXT_CHECKOUT_TO_BASKET,
            },
        )

    @staticmethod
    def _to_login(target: str) -> ResponseReturnValue:
        return redirect(url_for("auth.login", next=target), HTTPStatus.SEE_OTHER)


def create_checkout_blueprint(
    current_user: CurrentUser,
    start: StartCheckout | None,
    complete: CompleteCheckout | None,
    cancel: CancelCheckout,
) -> Blueprint:
    """@brief Build the blueprint "checkout": POST /checkout and the two returns."""
    blueprint = Blueprint("checkout", __name__)
    controller = CheckoutController(current_user, start, complete, cancel)
    routes = (
        ("/checkout", "begin", controller.begin, "POST"),
        ("/checkout/success", "success", controller.success, "GET"),
        ("/checkout/cancel", "cancel", controller.cancel, "GET"),
    )
    for rule, endpoint, handler, method in routes:
        blueprint.add_url_rule(
            rule, endpoint=endpoint, view_func=handler, methods=[method]
        )
    return blueprint
