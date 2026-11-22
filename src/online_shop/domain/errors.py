"""@brief The errors the business rules raise."""


class DomainError(ValueError):
    """@brief Base of every error raised by a business rule."""


class InvalidMoneyError(DomainError):
    """@brief An amount of money is not a whole, non-negative number of cents."""


class InvalidProductError(DomainError):
    """@brief A product breaks one of its rules."""


class InvalidUserError(DomainError):
    """@brief A user breaks one of its rules."""


class InvalidEmailError(DomainError):
    """@brief An email address is not acceptable."""


class InvalidPasswordError(DomainError):
    """@brief A password is not acceptable."""


class DuplicateEmailError(DomainError):
    """@brief An account with this email already exists."""


class InvalidQuantityError(DomainError):
    """@brief A basket quantity is not a whole number inside the limits."""


class InvalidBasketError(DomainError):
    """@brief A basket or a basket line breaks one of its rules."""


class InvalidOrderError(DomainError):
    """@brief An order or an order line breaks one of its rules."""


class DuplicateOrderError(DomainError):
    """@brief An order for this payment session already exists."""
