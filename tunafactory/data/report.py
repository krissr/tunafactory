from __future__ import annotations

from typing import Dict, List


def build_human_report(total_samples: int, duplicates: Dict[str, object], contradictions: Dict[str, object], low_quality: Dict[str, object]) -> str:
    issues: List[str] = []
    if duplicates["count"]:
        issues.append(f"1. High duplication ({duplicates['ratio'] * 100:.0f}%)")
    if contradictions["count"]:
        issues.append(f"2. {contradictions['count']} contradictory prompts")
    if low_quality["count"]:
        issues.append(f"3. Too many short/low-quality answers ({low_quality['ratio'] * 100:.0f}%)")

    lines = [f"Dataset: {total_samples:,} samples"]
    if issues:
        lines.append("⚠️ Issues found:")
        lines.extend(issues)
        lines.extend(
            [
                "→ Your model will likely:",
                "- overfit",
                "- give inconsistent answers",
                "- be unhelpful",
                "Suggestions:",
                "- remove duplicates",
                "- fix contradictions",
                "- add more detailed responses",
            ]
        )
    else:
        lines.append("✅ No major issues found. Dataset is likely suitable for fine-tuning.")

    return "\n".join(lines)
