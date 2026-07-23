import pytest

from l9_harness.corpus.adapters.filesystem import FilesystemCorpus
from l9_harness.corpus.sync import synchronize
from l9_harness.domain.errors import ContractError


def test_pull_is_exact_and_removes_stale_files(tmp_path):
    remote = tmp_path / "remote"
    cache = tmp_path / "cache"
    remote.mkdir()
    cache.mkdir()
    (remote / "current").write_text("current")
    (cache / "stale").write_text("stale")
    FilesystemCorpus(remote).pull(cache)
    assert (cache / "current").read_text() == "current"
    assert not (cache / "stale").exists()


def test_overlapping_corpus_roots_are_rejected(tmp_path):
    remote = tmp_path / "remote"
    remote.mkdir()
    with pytest.raises(ValueError):
        FilesystemCorpus(remote).pull(remote / "cache")


def test_sync_rejects_divergent_same_path(tmp_path):
    remote = tmp_path / "remote"
    cache = tmp_path / "cache"
    outbox = tmp_path / "outbox"
    for path in (remote, cache, outbox):
        path.mkdir()
        (path / "same").write_text("base")
    (remote / "same").write_text("remote")
    (outbox / "same").write_text("local")
    with pytest.raises(ContractError):
        synchronize(remote, cache, outbox)
