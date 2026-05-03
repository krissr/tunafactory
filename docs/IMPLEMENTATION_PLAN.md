# tunafactory Implementation Plan

This is a concrete, execution-focused plan to ship tunafactory from concept to a working v0.1 product.

## 0) Product thesis and constraints

**Goal:** make local/cloud fine-tuning boring and reliable for 1k–100k instruction examples.

**North-star user flow (4 commands):**
1. `tunafactory data prepare`
2. `tunafactory run finetune`
3. `tunafactory eval report`
4. `tunafactory export`

**Primary models:**
- `meta-llama/Meta-Llama-3.1-8B-Instruct`
- `mistralai/Mistral-7B-Instruct-v0.3`
- `mistralai/Mistral-7B-v0.3`

**Engine choice:** LLaMA-Factory as backend (best tradeoff: broad model support + mature SFT/QLoRA pipeline).

---

## 1) Architecture: thin wrapper, strict contracts

Build tunafactory as a thin orchestrator around LLaMA-Factory:

- **Data layer** (ingestion, schema, checks, split, fingerprints)
- **Run layer** (preset resolution, config emission, subprocess execution)
- **Eval layer** (loss/perplexity ingestion + qualitative comparisons)
- **Export layer** (adapter, merged, gguf)

### 1.1 System boundaries

- tunafactory does:
  - deterministic preprocessing
  - safe defaults and presets
  - run artifact management
  - report generation
- LLaMA-Factory does:
  - model loading/training runtime
  - PEFT/QLoRA internals
  - checkpointing and merge ops

### 1.2 Artifact layout (run-centric)

```text
runs/
  run_YYYYMMDD_HHMMSS_xxxx/
    manifest.json
    dataset/
      prepared_train.jsonl
      prepared_val.jsonl
      fingerprint.sha256
      data_quality.json
    configs/
      llamafactory_train.yaml
      export.yaml
    checkpoints/
    logs/
      trainer.log
      metrics.jsonl
    eval/
      report.md
      report.html
      samples.jsonl
    export/
      adapter/
      merged-fp16/
      gguf/
```

---

## 2) Data contract (hard requirement)

## 2.1 Canonical schema

Prepared row schema:

```json
{
  "id": "string",
  "messages": [
    {"role": "system", "content": "optional"},
    {"role": "user", "content": "required"},
    {"role": "assistant", "content": "required"}
  ],
  "meta": {
    "source": "optional",
    "tags": ["optional"],
    "group_id": "optional"
  }
}
```

Keep only what training needs. Everything else is dropped or preserved in `meta`.

## 2.2 Input adapters

Support v0.1:
- JSONL adapter
- CSV adapter with column mapping flags:
  - `--input-col`
  - `--output-col`
  - optional `--system-col`

## 2.3 Validation passes (ordered)

1. Structural validation (required fields/types)
2. Empty/whitespace response detection
3. Exact duplicate detection
4. Length checks (token counts)
5. Conversation sanity checks:
   - last turn must be assistant
   - at least one user turn

## 2.4 Tokenizer-aware stats

Compute per-row tokens with selected model tokenizer and produce:
- p50/p90/p95/p99 lengths
- outlier rows (hard cap + soft warnings)
- estimated train tokens total

## 2.5 Split strategy

- Deterministic train/val split via seed
- Default 98/2 for 1k and 10k; 99/1 for 100k
- Optional grouping (`group_id`) to avoid leakage across splits

---

## 3) Presets: one-click profiles for 1k / 10k / 100k

Create fixed presets keyed by dataset size bucket.

## 3.1 Preset table (initial defaults)

- **small (<= 2k)**
  - LoRA rank: 16
  - lr: 2e-4
  - epochs: 4
  - warmup_ratio: 0.05
  - cutoff_len: 2048
- **medium (2k–20k)**
  - rank: 32
  - lr: 1.5e-4
  - epochs: 3
  - warmup_ratio: 0.03
  - cutoff_len: 3072
- **large (>20k)**
  - rank: 64
  - lr: 1e-4
  - epochs: 2
  - warmup_ratio: 0.02
  - cutoff_len: 4096

Global defaults:
- QLoRA 4-bit (`nf4`, `double_quant=true`, `bf16=true` when supported)
- gradient checkpointing on
- cosine scheduler
- eval every fixed step budget

## 3.2 Hardware-aware auto-scaling

At runtime detect GPU VRAM and adjust:
- `per_device_train_batch_size`
- `gradient_accumulation_steps`
- `max_seq_len` (within safe bounds)

Produce a clear warning if selected model/preset cannot fit.

---

## 4) CLI design and behavior

## 4.1 Commands

```bash
tunafactory data prepare <path> [--format csv|jsonl] [--model llama3.1-8b]
tunafactory run finetune --model <alias> --dataset <prepared_dir> [--preset auto]
tunafactory eval report --run <run_id> [--n-samples 50]
tunafactory export --run <run_id> --target adapter|merged|gguf
```

## 4.2 UX requirements

- Dry run mode for every command (`--dry-run`)
- Progress bars and concise logs
- Human-readable errors with actionable fixes
- Every command writes machine-readable JSON summary

---

## 5) Evaluation and reporting

## 5.1 Quantitative metrics

For each run, track and report:
- train loss curve
- val loss curve
- best val checkpoint
- perplexity (val)
- token throughput and wall-clock time

## 5.2 Qualitative comparison set

Generate side-by-side outputs on a fixed eval slice:
- base model output
- tuned model output
- reference answer

Score framework (v0.1 simple):
- exact/substring heuristic where relevant
- optional rubric tags (helpfulness, correctness, style)

## 5.3 Report outputs

- `report.md` for git/history
- `report.html` for sharing
- `samples.jsonl` for downstream analysis

---

## 6) Export pipeline

Support:
1. LoRA adapter (default)
2. merged fp16
3. GGUF Q4_K_M

Rules:
- Verify export artifacts and checksums
- Write `export_manifest.json` with provenance:
  - base model
  - run id
  - commit hash
  - dataset fingerprint

---

## 7) Security, privacy, and compliance guardrails

For likely professional data (medical/legal):
- default local disk only; no external uploads
- explicit redaction hooks during data prep
- PII scanner stub in v0.1 (regex + configurable rules)
- retain minimal logs (no raw dataset echoing)

---

## 8) Scenario-specific guidance (three user archetypes)

## 8.1 Doctor (10k patient conversations)

Recommended path:
- de-identify first (names, phone, MRN, addresses)
- medium preset
- strict group split by patient/thread id
- eval slice includes hard safety prompts

Success criteria:
- improved clinical style consistency
- no regression on safety refusals

## 8.2 Civil engineering lawyer (100k examples)

Recommended path:
- large preset
- stronger dedup and contradiction sampling checks
- 99/1 split with grouped cases
- longer context cutoff (3072–4096)

Success criteria:
- citation-like response style consistency
- better domain terminology precision

## 8.3 Hobby user (1k examples)

Recommended path:
- small preset
- prioritize data cleaning over hyperparameter tuning
- quick eval with 30–50 prompts

Success criteria:
- clear stylistic adaptation without overfitting artifacts

---

## 9) Implementation roadmap (8 weeks)

## Phase 1 (Week 1–2): skeleton + data prep

Deliverables:
- project package + CLI scaffold
- JSONL/CSV ingestion
- schema + validation + split
- dataset fingerprint + quality report

Exit criteria:
- `tunafactory data prepare` stable on sample datasets

## Phase 2 (Week 3–4): training orchestration

Deliverables:
- preset engine (`small/medium/large/auto`)
- model alias mapping
- LLaMA-Factory config emitter
- subprocess launch + run manifest + logs

Exit criteria:
- successful QLoRA run for Llama 3.1 8B and Mistral 7B on one GPU profile

## Phase 3 (Week 5): eval reporting

Deliverables:
- parse training metrics
- base vs tuned generation comparer
- markdown/html report generation

Exit criteria:
- single-command report with quantitative + qualitative sections

## Phase 4 (Week 6): export

Deliverables:
- adapter/merged/gguf export commands
- artifact checksums + export manifest

Exit criteria:
- exported GGUF loads in a local inference stack

## Phase 5 (Week 7): hardening

Deliverables:
- error handling + retries
- deterministic tests and fixture datasets
- docs/playbooks for three archetypes

Exit criteria:
- end-to-end reproducibility validated across two clean environments

## Phase 6 (Week 8): beta release

Deliverables:
- v0.1 tag
- getting-started tutorial
- known limitations doc

Exit criteria:
- 3 pilot users complete the 4-command flow without developer intervention

---

## 10) Engineering checklist (must-have tasks)

- [ ] `tunafactory/data/schema.py` — canonical pydantic models
- [ ] `tunafactory/data/prepare.py` — adapters + transform pipeline
- [ ] `tunafactory/data/validate.py` — validation passes + reports
- [ ] `tunafactory/run/presets.py` — auto preset logic + hardware adaptation
- [ ] `tunafactory/run/launch.py` — LLaMA-Factory process orchestration
- [ ] `tunafactory/run/manifest.py` — immutable run metadata
- [ ] `tunafactory/eval/metrics.py` — curves + summary metrics
- [ ] `tunafactory/eval/report.py` — markdown/html output
- [ ] `tunafactory/export/service.py` — export targets + checksums
- [ ] integration tests for full flow on toy dataset

---

## 11) MVP acceptance tests

1. **Data prep test:** invalid rows are caught; clean set exported deterministically.
2. **Train test:** single command launches and finishes on small fixture.
3. **Eval test:** report contains loss/perplexity + side-by-side examples.
4. **Export test:** GGUF artifact produced with manifest/checksum.
5. **Repro test:** rerun with same seed and data gives same split + near-identical metrics trend.

---

## 12) Suggested “simple first” defaults

- Default model alias: `llama3.1-8b`
- Default preset: `auto`
- Default split seed: `42`
- Default val ratio: inferred from dataset size
- Default output root: `./runs`

Only expose advanced knobs under `--advanced` namespace.

---

## 13) Future v0.2+ (after MVP proves value)

- lightweight web dashboard
- DPO/ORPO alignment stage
- resume/branch runs from checkpoints
- cloud templates (AWS/GCP) with same manifest contract

The key: preserve the same 4-command user mental model.
