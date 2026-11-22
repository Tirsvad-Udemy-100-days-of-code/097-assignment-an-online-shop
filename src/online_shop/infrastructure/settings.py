"""@brief The settings the shop reads from its environment."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

from online_shop import constants


@dataclass(frozen=True, slots=True)
class Settings:
    """@brief Secrets and the optional admin account.

    @param secret_key Signs the session cookie; None means a random one per start.
    @param admin_email Email of the admin account to create, or None.
    @param admin_password Its password, or None; hidden from repr and logs.
    @param stripe_env_file The file with the Stripe test keys, or None to not
        look for one; `from_environment` defaults it to `stripe.env`.
    @param stripe_publishable_key Fallback when the file is missing; hidden.
    @param stripe_secret_key Fallback when the file is missing; hidden.
    """

    secret_key: str | None = None
    admin_email: str | None = None
    admin_password: str | None = field(default=None, repr=False)
    stripe_env_file: Path | None = None
    stripe_publishable_key: str | None = field(default=None, repr=False)
    stripe_secret_key: str | None = field(default=None, repr=False)

    @classmethod
    def from_environment(cls, environ: Mapping[str, str]) -> Settings:
        """@brief Read the settings; an empty variable counts as not set."""
        return cls(
            secret_key=environ.get(constants.ENV_SECRET_KEY) or None,
            admin_email=environ.get(constants.ENV_ADMIN_EMAIL) or None,
            admin_password=environ.get(constants.ENV_ADMIN_PASSWORD) or None,
            stripe_env_file=Path(
                environ.get(constants.ENV_STRIPE_ENV_FILE)
                or constants.STRIPE_ENV_FILE_NAME
            ),
            stripe_publishable_key=environ.get(constants.ENV_STRIPE_PUBLISHABLE_KEY)
            or None,
            stripe_secret_key=environ.get(constants.ENV_STRIPE_SECRET_KEY) or None,
        )
