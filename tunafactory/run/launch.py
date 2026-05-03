from __future__ import annotations

import json
from pathlib import Path

from .manifest import write_manifest
from .presets import preset_config

MODEL_ALIASES = {
    "llama3.1-8b": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "mistral-7b-instruct": "mistralai/Mistral-7B-Instruct-v0.3",
    "mistral-7b": "mistralai/Mistral-7B-v0.3",
}


def launch_finetune(model: str, dataset_dir: str, runs_root: str = "runs", preset: str = "small") -> Path:
    model_name = MODEL_ALIASES.get(model, model)
    run_dir = Path(runs_root) / "run_001"
    (run_dir / "configs").mkdir(parents=True, exist_ok=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)

    cfg = {
        "model_name_or_path": model_name,
        "dataset_dir": str(dataset_dir),
        "preset": preset,
        "params": preset_config(preset),
        "backend": "llamafactory",
    }
    (run_dir / "configs" / "llamafactory_train.json").write_text(json.dumps(cfg, indent=2))
    (run_dir / "logs" / "trainer.log").write_text("Simulated training run.\n")

    write_manifest(run_dir, {"model": model_name, "dataset_dir": dataset_dir, "preset": preset})
    return run_dir
