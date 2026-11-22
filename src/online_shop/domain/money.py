"""@brief The Money value object."""

from dataclasses import dataclass

from online_shop.domain.errors import InvalidMoneyError


@dataclass(frozen=True, slots=True)
class Money:
    """@brief An amount in whole minor units (cents); never a float.

    @param cents The amount in cents, zero or more.
    """

    cents: int

    def __post_init__(self) -> None:
        """@brief Reject an amount that is not a non-negative integer."""
        if isinstance(self.cents, bool) or not isinstance(self.cents, int):
            raise InvalidMoneyError("Money must be a whole number of cents.")
        if self.cents < 0:
            raise InvalidMoneyError("Money cannot be negative.")
