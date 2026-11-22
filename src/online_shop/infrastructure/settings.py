"""@brief The settings the shop reads from its environment."""

from collections.abc import Mapping
from dataclasses import dataclass, field

from online_shop import constants


@dataclass(frozen=True, slots=True)
class Settings:
    """@brief Secrets and the optional admin account.

    @param secret_key Signs the session cookie; None means a random one per start.
    @param admin_email Email of the admin account to create, or None.
    @param admin_password Its password, or None; hidden from repr and logs.
    """

    secret_key: str | None = None
    admin_email: str | None = None
    admin_password: str | None = field(default=None, repr=False)

    @classmethod
    def from_environment(cls, environ: Mapping[str, str]) -> Settings:
        """@brief Read the settings; an empty variable counts as not set."""
        return cls(
            secret_key=environ.get(constants.ENV_SECRET_KEY) or None,
            admin_email=environ.get(constants.ENV_ADMIN_EMAIL) or None,
            admin_password=environ.get(constants.ENV_ADMIN_PASSWORD) or None,
        )
