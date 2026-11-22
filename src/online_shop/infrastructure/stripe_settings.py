"""@brief The Stripe test keys, read from a local file and never shown."""

import re
from collections.abc import Mapping
from pathlib import Path

from online_shop import constants


class StripeConfigurationError(ValueError):
    """@brief The Stripe key file is wrong; the message never holds a key."""


class StripeSettings:
    """@brief The publishable and the secret test key; hidden from repr and logs."""

    __slots__ = ("_publishable_key", "_secret_key")

    def __init__(self, publishable_key: str, secret_key: str) -> None:
        """@brief Check both keys.

        @raises StripeConfigurationError When a key is not a Stripe test key.
        """
        _check_key(
            constants.STRIPE_KEY_PUBLISHABLE,
            publishable_key,
            constants.STRIPE_PUBLISHABLE_PREFIXES,
        )
        _check_key(
            constants.STRIPE_KEY_SECRET, secret_key, constants.STRIPE_SECRET_PREFIXES
        )
        self._publishable_key = publishable_key
        self._secret_key = secret_key

    @property
    def publishable_key(self) -> str:
        """@brief The publishable test key."""
        return self._publishable_key

    @property
    def secret_key(self) -> str:
        """@brief The secret test key; hand it only to the gateway."""
        return self._secret_key

    def __repr__(self) -> str:
        """@brief The class name with the keys redacted."""
        return "StripeSettings(publishable_key=<hidden>, secret_key=<hidden>)"

    __str__ = __repr__


def _check_key(name: str, value: str, prefixes: tuple[str, ...]) -> None:
    prefix = next((p for p in prefixes if value.startswith(p)), None)
    if prefix is None:
        raise StripeConfigurationError(
            f"{name} must be a Stripe test key starting with "
            f"{' or '.join(prefixes)}; live and unknown keys are refused."
        )
    rest = value[len(prefix) :]
    if not rest or not re.fullmatch(constants.STRIPE_KEY_PATTERN, rest):
        raise StripeConfigurationError(f"{name} is not a well formed Stripe key.")


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _parse(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        values[name.strip()] = _unquote(value.strip())
    return values


def _from_values(values: Mapping[str, str | None], source: str) -> StripeSettings:
    missing = [
        name
        for name in (constants.STRIPE_KEY_PUBLISHABLE, constants.STRIPE_KEY_SECRET)
        if not values.get(name)
    ]
    if missing:
        raise StripeConfigurationError(
            f"The Stripe {source} lacks: {', '.join(missing)}."
        )
    return StripeSettings(
        str(values[constants.STRIPE_KEY_PUBLISHABLE]),
        str(values[constants.STRIPE_KEY_SECRET]),
    )


def load_stripe_settings(
    path: Path | None,
    env_publishable_key: str | None = None,
    env_secret_key: str | None = None,
) -> StripeSettings | None:
    """@brief Read the keys from the key file, else from the environment values.

    The file wins when it exists. Without it, the two environment values are
    used; with neither of them Stripe is simply not configured.

    @param path The `KEY=value` file, or None to not look for one.
    @param env_publishable_key The value of the PUBLISHABLE_KEY variable, or None.
    @param env_secret_key The value of the SECRET_KEY variable, or None.
    @return The settings, or None when no source is present.
    @raises StripeConfigurationError When a key is missing, live or malformed.
    """
    if path is not None:
        try:
            text = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            pass
        else:
            return _from_values(_parse(text), "key file")
    if not env_publishable_key and not env_secret_key:
        return None
    return _from_values(
        {
            constants.ENV_STRIPE_PUBLISHABLE_KEY: env_publishable_key,
            constants.ENV_STRIPE_SECRET_KEY: env_secret_key,
        },
        "environment",
    )
