"""Tests of the Stripe key file: parsing, test-key rule and secrecy."""

from pathlib import Path

import pytest

from fakes import fake_key
from online_shop.infrastructure.settings import Settings
from online_shop.infrastructure.stripe_settings import (
    StripeConfigurationError,
    StripeSettings,
    load_stripe_settings,
)

PK = fake_key("pk", "test", "p" * 12)
SK = fake_key("sk", "test", "s" * 12)


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "stripe.env"
    path.write_text(text, encoding="utf-8")
    return path


def test_missing_file_means_not_configured(tmp_path: Path) -> None:
    assert load_stripe_settings(tmp_path / "absent.env") is None


def test_loads_comments_blank_lines_spaces_and_quotes(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        f"# keys\n\nPUBLISHABLE_KEY = \"{PK}\"\nignored line\nSECRET_KEY='{SK}'\n",
    )
    settings = load_stripe_settings(path)
    assert settings is not None
    assert settings.publishable_key == PK
    assert settings.secret_key == SK


def test_accepts_a_restricted_test_key(tmp_path: Path) -> None:
    settings = load_stripe_settings(write(tmp_path, _file(PK, fake_key("rk", "test"))))
    assert settings is not None


def _file(publishable: str | None, secret: str | None) -> str:
    lines = []
    if publishable is not None:
        lines.append(f"PUBLISHABLE_KEY={publishable}")
    if secret is not None:
        lines.append(f"SECRET_KEY={secret}")
    return "\n".join(lines) + "\n"


LIVE_SECRET = fake_key("sk", "live", "L" * 12)
LIVE_PUBLISHABLE = fake_key("pk", "live", "P" * 12)
GOOD_P = fake_key("pk", "test")
GOOD_S = fake_key("sk", "test")


@pytest.mark.parametrize(
    "text",
    [
        _file(LIVE_PUBLISHABLE, GOOD_S),
        _file(GOOD_P, LIVE_SECRET),
        _file(GOOD_P, "whatever"),
        _file(fake_key("sk", "test"), GOOD_S),
        _file("pk_test_", GOOD_S),
        _file(fake_key("pk", "test", "a b"), GOOD_S),
        _file(GOOD_P, None),
        "",
    ],
)
def test_refuses_live_unknown_or_missing_keys_without_leaking(
    tmp_path: Path, text: str
) -> None:
    with pytest.raises(StripeConfigurationError) as error:
        load_stripe_settings(write(tmp_path, text))
    for value in (LIVE_SECRET, LIVE_PUBLISHABLE, "whatever", GOOD_P, GOOD_S):
        assert value not in str(error.value)


def test_keys_are_hidden_from_repr_and_str() -> None:
    settings = StripeSettings(PK, SK)
    for text in (repr(settings), str(settings), f"{settings}"):
        assert PK not in text
        assert SK not in text


def env_settings(**environ: str) -> Settings:
    return Settings.from_environment(environ)


def test_environment_is_used_when_the_file_is_missing(tmp_path: Path) -> None:
    settings = load_stripe_settings(tmp_path / "absent.env", PK, SK)
    assert settings is not None
    assert (settings.publishable_key, settings.secret_key) == (PK, SK)


def test_the_file_wins_over_the_environment(tmp_path: Path) -> None:
    other_pk = fake_key("pk", "test", "o" * 12)
    other_sk = fake_key("sk", "test", "o" * 12)
    path = write(tmp_path, _file(PK, SK))
    settings = load_stripe_settings(path, other_pk, other_sk)
    assert settings is not None
    assert (settings.publishable_key, settings.secret_key) == (PK, SK)


def test_a_broken_file_is_not_rescued_by_the_environment(tmp_path: Path) -> None:
    with pytest.raises(StripeConfigurationError):
        load_stripe_settings(write(tmp_path, _file(PK, None)), PK, SK)


def test_neither_source_means_not_configured(tmp_path: Path) -> None:
    assert load_stripe_settings(tmp_path / "absent.env", None, None) is None
    assert load_stripe_settings(None) is None
    assert load_stripe_settings(None, "", "") is None


@pytest.mark.parametrize(
    ("publishable", "secret", "missing"),
    [(PK, None, "SECRET_KEY"), (None, SK, "PUBLISHABLE_KEY")],
)
def test_one_environment_key_alone_is_an_error_naming_the_other(
    tmp_path: Path, publishable: str | None, secret: str | None, missing: str
) -> None:
    with pytest.raises(StripeConfigurationError) as error:
        load_stripe_settings(tmp_path / "absent.env", publishable, secret)
    assert missing in str(error.value)
    assert PK not in str(error.value)
    assert SK not in str(error.value)


def test_a_live_key_in_the_environment_is_refused_without_leaking() -> None:
    with pytest.raises(StripeConfigurationError) as error:
        load_stripe_settings(None, GOOD_P, LIVE_SECRET)
    assert LIVE_SECRET not in str(error.value)
    assert GOOD_P not in str(error.value)


def test_settings_read_the_two_variables_and_hide_them() -> None:
    settings = env_settings(PUBLISHABLE_KEY=PK, SECRET_KEY=SK)
    assert settings.stripe_publishable_key == PK
    assert settings.stripe_secret_key == SK
    assert PK not in repr(settings)
    assert SK not in repr(settings)


def test_settings_without_the_variables_have_no_keys() -> None:
    settings = env_settings()
    assert settings.stripe_publishable_key is None
    assert settings.stripe_secret_key is None
