from __future__ import annotations
from typing import Any

def classify(expected: dict[str, Any], actual: dict[str, Any]) -> dict:
    mismatches = []
    for k in sorted(set(expected) | set(actual)):
        if expected.get(k) != actual.get(k):
            mismatches.append({'field': k, 'expected': expected.get(k), 'actual': actual.get(k), 'class': 'operational' if k in {'executionId', 'startedAt', 'completedAt', 'resourceUsage'} else 'semantic'})
    return {'mismatches': mismatches, 'semanticCount': sum((x['class'] == 'semantic' for x in mismatches)), 'operationalCount': sum((x['class'] == 'operational' for x in mismatches)), 'pass': not any((x['class'] == 'semantic' for x in mismatches))}
