from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from .validate import validate_rows


def _read_jsonl(path: Path) -> List[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _read_csv(path: Path, input_col: str, output_col: str, system_col: str | None = None) -> List[dict]:
    rows = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for i, r in enumerate(reader):
            messages = []
            if system_col and r.get(system_col):
                messages.append({"role": "system", "content": r[system_col]})
            messages.append({"role": "user", "content": r[input_col]})
            messages.append({"role": "assistant", "content": r[output_col]})
            rows.append({"id": str(i), "messages": messages, "meta": {"source": str(path)}})
    return rows


def _fingerprint(rows: Iterable[dict]) -> str:
    payload = "\n".join(json.dumps(r, sort_keys=True) for r in rows)
    return hashlib.sha256(payload.encode()).hexdigest()


def prepare_dataset(
    input_path: str,
    output_dir: str,
    fmt: str | None = None,
    seed: int = 42,
    input_col: str = "input",
    output_col: str = "output",
    system_col: str | None = None,
) -> Tuple[Path, Dict[str, object]]:
    _ = seed
    path = Path(input_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if fmt is None:
        fmt = path.suffix.lower().lstrip(".")

    if fmt == "jsonl":
        rows = _read_jsonl(path)
    elif fmt == "csv":
        rows = _read_csv(path, input_col=input_col, output_col=output_col, system_col=system_col)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    report = validate_rows(rows)
    train_path = out / "prepared_train.jsonl"
    val_path = out / "prepared_val.jsonl"

    split = max(1, int(len(rows) * 0.02)) if len(rows) > 1 else 0
    val = rows[:split]
    train = rows[split:]

    for target, data in ((train_path, train), (val_path, val)):
        with target.open("w") as f:
            for row in data:
                f.write(json.dumps(row) + "\n")

    fp = _fingerprint(rows)
    (out / "fingerprint.sha256").write_text(fp)
    (out / "data_quality.json").write_text(json.dumps(report, indent=2))

    return out, {"fingerprint": fp, "report": report, "train_rows": len(train), "val_rows": len(val)}
