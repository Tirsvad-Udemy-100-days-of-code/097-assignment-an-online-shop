"""@brief The signed session cookie: sign-in state and the CSRF token."""

import hmac
import secrets
from datetime import timedelta

from flask import Flask, session

from online_shop import constants


def configure_sessions(app: Flask, secret_key: str) -> None:
    """@brief Sign the session cookie and set its security attributes.

    @param app The Flask application.
    @param secret_key The key that signs the cookie.
    """
    app.config.update(
        SECRET_KEY=secret_key,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE=constants.SESSION_COOKIE_SAMESITE,
        PERMANENT_SESSION_LIFETIME=timedelta(
            seconds=constants.SESSION_LIFETIME_SECONDS
        ),
    )


def _new_token() -> str:
    return secrets.token_urlsafe(constants.CSRF_TOKEN_BYTES)


class SessionManager:
    """@brief Reads and changes the session of the current request."""

    def user_id(self) -> int | None:
        """@brief The signed-in user's key, or None when anonymous."""
        value = session.get(constants.SESSION_USER_KEY)
        return value if isinstance(value, int) else None

    def sign_in(self, user_id: int) -> None:
        """@brief Start a fresh session for the user.

        The old session is dropped first so a pre-login session id or token
        cannot be reused (session fixation).
        """
        session.clear()
        session[constants.SESSION_USER_KEY] = user_id
        session[constants.SESSION_CSRF_KEY] = _new_token()
        session.permanent = True

    def sign_out(self) -> None:
        """@brief Drop everything in the session; the cookie is cleared."""
        session.clear()

    def csrf_token(self) -> str:
        """@brief The CSRF token of this session, created on first use."""
        token = session.get(constants.SESSION_CSRF_KEY)
        if not isinstance(token, str) or not token:
            token = _new_token()
            session[constants.SESSION_CSRF_KEY] = token
            session.permanent = True
        return token

    def accepts_csrf_token(self, submitted: str) -> bool:
        """@brief True when the token matches the session's (constant time)."""
        expected = session.get(constants.SESSION_CSRF_KEY)
        if not isinstance(expected, str) or not expected or not submitted:
            return False
        return hmac.compare_digest(expected.encode("utf-8"), submitted.encode("utf-8"))
