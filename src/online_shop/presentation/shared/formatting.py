"""@brief Text formatting used by the templates of several features."""

from datetime import datetime

from online_shop import constants


def format_price(price_cents: int) -> str:
    """@brief Write an amount in cents as text, for example 12.50 with the symbol."""
    major, minor = divmod(price_cents, constants.MINOR_UNITS_PER_MAJOR)
    return f"{constants.CURRENCY_SYMBOL}{major}.{minor:02d}"


def format_date(moment: datetime) -> str:
    """@brief Write the day of a time as text."""
    return moment.strftime(constants.DATE_FORMAT)


def status_slug(status: str) -> str:
    """@brief A CSS-safe name for an order status label, for example "being-packed"."""
    return status.lower().replace(" ", "-")
