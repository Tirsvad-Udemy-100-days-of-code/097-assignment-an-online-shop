"""@brief The plain data the use cases hand to the presentation layer."""

from dataclasses import dataclass

from online_shop.domain.product import Product
from online_shop.domain.user import User, UserRole


@dataclass(frozen=True, slots=True)
class ProductDto:
    """@brief A product as the presentation layer sees it.

    @param id The key of the product.
    @param name The name shown to the customer.
    @param description The text that describes the product.
    @param price_cents The price in cents.
    @param image The file name of the product image.
    """

    id: int
    name: str
    description: str
    price_cents: int
    image: str


def to_product_dto(product: Product) -> ProductDto:
    """@brief Map a product entity to its DTO."""
    return ProductDto(
        product.id,
        product.name,
        product.description,
        product.price.cents,
        product.image,
    )


@dataclass(frozen=True, slots=True)
class UserDto:
    """@brief A user as the presentation layer sees it; no password hash.

    @param id The key of the user.
    @param email The normalized email address.
    @param role The role as text, "customer" or "admin".
    """

    id: int
    email: str
    role: str

    @property
    def is_admin(self) -> bool:
        """@brief True when the user has the admin role."""
        return self.role == UserRole.ADMIN


def to_user_dto(user: User) -> UserDto:
    """@brief Map a user entity to its DTO, leaving the hash behind."""
    return UserDto(user.id, user.email, user.role.value)
