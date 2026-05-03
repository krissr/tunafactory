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

## Detailed implementation plan

If this flow is smooth, MVP is successful.

## Detailed implementation plan

See `docs/IMPLEMENTATION_PLAN.md` for the execution roadmap.
