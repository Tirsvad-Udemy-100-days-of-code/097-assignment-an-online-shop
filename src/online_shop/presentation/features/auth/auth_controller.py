"""@brief The controller of registration, login and logout."""

from http import HTTPStatus

from flask import Blueprint, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue

from online_shop import constants
from online_shop.application.authenticate_user import AuthenticateUser
from online_shop.application.errors import AuthenticationFailedError
from online_shop.application.register_user import RegisterUser
from online_shop.domain.errors import (
    DuplicateEmailError,
    InvalidEmailError,
    InvalidPasswordError,
)
from online_shop.presentation.shared.redirects import local_path_or
from online_shop.presentation.shared.session import SessionManager


class AuthController:
    """@brief Maps the account forms to the use cases and pages."""

    def __init__(
        self,
        register: RegisterUser,
        authenticate: AuthenticateUser,
        sessions: SessionManager,
    ) -> None:
        """@param register The sign-up use case.
        @param authenticate The sign-in use case.
        @param sessions The session of the request.
        """
        self._register = register
        self._authenticate = authenticate
        self._sessions = sessions

    def show_register(self) -> str:
        """@brief Render the empty registration form."""
        return self._register_page("", {})[0]

    def submit_register(self) -> ResponseReturnValue:
        """@brief Create the account and sign in, or show the field errors."""
        email = request.form.get(constants.FIELD_EMAIL, "")
        password = request.form.get(constants.FIELD_PASSWORD, "")
        try:
            user = self._register.execute(email, password)
        except InvalidEmailError as error:
            return self._register_page(email, {constants.FIELD_EMAIL: str(error)})
        except InvalidPasswordError as error:
            return self._register_page(email, {constants.FIELD_PASSWORD: str(error)})
        except DuplicateEmailError:
            return self._register_page(
                email,
                {constants.FIELD_EMAIL: constants.ERROR_EMAIL_TAKEN},
                HTTPStatus.CONFLICT,
            )
        self._sessions.sign_in(user.id)
        return self._redirect_after_sign_in()

    def show_login(self) -> str:
        """@brief Render the empty login form."""
        return self._login_page("", None)[0]

    def submit_login(self) -> ResponseReturnValue:
        """@brief Sign in, or show one generic error for any wrong credentials."""
        email = request.form.get(constants.FIELD_EMAIL, "")
        password = request.form.get(constants.FIELD_PASSWORD, "")
        try:
            user = self._authenticate.execute(email, password)
        except AuthenticationFailedError as error:
            return self._login_page(email, str(error))
        self._sessions.sign_in(user.id)
        return self._redirect_after_sign_in()

    def logout(self) -> ResponseReturnValue:
        """@brief End the session and go to the home page."""
        self._sessions.sign_out()
        return redirect(url_for("home.show"), HTTPStatus.SEE_OTHER)

    def _next_url(self) -> str:
        target = request.form.get(constants.FIELD_NEXT) or request.args.get(
            constants.FIELD_NEXT
        )
        return local_path_or(target, "")

    def _redirect_after_sign_in(self) -> ResponseReturnValue:
        target = self._next_url() or url_for("home.show")
        return redirect(target, HTTPStatus.SEE_OTHER)

    def _register_page(
        self,
        email: str,
        errors: dict[str, str],
        status: HTTPStatus | None = None,
    ) -> tuple[str, int]:
        status = status or (HTTPStatus.BAD_REQUEST if errors else HTTPStatus.OK)
        body = render_template(
            "auth/register.html",
            title=constants.TEXT_REGISTER,
            email=email,
            errors=errors,
            next_url=self._next_url(),
        )
        return body, status

    def _login_page(self, email: str, error: str | None) -> tuple[str, int]:
        status = HTTPStatus.OK if error is None else HTTPStatus.UNAUTHORIZED
        body = render_template(
            "auth/login.html",
            title=constants.TEXT_LOGIN,
            email=email,
            form_error=error,
            next_url=self._next_url(),
        )
        return body, status


def create_auth_blueprint(
    register: RegisterUser,
    authenticate: AuthenticateUser,
    sessions: SessionManager,
) -> Blueprint:
    """@brief Build the blueprint "auth" with /register, /login and /logout."""
    blueprint = Blueprint("auth", __name__)
    controller = AuthController(register, authenticate, sessions)
    routes = (
        ("/register", "register", controller.show_register, ["GET"]),
        ("/register", "register_submit", controller.submit_register, ["POST"]),
        ("/login", "login", controller.show_login, ["GET"]),
        ("/login", "login_submit", controller.submit_login, ["POST"]),
        ("/logout", "logout", controller.logout, ["POST"]),
    )
    for rule, endpoint, view, methods in routes:
        blueprint.add_url_rule(rule, endpoint=endpoint, view_func=view, methods=methods)
    return blueprint
