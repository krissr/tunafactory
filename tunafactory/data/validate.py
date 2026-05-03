from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List


def validate_rows(rows: Iterable[dict]) -> Dict[str, object]:
    rows = list(rows)
    errors: List[str] = []
    seen = Counter()

    for i, row in enumerate(rows):
        rid = row.get("id", f"row_{i}")
        messages = row.get("messages", [])
        if not isinstance(messages, list) or not messages:
            errors.append(f"{rid}: missing messages")
            continue
        if messages[-1].get("role") != "assistant":
            errors.append(f"{rid}: last message must be assistant")
        if not any(m.get("role") == "user" for m in messages):
            errors.append(f"{rid}: must include a user message")
        if not messages[-1].get("content", "").strip():
            errors.append(f"{rid}: empty assistant response")
        seen[str(messages)] += 1

    duplicates = sum(1 for _, c in seen.items() if c > 1)
    return {
        "total_rows": len(rows),
        "errors": errors,
        "duplicate_groups": duplicates,
        "ok": len(errors) == 0,
    }
