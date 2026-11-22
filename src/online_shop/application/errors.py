"""@brief The errors the use cases raise."""


class ProductNotFoundError(LookupError):
    """@brief No product has the requested id."""
