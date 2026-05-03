# 🐟 TunaFactory

TunaFactory is a **dead-simple fine-tuning toolkit** for LLMs.

Goal: go from raw examples to a usable model in a few commands.

Backend: an opinionated wrapper around [LLaMA-Factory](https://github.com/hiyouga/LlamaFactory).

Priority models:
- 🥇 `meta-llama/Meta-Llama-3.1-8B-Instruct`
- 🥈 `mistralai/Mistral-7B-Instruct-v0.3`
- 🥈 `mistralai/Mistral-7B-v0.3`

---

## MVP (v0.1) — Simple and opinionated

Ship one path that works end-to-end:

1. **Prepare data**
2. **Run fine-tune**
3. **Review eval report**
4. **Export model**

No SSH. No config maze. Strong defaults.

### CLI UX

```bash
tunafactory data prepare data.jsonl
tunafactory run finetune --model llama3.1-8b --dataset prepared_dataset
tunafactory eval report --run run_001
tunafactory export --run run_001 --target gguf
```

---

## Scope

### ✅ Include in v0.1

- Data input: CSV + JSONL
- Canonical schema validation
  - missing fields
  - empty responses
  - duplicate rows (exact)
  - token length outliers
- Deterministic train/val split
- QLoRA 4-bit training presets for:
  - 1k examples
  - 10k examples
  - 100k examples
- LLaMA-Factory run config emission + subprocess launch
- Run manifest for reproducibility (`manifest.json`)
- Eval report:
  - train/val loss
  - perplexity
  - side-by-side base vs tuned outputs
- Export targets:
  - LoRA adapter
  - merged fp16
  - GGUF Q4_K_M

### ❌ Defer to v0.2+

- Multi-provider cloud orchestration
- External LLM dataset quality scoring
- Full fine-tune mode
- Multi-tenant auth
- Advanced checkpoint rollback UI

---

## Product principles

- **Defaults first:** most users should never touch LR/scheduler/rank.
- **Small surface area:** a few commands, each doing one thing well.
- **Reproducible runs:** every run has frozen config + dataset fingerprint.
- **Privacy-aware:** export to GGUF for local/offline inference.

---

## Proposed repo layout

```text
tunafactory/
├── tunafactory/
│   ├── cli.py
│   ├── data/
│   │   ├── schema.py
│   │   ├── validate.py
│   │   └── prepare.py
│   ├── run/
│   │   ├── presets.py
│   │   ├── launch.py
│   │   └── manifest.py
│   ├── eval/
│   │   ├── metrics.py
│   │   └── report.py
│   └── export/
│       └── service.py
├── tests/
└── README.md
```

---

## Definition of done (MVP)

A new user can:

1. Bring a CSV/JSONL dataset.
2. Run one command to prepare and validate it.
3. Fine-tune Llama 3.1 8B or Mistral 7B with defaults.
4. Open one report and compare base vs tuned output.
5. Export GGUF and run locally.

If this flow is smooth, MVP is successful.
