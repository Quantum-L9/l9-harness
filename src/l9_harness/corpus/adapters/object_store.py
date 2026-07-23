from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from ...domain.digests import digest_bytes


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        raise urllib.error.HTTPError(req.full_url, code, "Redirect prohibited", headers, fp)


class ObjectStoreCorpus:
    def __init__(
        self,
        object_url: str,
        authorization: str | None = None,
        *,
        allow_insecure: bool = False,
        allowed_hosts: frozenset[str] | None = None,
        maximum_bytes: int = 64 * 1024 * 1024,
    ):
        parsed = urllib.parse.urlsplit(object_url)
        if parsed.scheme not in {"https", "http"}:
            raise ValueError("Object store URL must be HTTP(S)")
        if parsed.scheme != "https" and not allow_insecure:
            raise ValueError("Object store URL must use HTTPS")
        if not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
            raise ValueError("Object store URL contains prohibited authority components")
        if allowed_hosts is not None and parsed.hostname.lower() not in allowed_hosts:
            raise ValueError("Object store host is not authorized")
        if maximum_bytes < 1:
            raise ValueError("maximum_bytes must be positive")
        self.object_url = object_url
        self.authorization = authorization
        self.maximum_bytes = maximum_bytes
        self._opener = urllib.request.build_opener(_NoRedirect())

    def _request(self, method: str, data: bytes | None = None) -> Any:
        headers = {"Content-Type": "application/zip"}
        if self.authorization:
            headers["Authorization"] = self.authorization
        request = urllib.request.Request(
            self.object_url,
            data=data,
            headers=headers,
            method=method,
        )
        return self._opener.open(request, timeout=120)

    def pull(
        self,
        target: Path,
        expected_digest: dict[str, str] | None = None,
    ) -> dict[str, str]:
        with self._request("GET") as response:
            declared = response.headers.get("Content-Length")
            if declared is not None and int(declared) > self.maximum_bytes:
                raise RuntimeError("Object-store corpus exceeds maximum size")
            data = response.read(self.maximum_bytes + 1)
        if len(data) > self.maximum_bytes:
            raise RuntimeError("Object-store corpus exceeds maximum size")
        digest = digest_bytes(data)
        if expected_digest and digest != expected_digest:
            raise RuntimeError("Object-store corpus digest mismatch")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return digest

    def push(
        self,
        source: Path,
        expected_digest: dict[str, str] | None = None,
    ) -> dict[str, str]:
        if source.stat().st_size > self.maximum_bytes:
            raise RuntimeError("Object-store corpus exceeds maximum size")
        data = source.read_bytes()
        digest = digest_bytes(data)
        if expected_digest and digest != expected_digest:
            raise RuntimeError("Refusing object-store push with unexpected digest")
        with self._request("PUT", data) as response:
            if response.status >= 300:
                raise RuntimeError(f"Object-store push failed: HTTP {response.status}")
        return digest
