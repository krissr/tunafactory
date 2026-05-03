from __future__ import annotations

import json
from pathlib import Path


def summarize_metrics(run_dir: str) -> dict:
    run_path = Path(run_dir)
    state_file = run_path / "checkpoints" / "trainer_state.json"
    if not state_file.exists():
        return {"train_loss": None, "val_loss": None, "perplexity": None, "note": "trainer_state.json not found"}

    state = json.loads(state_file.read_text())
    log_history = state.get("log_history", [])
    train_losses = [x["loss"] for x in log_history if "loss" in x]
    eval_losses = [x["eval_loss"] for x in log_history if "eval_loss" in x]
    train_loss = train_losses[-1] if train_losses else None
    val_loss = eval_losses[-1] if eval_losses else None
    ppl = None if val_loss is None else round(2.718281828 ** val_loss, 4)
    return {"train_loss": train_loss, "val_loss": val_loss, "perplexity": ppl}
