from l9_harness.corpus.layout import layout


def test_layout_separates_cache_outbox(tmp_path):
    d = layout(tmp_path)
    assert d["cache"] != d["outbox"]
    assert d["cache"].exists() and d["outbox"].exists()
