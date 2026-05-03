from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .manifest import write_manifest
from .presets import preset_config

MODEL_ALIASES = {
    "llama3.1-8b": "meta-llama/Meta-Llama-3.1-8B-Instruct",
    "mistral-7b-instruct": "mistralai/Mistral-7B-Instruct-v0.3",
    "mistral-7b": "mistralai/Mistral-7B-v0.3",
}


def _next_run_dir(runs_root: str) -> Path:
    root = Path(runs_root)
    root.mkdir(parents=True, exist_ok=True)
    existing = sorted([p for p in root.glob("run_*") if p.is_dir()])
    idx = len(existing) + 1
    return root / f"run_{idx:03d}"


def _require_llamafactory_cli() -> str:
    exe = shutil.which("llamafactory-cli")
    if not exe:
        raise RuntimeError(
            "llamafactory-cli not found. Install LLaMA-Factory first, e.g. `pip install llamafactory` "
            "and ensure the executable is on PATH."
        )
    return exe


def launch_finetune(model: str, dataset_dir: str, runs_root: str = "runs", preset: str = "small") -> Path:
    model_name = MODEL_ALIASES.get(model, model)
    run_dir = _next_run_dir(runs_root)
    (run_dir / "configs").mkdir(parents=True, exist_ok=True)
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    (run_dir / "checkpoints").mkdir(parents=True, exist_ok=True)

    params = preset_config(preset)
    train_cfg = {
        "stage": "sft",
        "do_train": True,
        "model_name_or_path": model_name,
        "dataset_dir": str(Path(dataset_dir).resolve()),
        "dataset": "prepared_train",
        "eval_dataset": "prepared_val",
        "template": "default",
        "finetuning_type": "lora",
        "quantization_bit": 4,
        "output_dir": str((run_dir / "checkpoints").resolve()),
        "learning_rate": params["lr"],
        "num_train_epochs": params["epochs"],
        "cutoff_len": params["cutoff_len"],
        "lora_rank": params["lora_rank"],
        "logging_steps": 10,
        "save_steps": 100,
        "plot_loss": True,
        "bf16": True,
    }

    cfg_path = run_dir / "configs" / "llamafactory_train.json"
    cfg_path.write_text(json.dumps(train_cfg, indent=2))

    exe = _require_llamafactory_cli()
    log_path = run_dir / "logs" / "trainer.log"
    with log_path.open("w") as logf:
        subprocess.run([exe, "train", str(cfg_path)], check=True, stdout=logf, stderr=subprocess.STDOUT)

    write_manifest(
        run_dir,
        {
            "model": model_name,
            "dataset_dir": dataset_dir,
            "preset": preset,
            "backend": "llamafactory",
            "train_config": str(cfg_path),
        },
    )
    return run_dir
