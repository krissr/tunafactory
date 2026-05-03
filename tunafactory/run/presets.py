from __future__ import annotations


def select_preset(dataset_rows: int) -> str:
    if dataset_rows <= 2000:
        return "small"
    if dataset_rows <= 20000:
        return "medium"
    return "large"


def preset_config(preset: str) -> dict:
    table = {
        "small": {"lora_rank": 16, "lr": 2e-4, "epochs": 4, "cutoff_len": 2048},
        "medium": {"lora_rank": 32, "lr": 1.5e-4, "epochs": 3, "cutoff_len": 3072},
        "large": {"lora_rank": 64, "lr": 1e-4, "epochs": 2, "cutoff_len": 4096},
    }
    if preset not in table:
        raise ValueError(f"Unknown preset: {preset}")
    return table[preset]
