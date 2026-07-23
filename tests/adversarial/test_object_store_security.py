from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from l9_harness.corpus.adapters.object_store import ObjectStoreCorpus


class Response:
    def __init__(self, data: bytes, declared: str | None = None, status: int = 200):
        self.data = data
        self.headers = {} if declared is None else {"Content-Length": declared}
        self.status = status

    def __enter__(self) -> "Response":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def read(self, limit: int = -1) -> bytes:
        return self.data if limit < 0 else self.data[:limit]


def test_object_store_requires_https() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        ObjectStoreCorpus("http://example.com/corpus.zip")


def test_object_store_rejects_credentials_and_unapproved_hosts() -> None:
    with pytest.raises(ValueError, match="authority"):
        ObjectStoreCorpus("https://user:secret@example.com/corpus.zip")
    with pytest.raises(ValueError, match="not authorized"):
        ObjectStoreCorpus(
            "https://example.com/corpus.zip",
            allowed_hosts=frozenset({"objects.example.net"}),
        )


def test_object_store_pull_is_bounded(tmp_path: Path) -> None:
    corpus = ObjectStoreCorpus("https://example.com/corpus.zip", maximum_bytes=4)
    corpus._opener = SimpleNamespace(open=lambda *_args, **_kwargs: Response(b"12345"))
    with pytest.raises(RuntimeError, match="maximum size"):
        corpus.pull(tmp_path / "corpus.zip")


def test_object_store_push_is_bounded(tmp_path: Path) -> None:
    source = tmp_path / "corpus.zip"
    source.write_bytes(b"12345")
    corpus = ObjectStoreCorpus("https://example.com/corpus.zip", maximum_bytes=4)
    with pytest.raises(RuntimeError, match="maximum size"):
        corpus.push(source)
