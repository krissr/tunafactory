from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def write_manifest(run_dir: Path, payload: dict) -> Path:
    payload = dict(payload)
    payload["created_at"] = datetime.now(timezone.utc).isoformat()
    target = run_dir / "manifest.json"
    target.write_text(json.dumps(payload, indent=2))
    return target
