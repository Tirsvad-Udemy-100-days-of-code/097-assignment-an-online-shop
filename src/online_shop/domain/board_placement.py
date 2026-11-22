"""@brief The rule that places an order in a board column."""

from collections.abc import Mapping, Sequence

from online_shop.domain.order import OrderStatus


def place_order(
    columns: Mapping[OrderStatus, Sequence[int]],
    order_id: int,
    status: OrderStatus,
    index: int,
) -> dict[OrderStatus, list[int]]:
    """@brief Move one order to a column and index; return every column's order ids.

    Any column to any column is allowed. The index counts the cards of the
    target column without the moved one and is limited to the column's ends, so
    a position past the end puts the card last. Positions are the list indexes.

    @param columns The order ids of each status, in position order.
    @param order_id The order to move; it must be in one column.
    @param status The target column.
    @param index The wanted place in the target column.
    @return The new ids of each status; the input is left unchanged.
    """
    placed = {key: [i for i in ids if i != order_id] for key, ids in columns.items()}
    target = placed.setdefault(status, [])
    target.insert(max(0, min(index, len(target))), order_id)
    return placed
