from __future__ import annotations
from typing import Any
REQUIRED_AUTHORITY_FIELDS = {'id', 'version', 'buildDigest', 'acceptedBuildDigests', 'authorizedChecks', 'publicContractDigest', 'producerAuthorization'}

def validate_sdk_authority(doc: dict[str, Any]) -> list[str]:
    missing = sorted(REQUIRED_AUTHORITY_FIELDS - set(doc))
    if doc.get('id') != 'l9-ci-sdk':
        missing.append('id:l9-ci-sdk')
    if doc.get('producerAuthorization') != 'approved':
        missing.append('producerAuthorization:approved')
    return missing
