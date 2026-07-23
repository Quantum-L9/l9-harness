from __future__ import annotations
from pathlib import Path
from ...conformance.producer import run_producer_fixtures
from ...conformance.consumer import verify_transport

def producer(fixtures: Path) -> dict:
    r = run_producer_fixtures(fixtures)
    return {'status': 'pass' if r['pass'] else 'fail', 'details': r}

def consumer(source: Path, transported: Path) -> dict:
    r = verify_transport(source, transported)
    return {'status': 'pass' if r['pass'] else 'fail', 'details': r}
