"""@brief The controller of the admin order board: the page and its JSON API."""

from http import HTTPStatus

from flask import Blueprint, jsonify, render_template, request
from flask.typing import ResponseReturnValue

from online_shop import constants
from online_shop.application.dto import BoardCardDto, BoardDto
from online_shop.application.errors import InvalidMoveError, OrderNotFoundError
from online_shop.application.move_order import MoveOrder
from online_shop.application.view_board import ViewBoard
from online_shop.presentation.shared.admin_access import AdminAccess
from online_shop.presentation.shared.formatting import format_price


def _card_json(card: BoardCardDto) -> dict[str, object]:
    return {
        "order_id": card.order_id,
        "customer_email": card.customer_email,
        "items": list(card.items),
        "total_cents": card.total_cents,
        "total": format_price(card.total_cents),
        "created_at": card.created_at.isoformat(),
        "created": card.created_at.strftime(constants.DATETIME_FORMAT),
    }


def _board_json(board: BoardDto) -> dict[str, object]:
    return {
        "columns": [
            {
                "status": column.status,
                "count": len(column.cards),
                "cards": [_card_json(card) for card in column.cards],
            }
            for column in board.columns
        ]
    }


def _whole_number(value: object) -> int | None:
    # bool is an int in Python, but true is not an order number.
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    return None


def _parse_move(body: object) -> tuple[int, str, int] | None:
    """The order id, status and index of a move body, or None when malformed."""
    if not isinstance(body, dict):
        return None
    order_id = _whole_number(body.get("order_id"))
    index = _whole_number(body.get("index"))
    status = body.get("status")
    if order_id is None or index is None or not isinstance(status, str):
        return None
    return order_id, status, index


class BoardController:
    """@brief Maps the board requests to the use cases; admins only."""

    def __init__(
        self, access: AdminAccess, view: ViewBoard, move_order: MoveOrder
    ) -> None:
        """@param access The admin check.  @param view The board use case.
        @param move_order The move use case.
        """
        self._access = access
        self._view = view
        self._move_order = move_order

    def page(self) -> ResponseReturnValue:
        """@brief The board page; the script loads the cards from the API."""
        denied = self._access.page_denial()
        if denied is not None:
            return denied
        return render_template(
            "admin/board.html",
            title=constants.TEXT_BOARD_TITLE,
            api={"board": constants.BOARD_API_PATH, "move": constants.BOARD_MOVE_PATH},
            texts={
                "heading": constants.TEXT_BOARD_TITLE,
                "move_to": constants.TEXT_BOARD_MOVE_TO,
                "order": constants.TEXT_BOARD_ORDER,
                "move_failed": constants.TEXT_BOARD_MOVE_FAILED,
                "load_failed": constants.TEXT_BOARD_LOAD_FAILED,
                "empty": constants.TEXT_BOARD_EMPTY_COLUMN,
            },
        )

    def data(self) -> ResponseReturnValue:
        """@brief The five columns with their cards as JSON."""
        denied = self._access.api_denial()
        if denied is not None:
            return denied
        return jsonify(_board_json(self._view.execute()))

    def move(self) -> ResponseReturnValue:
        """@brief Move one order; the body is {order_id, status, index}."""
        denied = self._access.api_denial()
        if denied is not None:
            return denied
        parsed = _parse_move(request.get_json(silent=True))
        if parsed is None:
            return self._error(HTTPStatus.BAD_REQUEST, constants.ERROR_MOVE_BODY)
        try:
            self._move_order.execute(*parsed)
        except InvalidMoveError as error:
            return self._error(HTTPStatus.BAD_REQUEST, str(error))
        except OrderNotFoundError as error:
            return self._error(HTTPStatus.NOT_FOUND, str(error))
        return jsonify(_board_json(self._view.execute()))

    @staticmethod
    def _error(status: HTTPStatus, message: str) -> ResponseReturnValue:
        return jsonify(error=message), status


def create_board_blueprint(
    access: AdminAccess, view: ViewBoard, move_order: MoveOrder
) -> Blueprint:
    """@brief Build the blueprint "board": the page and the two API routes."""
    blueprint = Blueprint("board", __name__)
    controller = BoardController(access, view, move_order)
    routes = (
        ("/admin/board", "page", controller.page, "GET"),
        (constants.BOARD_API_PATH, "data", controller.data, "GET"),
        (constants.BOARD_MOVE_PATH, "move", controller.move, "POST"),
    )
    for rule, endpoint, handler, method in routes:
        blueprint.add_url_rule(
            rule, endpoint=endpoint, view_func=handler, methods=[method]
        )
    return blueprint
