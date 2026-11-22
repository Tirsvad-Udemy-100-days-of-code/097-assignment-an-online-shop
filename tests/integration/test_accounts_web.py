"""Tests of sessions, CSRF, the account pages and the admin guard on the real app."""

import re
from pathlib import Path

import pytest
from flask.testing import FlaskClient

from online_shop import constants
from online_shop.infrastructure.settings import Settings
from online_shop.presentation.app import create_app

PASSWORD = "correct horse"
ADMIN_EMAIL = "root@example.com"
ADMIN_PASSWORD = "admin password"
SEE_OTHER = 303


@pytest.fixture
def client(tmp_path: Path) -> FlaskClient:
    settings = Settings("test-key", ADMIN_EMAIL, ADMIN_PASSWORD)
    return create_app(tmp_path / "shop.sqlite3", settings).test_client()


def token_of(client: FlaskClient, path: str = "/login") -> str:
    html = client.get(path).get_data(as_text=True)
    match = re.search(r'name="csrf_token" value="([^"]+)"', html)
    assert match
    return match.group(1)


def post(client: FlaskClient, path: str, **fields: str) -> object:
    data = {constants.CSRF_FORM_FIELD: token_of(client, path), **fields}
    return client.post(path, data=data)


def register(client: FlaskClient, email: str = "ann@example.com") -> object:
    return post(client, "/register", email=email, password=PASSWORD)


def test_register_signs_in_and_header_shows_the_email(client: FlaskClient) -> None:
    response = register(client)
    assert response.status_code == SEE_OTHER  # type: ignore[attr-defined]
    assert response.headers["Location"] == "/"  # type: ignore[attr-defined]
    html = client.get("/").get_data(as_text=True)
    assert "ann@example.com" in html
    assert 'action="/logout"' in html
    assert 'href="/login"' not in html


def test_anonymous_header_shows_login_and_register(client: FlaskClient) -> None:
    html = client.get("/").get_data(as_text=True)
    assert 'href="/login"' in html
    assert 'href="/register"' in html
    assert "/logout" not in html


def test_duplicate_registration_shows_an_error(client: FlaskClient) -> None:
    register(client)
    client.post("/logout", data={constants.CSRF_FORM_FIELD: token_of(client, "/")})
    response = register(client, "ANN@example.com")
    assert response.status_code == 409  # type: ignore[attr-defined]
    assert constants.ERROR_EMAIL_TAKEN in response.get_data(as_text=True)  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("email", "password", "message"),
    [
        ("bad", PASSWORD, constants.ERROR_EMAIL_INVALID),
        ("ann@example.com", "short", constants.ERROR_PASSWORD_TOO_SHORT),
    ],
)
def test_register_shows_field_errors(
    client: FlaskClient, email: str, password: str, message: str
) -> None:
    response = post(client, "/register", email=email, password=password)
    assert response.status_code == 400  # type: ignore[attr-defined]
    assert message in response.get_data(as_text=True)  # type: ignore[attr-defined]


def test_login_with_wrong_password_and_unknown_email_look_the_same(
    client: FlaskClient,
) -> None:
    register(client)
    client.post("/logout", data={constants.CSRF_FORM_FIELD: token_of(client, "/")})
    bodies = []
    for email in ("ann@example.com", "nobody@example.com"):
        response = post(client, "/login", email=email, password="wrong password")
        assert response.status_code == 401  # type: ignore[attr-defined]
        bodies.append(response.get_data(as_text=True))  # type: ignore[attr-defined]
    assert all(constants.ERROR_BAD_CREDENTIALS in body for body in bodies)


def test_login_cookie_is_httponly_samesite_and_logout_clears_it(
    client: FlaskClient,
) -> None:
    register(client)
    client.post("/logout", data={constants.CSRF_FORM_FIELD: token_of(client, "/")})
    login = post(client, "/login", email="ann@example.com", password=PASSWORD)
    cookie = login.headers["Set-Cookie"]  # type: ignore[attr-defined]
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Expires=" in cookie
    logout = client.post(
        "/logout", data={constants.CSRF_FORM_FIELD: token_of(client, "/")}
    )
    assert logout.status_code == SEE_OTHER
    assert "ann@example.com" not in client.get("/").get_data(as_text=True)


def test_login_replaces_the_pre_login_csrf_token(client: FlaskClient) -> None:
    register(client)
    client.post("/logout", data={constants.CSRF_FORM_FIELD: token_of(client, "/")})
    before = token_of(client)
    post_login = client.post(
        "/login",
        data={
            constants.CSRF_FORM_FIELD: before,
            "email": "ann@example.com",
            "password": PASSWORD,
        },
    )
    assert post_login.status_code == SEE_OTHER
    assert token_of(client, "/") != before


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("/admin", "/admin"),
        ("//evil.example", "/"),
        ("https://evil.example", "/"),
        ("/\\evil.example", "/"),
        ("javascript:alert(1)", "/"),
        ("/	/evil.example", "/"),
    ],
)
def test_next_is_honoured_only_for_local_paths(
    client: FlaskClient, target: str, expected: str
) -> None:
    register(client)
    client.post("/logout", data={constants.CSRF_FORM_FIELD: token_of(client, "/")})
    response = post(
        client,
        "/login",
        email="ann@example.com",
        password=PASSWORD,
        next=target,
    )
    assert response.headers["Location"] == expected  # type: ignore[attr-defined]


def test_post_without_token_is_refused(client: FlaskClient) -> None:
    response = client.post("/login", data={"email": "a@b.co", "password": PASSWORD})
    assert response.status_code == 403
    assert constants.ERROR_CSRF in response.get_data(as_text=True)


def test_post_with_wrong_token_is_refused(client: FlaskClient) -> None:
    token_of(client)
    response = client.post(
        "/login", data={constants.CSRF_FORM_FIELD: "wrong", "email": "a@b.co"}
    )
    assert response.status_code == 403


def test_token_from_another_session_is_refused(
    client: FlaskClient, tmp_path: Path
) -> None:
    other = create_app(tmp_path / "other.sqlite3", Settings("test-key")).test_client()
    stolen = token_of(other)
    token_of(client)
    assert (
        client.post("/login", data={constants.CSRF_FORM_FIELD: stolen}).status_code
        == 403
    )


def test_tampered_cookie_loses_the_session_and_token(client: FlaskClient) -> None:
    token = token_of(client)
    cookie = client.get_cookie("session")
    assert cookie is not None
    client.set_cookie("session", cookie.value[:-3] + "xyz")
    response = client.post("/login", data={constants.CSRF_FORM_FIELD: token})
    assert response.status_code == 403


def test_token_in_header_is_accepted(client: FlaskClient) -> None:
    token = token_of(client)
    response = client.post(
        "/login",
        headers={constants.CSRF_HEADER: token},
        data={"email": "a@b.co", "password": PASSWORD},
    )
    assert response.status_code == 401


def test_get_is_not_checked_for_a_token(client: FlaskClient) -> None:
    assert client.get("/login").status_code == 200


def test_admin_anonymous_redirects_to_login(client: FlaskClient) -> None:
    response = client.get("/admin")
    assert response.status_code == SEE_OTHER
    assert response.headers["Location"] == "/login"


def test_admin_customer_gets_403(client: FlaskClient) -> None:
    register(client)
    response = client.get("/admin")
    assert response.status_code == 403
    assert constants.ERROR_FORBIDDEN in response.get_data(as_text=True)


def test_admin_gets_the_page(client: FlaskClient) -> None:
    post(client, "/login", email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
    response = client.get("/admin")
    assert response.status_code == 200
    assert constants.TEXT_ADMIN_TITLE in response.get_data(as_text=True)


def test_admin_is_created_once_and_password_is_not_stored_plain(
    tmp_path: Path,
) -> None:
    path = tmp_path / "shop.sqlite3"
    settings = Settings("k", ADMIN_EMAIL, ADMIN_PASSWORD)
    create_app(path, settings)
    create_app(path, settings)
    assert ADMIN_PASSWORD.encode() not in path.read_bytes()
    assert "ADMIN_PASSWORD" not in repr(settings) and ADMIN_PASSWORD not in repr(
        settings
    )


def test_app_without_settings_runs_with_a_random_key(tmp_path: Path) -> None:
    client = create_app(tmp_path / "shop.sqlite3").test_client()
    assert client.get("/login").status_code == 200
    assert client.get("/admin").status_code == SEE_OTHER


def test_settings_read_the_environment_and_ignore_empty_values() -> None:
    settings = Settings.from_environment(
        {constants.ENV_SECRET_KEY: "k", constants.ENV_ADMIN_EMAIL: ""}
    )
    assert settings == Settings("k", None, None)
