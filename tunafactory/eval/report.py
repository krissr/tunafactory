from __future__ import annotations

import json
from pathlib import Path

from .metrics import summarize_metrics


def build_report(run_dir: str) -> Path:
    run_path = Path(run_dir)
    eval_dir = run_path / "eval"
    eval_dir.mkdir(parents=True, exist_ok=True)
    metrics = summarize_metrics(run_dir)
    (eval_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    md = eval_dir / "report.md"
    md.write_text(
        "# Evaluation Report\n\n"
        f"- Train loss: {metrics['train_loss']}\n"
        f"- Val loss: {metrics['val_loss']}\n"
        f"- Perplexity: {metrics['perplexity']}\n"
        + (f"- Note: {metrics['note']}\n" if "note" in metrics else "")
    )
    return md
