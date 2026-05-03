from __future__ import annotations

from pathlib import Path


def export_run(run_dir: str, target: str) -> Path:
    run_path = Path(run_dir)
    out = run_path / "export" / target
    out.mkdir(parents=True, exist_ok=True)
    (out / "README.txt").write_text(f"Exported target: {target}\n")
    return out
