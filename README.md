# 🐟 tunafactory

tunafactory is a **dead-simple fine-tuning toolkit** for LLMs.

Backend: wrapper + orchestrator around [LLaMA-Factory](https://github.com/hiyouga/LlamaFactory).

Priority models:
- 🥇 `meta-llama/Meta-Llama-3.1-8B-Instruct`
- 🥈 `mistralai/Mistral-7B-Instruct-v0.3`
- 🥈 `mistralai/Mistral-7B-v0.3`

## Requirements

- Python 3.10+
- `llamafactory-cli` installed and available in `PATH`
- CUDA GPU environment configured for training

## Quickstart

```bash
python -m tunafactory.cli data prepare data.jsonl --output-dir prepared_dataset
python -m tunafactory.cli run finetune --model llama3.1-8b --dataset prepared_dataset --preset small
python -m tunafactory.cli eval report --run runs/run_001
python -m tunafactory.cli export --run runs/run_001 --target gguf
```


## How to use tunafactory (step-by-step)

### 1) Install prerequisites

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install llamafactory
```

Make sure `llamafactory-cli` is on your `PATH` and that your CUDA GPU stack is configured.

### 2) Prepare your dataset

Create a JSONL file where each line is one training sample. Then run:

```bash
python -m tunafactory.cli data prepare data.jsonl --output-dir prepared_dataset
```

This creates the prepared train/validation artifacts expected by the runner.

### 3) Launch fine-tuning

```bash
python -m tunafactory.cli run finetune \
  --model llama3.1-8b \
  --dataset prepared_dataset \
  --preset small
```

A new run directory is created under `runs/` (for example `runs/run_001`) with:
- `configs/llamafactory_train.json` (generated backend config)
- `logs/trainer.log` (captured training logs)
- `checkpoints/` (adapter/checkpoint outputs)
- `manifest.json` (run metadata)

### 4) Generate an evaluation report

```bash
python -m tunafactory.cli eval report --run runs/run_001
```

### 5) Export artifacts

```bash
python -m tunafactory.cli export --run runs/run_001 --target gguf
```

Use `--target adapter` if you only want the adapter path.

### 6) Troubleshooting

- **`llamafactory-cli not found`**: install LLaMA-Factory (`pip install llamafactory`) and verify your environment is activated.
- **CUDA/runtime failures**: verify drivers, CUDA toolkit compatibility, and GPU visibility.
- **Unexpected training behavior**: inspect `runs/<run_id>/logs/trainer.log` and the generated config in `runs/<run_id>/configs/`.

## Detailed implementation plan

See `docs/IMPLEMENTATION_PLAN.md` for the execution roadmap.
