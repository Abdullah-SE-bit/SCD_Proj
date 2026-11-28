"""Password hashes: salted scrypt, with the cost stored next to each hash so it can be raised later."""

import base64
import hashlib
import hmac
import secrets

N, R, P = 2**14, 8, 1


def _derive(password: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p, dklen=32)


def hashed(password: str) -> str:
    salt = secrets.token_bytes(16)
    parts = [base64.b64encode(value).decode() for value in (salt, _derive(password, salt, N, R, P))]
    return "$".join(["scrypt", str(N), str(R), str(P), *parts])


def matches(password: str, stored: str) -> bool:
    try:
        kind, n, r, p, salt, digest = stored.split("$")
        derived = _derive(password, base64.b64decode(salt), int(n), int(r), int(p))
        return kind == "scrypt" and hmac.compare_digest(derived, base64.b64decode(digest))
    except ValueError:  # not a hash this module wrote
        return False
