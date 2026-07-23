from pathlib import Path
ROOT = Path(__file__).resolve().parents[2] / 'src/l9_harness'

def source():
    return '\n'.join((p.read_text() for p in ROOT.rglob('*.py')))

def test_no_github_publication_imports():
    s = source()
    assert 'PyGithub' not in s and 'github.CheckRun' not in s

def test_no_assurance_internal_imports():
    s = source()
    assert 'assurance_evaluator' not in s and '@l9/assurance' not in s

def test_no_sdk_private_imports():
    assert 'l9_ci_sdk.' not in source()
