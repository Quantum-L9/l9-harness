from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from ...security.paths import confined


def _overlap(left: Path, right: Path) -> bool:
    left = left.resolve()
    right = right.resolve()
    return left == right or left in right.parents or right in left.parents


class FilesystemCorpus:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def _validate_tree(self, source: Path) -> None:
        for path in sorted(source.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Corpus symlink prohibited: {path}")

    def _copy_exact(self, source: Path, target: Path) -> None:
        source = source.resolve()
        target = target.resolve()
        if _overlap(source, target):
            raise ValueError("Corpus source and target must not overlap")
        self._validate_tree(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix="l9-corpus-", dir=target.parent))
        try:
            payload = stage / "payload"
            payload.mkdir()
            for path in sorted(source.rglob("*")):
                if not path.is_file():
                    continue
                relative = path.relative_to(source)
                destination = confined(payload, payload / relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination, follow_symlinks=False)
            previous = target.with_name(target.name + ".previous")
            if previous.exists():
                shutil.rmtree(previous)
            if target.exists():
                target.replace(previous)
            payload.replace(target)
            shutil.rmtree(previous, ignore_errors=True)
        finally:
            shutil.rmtree(stage, ignore_errors=True)

    def _copy_merge(self, source: Path, target: Path) -> None:
        source = source.resolve()
        target = target.resolve()
        if _overlap(source, target):
            raise ValueError("Corpus source and target must not overlap")
        self._validate_tree(source)
        target.mkdir(parents=True, exist_ok=True)
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(source)
            destination = confined(target, target / relative)
            if destination.exists() and destination.read_bytes() != path.read_bytes():
                raise ValueError(f"Corpus destination conflict: {relative.as_posix()}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination, follow_symlinks=False)

    def pull(self, target: Path) -> None:
        self._copy_exact(self.root, target)

    def push(self, source: Path) -> None:
        self._copy_merge(source, self.root)
