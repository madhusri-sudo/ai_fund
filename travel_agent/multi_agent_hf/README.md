# Multi-Agent Travel (Hugging Face — local, no token)

**Full start-to-end walkthrough:** [`EXECUTION_GUIDE.md`](EXECUTION_GUIDE.md)

This is a **separate copy** of `multi_agent/`.

| Folder | Provider |
|---|---|
| `multi_agent/` | Google Gemini |
| `multi_agent_hf/` | Hugging Face **local** model (default) |

**No HF token needed** in default local mode.

---

## 1. Change model in one place

```python
# multi_agent_hf/llm.py
HF_MODE = "local"
HF_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# HF_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"  # smaller/faster
```

Flight/Hotel agents read **real inventory** (Python parsing, not LLM invention):

1. Postgres first (if running + seeded)
2. Fallback to `app/data/seed_data.py` if DB is down

The **final user answer is always an LLM call** (`agents/final_answer.py`) that writes a natural response using those inventory findings as context.

```bash
# optional live Postgres
python scripts/init_db.py
python scripts/seed_demo_data.py

# inventory-backed demo (works even if Postgres is down via seed fallback)
python multi_agent_hf/examples/02_unit_test_each_agent.py
```

---

## 2. Install (once)

```bash
cd travel_agent
pip install -r requirements.txt
pip install -r requirements-hf.txt
```

If torch install is heavy on Windows CPU:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers accelerate huggingface_hub
```

First run downloads the model weights (internet needed once). After that it runs offline.

---

## 3. Run

```bash
python multi_agent_hf/examples/01_single_agent_baseline.py
python multi_agent_hf/examples/02_unit_test_each_agent.py
python -m multi_agent_hf.main sequential
```

SmolLM2-135M is much smaller than TinyLlama/Gemini — quality is limited, but good enough for orchestration demos on CPU.

---

## 4. Optional later: HF API mode

Only if you create a free token at https://huggingface.co/settings/tokens

```env
# travel_agent/.env
HF_TOKEN=hf_...
```

```python
# multi_agent_hf/llm.py
HF_MODE = "api"
HF_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
```

You do **not** need this for the default local setup.
