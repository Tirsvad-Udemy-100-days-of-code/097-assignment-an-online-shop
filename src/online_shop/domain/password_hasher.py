"""@brief The port through which the business hashes and checks passwords."""

from typing import Protocol


class PasswordHasher(Protocol):
    """@brief Turns a password into a salted hash and checks a password against one."""

    def hash(self, password: str) -> str:
        """@brief Return a self-describing salted hash of the password."""
        ...

    def verify(self, password: str, password_hash: str) -> bool:
        """@brief Return True when the password matches the stored hash."""
        ...
