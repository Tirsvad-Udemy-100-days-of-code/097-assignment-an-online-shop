"""@brief The user of the current request, for controllers and templates."""

from online_shop.application.dto import UserDto
from online_shop.application.get_user import GetUser
from online_shop.presentation.shared.session import SessionManager


class CurrentUser:
    """@brief Looks up the signed-in user from the session."""

    def __init__(self, get_user: GetUser, sessions: SessionManager) -> None:
        """@param get_user The use case.  @param sessions The session."""
        self._get_user = get_user
        self._sessions = sessions

    def get(self) -> UserDto | None:
        """@brief The signed-in user, or None when anonymous or removed."""
        user_id = self._sessions.user_id()
        return None if user_id is None else self._get_user.execute(user_id)

    def template_context(self) -> dict[str, object]:
        """@brief The variables every template gets: the user and the CSRF token."""
        return {"current_user": self.get(), "csrf_token": self._sessions.csrf_token}
