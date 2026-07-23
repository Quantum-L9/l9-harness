# Regression Guard

## Preserved contracts

- Distribution name remains `l9-harness`.
- Console entrypoint remains `l9-harness`.
- Existing CLI command names remain unchanged.
- Harness remains outside the authoritative CI path.
- SDK remains the only intended Release-zero observation producer.
- Assurance remains the admission and verdict authority.
- CI Core remains the publication authority.
- Diagnostic fallback remains non-authoritative.
- Corpus candidates remain staged and are never automatically promoted.
- External observation and Assurance artifacts remain byte-preserved.

## Strengthened invariants

1. Dirty worktrees cannot become immutable `git-revision` subjects.
2. External plan and SDK documents are never mutated by loaders.
3. Missing plan requirements are not inferred from private Harness mirrors.
4. Requirement resolution checks producer version, build digest, check version, schema, configuration contract, subject kind, cardinality, alternatives, and supporting artifacts.
5. SDK execution occurs in a detached isolated clone, not the source worktree.
6. Process-mode network denial is reported as an unenforced limitation instead of a false pass.
7. Preserved external artifacts receive raw digests only until authority canonicalization is verifiable.
8. Bundle verification rejects unlisted files and symlinks.
9. Archive extraction rejects traversal, duplicates, symlinks, encryption, excessive expansion, and suspicious compression ratios.
10. Corpus pull is exact, submission is non-destructive, and divergent paths fail closed.
11. Production Assurance invocation verifies the executable bytes against the pinned authority digest.
12. Release construction runs repository validation before packaging.

## Required rerun ladder

```bash
find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .mypy_cache -o -name .ruff_cache \) -prune -exec rm -rf {} +
python -m compileall -q src tests scripts build_backend.py
python -m pytest -q
python scripts/verify_generated.py
python -B scripts/validate_repository.py
uv sync --locked --offline
python scripts/build_release.py
```

Ruff and mypy results must remain `BLOCKED`, not `PASS`, until their pinned executables actually run.

13. Doctor diagnostics use the same sanitized subprocess boundary as runtime Git operations.
14. Object-store corpus transfers are HTTPS-first, redirect-free, host-constrainable, and size-bounded.
15. Every tracked file inherits `L9_META.yaml` through the deterministic file index.
16. The wheel embeds the exact source identity and matches runtime/resource source bytes.
17. The sdist matches the approved source tree with no extra or missing files.
18. Distribution artifacts share one source-tree identity and verified checksums.

19. Every CLI command is normalized and validated through one ingress before dispatch.
20. Public ingress records expose argument names and digests, never raw values.
21. Repository validation may be rerun without changing source identity or tracked-file metadata.
22. Tracked-file validation compares exact records rather than counts only.
23. The distribution manifest binds the exact repository-validation report.
24. `FILETREE.md` is the sole source-tree inventory; duplicate final-tree files must not return.
25. Repository validation rejects stale `FINAL_TREE.md` and `FINAL_REPO_TREE.md` artifacts.
26. Fresh wheel metadata matches `pyproject.toml` name, version, Python requirement, and summary.
27. Fresh source distributions contain `FILETREE.md` and exclude superseded tree inventories.
28. CLI `--version` output matches runtime and package version identities.
