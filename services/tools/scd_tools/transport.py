"""One HTTPS exchange to an already checked address. Redirects are not followed here, so each hop is re-checked."""

import http.client
import socket
import ssl
from dataclasses import dataclass


@dataclass
class Response:
    status: int
    headers: dict[str, str]  # lower-case names
    body: bytes


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connects to the address that was checked, while TLS still verifies the host name (no DNS rebinding)."""

    def __init__(self, host: str, address: str, timeout: float) -> None:
        super().__init__(host, 443, timeout=timeout)
        self.address = address
        self.tls = ssl.create_default_context()

    def connect(self) -> None:
        raw = socket.create_connection((self.address, 443), self.timeout)
        self.sock = self.tls.wrap_socket(raw, server_hostname=self.host)


def send(method: str, host: str, address: str, target: str, headers: dict[str, str], body: bytes | None,
         timeout: float, max_bytes: int) -> Response:
    connection = PinnedHTTPSConnection(host, address, timeout)
    try:
        connection.request(method, target, body=body, headers=headers)
        reply = connection.getresponse()
        data = reply.read(max_bytes + 1)
        return Response(reply.status, {k.lower(): v for k, v in reply.getheaders()}, data)
    except (OSError, http.client.HTTPException) as error:
        raise ConnectionError(f"{host}: {type(error).__name__}") from None
    finally:
        connection.close()
