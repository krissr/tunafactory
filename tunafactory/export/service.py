from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def _require_llamafactory_cli() -> str:
    exe = shutil.which("llamafactory-cli")
    if not exe:
        raise RuntimeError("llamafactory-cli not found. Install LLaMA-Factory and ensure it is on PATH.")
    return exe


def export_run(run_dir: str, target: str) -> Path:
    run_path = Path(run_dir)
    manifest = json.loads((run_path / "manifest.json").read_text())
    checkpoint_dir = run_path / "checkpoints"

    out = run_path / "export" / target
    out.mkdir(parents=True, exist_ok=True)

    if target == "adapter":
        return checkpoint_dir

    exe = _require_llamafactory_cli()
    export_cfg = {
        "model_name_or_path": manifest["model"],
        "adapter_name_or_path": str(checkpoint_dir.resolve()),
        "export_dir": str(out.resolve()),
        "export_size": 4,
        "export_device": "cpu",
    }
    cfg_path = run_path / "configs" / f"export_{target}.json"
    cfg_path.write_text(json.dumps(export_cfg, indent=2))
    subprocess.run([exe, "export", str(cfg_path)], check=True)
    return out
