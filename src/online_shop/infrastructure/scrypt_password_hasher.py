"""@brief The scrypt adapter of the PasswordHasher port."""

import base64
import binascii
import hashlib
import hmac
import secrets

from online_shop import constants

_SEP = constants.HASH_SEPARATOR


def _scrypt(password: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=n,
        r=r,
        p=p,
        maxmem=constants.SCRYPT_MAX_MEMORY_BYTES,
        dklen=constants.SCRYPT_KEY_BYTES,
    )


class ScryptPasswordHasher:
    """@brief Hashes with scrypt and a random salt per password.

    The stored text is `scrypt$n$r$p$salt$key` (salt and key in base64), so the
    cost parameters can be raised later while old hashes still verify.
    """

    def hash(self, password: str) -> str:
        """@brief Return the salted hash of the password."""
        salt = secrets.token_bytes(constants.SCRYPT_SALT_BYTES)
        key = _scrypt(
            password, salt, constants.SCRYPT_N, constants.SCRYPT_R, constants.SCRYPT_P
        )
        return _SEP.join(
            (
                constants.SCRYPT_SCHEME,
                str(constants.SCRYPT_N),
                str(constants.SCRYPT_R),
                str(constants.SCRYPT_P),
                base64.b64encode(salt).decode("ascii"),
                base64.b64encode(key).decode("ascii"),
            )
        )

    def verify(self, password: str, password_hash: str) -> bool:
        """@brief Check a password in constant time; a malformed hash never matches."""
        parts = password_hash.split(_SEP)
        if (
            len(parts) != constants.HASH_PART_COUNT
            or parts[0] != constants.SCRYPT_SCHEME
        ):
            return False
        try:
            n, r, p = (int(value) for value in parts[1:4])
            salt = base64.b64decode(parts[4], validate=True)
            expected = base64.b64decode(parts[5], validate=True)
            actual = _scrypt(password, salt, n, r, p)
        except ValueError, binascii.Error:
            return False
        return hmac.compare_digest(actual, expected)
