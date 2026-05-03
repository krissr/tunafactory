from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

from .checks import detect_contradictions, detect_duplicates, detect_low_quality
from .prepare import _read_jsonl
from .report import build_human_report


def diagnose_dataset(input_path: str, output_dir: str = "tunafactory_output") -> Tuple[Path, Dict[str, object]]:
    rows = _read_jsonl(Path(input_path))

    duplicates = detect_duplicates(rows)
    contradictions = detect_contradictions(rows)
    low_quality = detect_low_quality(rows)

    annotated_path = Path(output_dir)
    annotated_path.mkdir(parents=True, exist_ok=True)

    annotated_file = annotated_path / "annotated.jsonl"
    with annotated_file.open("w") as handle:
        for i, row in enumerate(rows):
            issues = []
            if i in duplicates["indexes"]:
                issues.append("duplicate")
            if i in contradictions["indexes"]:
                issues.append("contradiction")
            if i in low_quality["indexes"]:
                issues.append("low_quality")

            handle.write(json.dumps({"id": row.get("id", f"row_{i}"), "issues": issues}) + "\n")

    report_text = build_human_report(len(rows), duplicates, contradictions, low_quality)
    report_file = annotated_path / "report.txt"
    report_file.write_text(report_text + "\n")

    summary = {
        "total_samples": len(rows),
        "duplicates": {"count": duplicates["count"], "ratio": duplicates["ratio"]},
        "contradictions": {"count": contradictions["count"], "samples": contradictions["samples"]},
        "low_quality": {"count": low_quality["count"], "ratio": low_quality["ratio"]},
        "output_dir": str(annotated_path),
    }

    return annotated_path, {"report": report_text, "summary": summary}
