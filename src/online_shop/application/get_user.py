"""@brief The use case that fetches the user of a session."""

from online_shop.application.dto import UserDto, to_user_dto
from online_shop.domain.user_repository import UserRepository


class GetUser:
    """@brief Returns one user by key."""

    def __init__(self, users: UserRepository) -> None:
        """@param users The user store."""
        self._users = users

    def execute(self, user_id: int) -> UserDto | None:
        """@brief Return the user, or None when no user has this id."""
        user = self._users.get(user_id)
        return None if user is None else to_user_dto(user)
