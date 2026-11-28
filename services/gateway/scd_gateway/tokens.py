"""Signed login tokens: JSON Web Token with HMAC-SHA256, standard library only."""

import base64
import hashlib
import hmac
import json
import time

LIFETIME = 8 * 3600  # seconds
HEADER = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').rstrip(b"=").decode()


def _encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _signature(signed: str, key: bytes) -> str:
    return _encode(hmac.new(key, signed.encode(), hashlib.sha256).digest())


def issue(user_id: str, key: bytes, now: float | None = None) -> str:
    claims = {"sub": user_id, "exp": int(time.time() if now is None else now) + LIFETIME}
    signed = f"{HEADER}.{_encode(json.dumps(claims).encode())}"
    return f"{signed}.{_signature(signed, key)}"


def user_of(token: str, key: bytes, now: float | None = None) -> str | None:
    """The user the token was issued to, or None. Only tokens with exactly this header and signature count."""
    parts = token.split(".")
    if not token.isascii() or len(parts) != 3 or parts[0] != HEADER:
        return None
    if not hmac.compare_digest(parts[2], _signature(f"{parts[0]}.{parts[1]}", key)):
        return None
    claims = json.loads(base64.urlsafe_b64decode(parts[1] + "=="))  # signed by us, so well formed
    return claims["sub"] if claims["exp"] >= (time.time() if now is None else now) else None
