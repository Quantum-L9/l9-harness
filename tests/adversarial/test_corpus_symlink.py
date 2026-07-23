import pytest
from l9_harness.corpus.adapters.filesystem import FilesystemCorpus

def test_corpus_rejects_symlink(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "target").write_text("x")
    (source / "link").symlink_to(source / "target")
    with pytest.raises(ValueError):
        FilesystemCorpus(source).pull(tmp_path / "cache")
