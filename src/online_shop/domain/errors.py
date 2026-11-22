"""@brief The errors the business rules raise."""


class DomainError(ValueError):
    """@brief Base of every error raised by a business rule."""


class InvalidMoneyError(DomainError):
    """@brief An amount of money is not a whole, non-negative number of cents."""


class InvalidProductError(DomainError):
    """@brief A product breaks one of its rules."""
