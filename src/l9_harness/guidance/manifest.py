from ..domain.digests import digest_canonical

def manifest_digest(manifest: dict) -> dict:
    return digest_canonical(manifest, 'guidance-manifest')
