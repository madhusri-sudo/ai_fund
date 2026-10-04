"""
Hugging Face LLM helper for multi_agent_hf.

Default: LOCAL model (no HF token required).
Optional: HF Inference API if you later add HF_TOKEN.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

from app.config.settings import get_settings

# ---------------------------------------------------------------------------
# Change these HERE only (for multi_agent_hf).
#
# HF_MODE:
#   "local" → downloads/runs a small public model on your machine (NO token)
#   "api"   → Hugging Face Inference API (needs HF_TOKEN in .env)
#
# Good local starter models (public, no token) — switch by commenting:
#   "TinyLlama/TinyLlama-1.1B-Chat-v1.0"          # default
#   "HuggingFaceTB/SmolLM2-135M-Instruct"         # smaller/faster
#   "HuggingFaceTB/SmolLM2-360M-Instruct"
#   "Qwen/Qwen2.5-0.5B-Instruct"
# ---------------------------------------------------------------------------
HF_MODE = "local"
HF_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
# HF_MODEL = "HuggingFaceTB/SmolLM2-135M-Instruct"
HF_MAX_NEW_TOKENS = 512

_local_pipe: Any = None


def _hf_token() -> str:
    settings = get_settings()
    token = (
        settings.resolved_hf_token
        or os.getenv("HF_TOKEN", "")
        or os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
    )
    return token.strip()


def _configure_langsmith() -> None:
    settings = get_settings()
    if settings.langchain_api_key:
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langchain_api_key)
        os.environ.setdefault("LANGSMITH_API_KEY", settings.langchain_api_key)
    os.environ.setdefault(
        "LANGCHAIN_TRACING_V2",
        "true" if settings.langchain_tracing_v2 else "false",
    )
    os.environ.setdefault("LANGCHAIN_PROJECT", f"{settings.langchain_project}-hf")
    os.environ.setdefault(
        "LANGSMITH_TRACING",
        "true" if settings.langchain_tracing_v2 else "false",
    )
    os.environ.setdefault("LANGSMITH_PROJECT", f"{settings.langchain_project}-hf")


def _get_local_pipeline():
    """Load local transformers chat pipeline once (cached)."""
    global _local_pipe
    if _local_pipe is not None:
        return _local_pipe

    try:
        import torch
        from transformers import pipeline
    except ImportError as exc:
        raise RuntimeError(
            "Local HF mode needs: torch + transformers.\n"
            "Install with:\n"
            "  pip install -r requirements-hf.txt\n"
            "Or CPU torch:\n"
            "  pip install torch transformers accelerate "
            "--index-url https://download.pytorch.org/whl/cpu"
        ) from exc

    _configure_langsmith()
    print(f"[multi_agent_hf] Loading local model '{HF_MODEL}' (first run may download)...")

    device = 0 if torch.cuda.is_available() else -1
    _local_pipe = pipeline(
        "text-generation",
        model=HF_MODEL,
        device=device,
        torch_dtype=torch.float16 if device == 0 else torch.float32,
    )
    return _local_pipe


def _invoke_local(system_prompt: str, user_prompt: str, temperature: float) -> str:
    pipe = _get_local_pipeline()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    gen_kwargs = {
        "max_new_tokens": HF_MAX_NEW_TOKENS,
        "return_full_text": False,
    }
    if temperature and temperature > 0:
        gen_kwargs["do_sample"] = True
        gen_kwargs["temperature"] = float(temperature)
    else:
        gen_kwargs["do_sample"] = False

    outputs = pipe(messages, **gen_kwargs)

    # transformers chat pipeline usually returns generated text in [0]["generated_text"]
    generated = outputs[0]["generated_text"]
    if isinstance(generated, list):
        # some versions return message list; take last assistant content
        for item in reversed(generated):
            if isinstance(item, dict) and item.get("role") == "assistant":
                return str(item.get("content", ""))
        return str(generated)
    return str(generated).strip()


def _invoke_api(system_prompt: str, user_prompt: str, temperature: float) -> str:
    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise RuntimeError(
            "huggingface_hub is missing. Run: pip install huggingface_hub"
        ) from exc

    token = _hf_token()
    if not token:
        raise RuntimeError(
            "HF_MODE='api' needs HF_TOKEN in .env.\n"
            "You said you have no token — keep HF_MODE='local' in multi_agent_hf/llm.py "
            "(default), which needs no token."
        )

    _configure_langsmith()
    client = InferenceClient(token=token)
    response = client.chat.completions.create(
        model=HF_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=HF_MAX_NEW_TOKENS,
        temperature=temperature,
    )
    return str(response.choices[0].message.content)


def invoke_text(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """One-shot chat completion. Same signature as multi_agent.llm.invoke_text."""
    mode = (HF_MODE or "local").strip().lower()
    try:
        if mode == "api":
            return _invoke_api(system_prompt, user_prompt, temperature)
        return _invoke_local(system_prompt, user_prompt, temperature)
    except Exception as exc:
        raise RuntimeError(
            f"Hugging Face call failed (mode={mode}, model={HF_MODEL}).\n"
            f"Details: {exc}\n"
            "Local mode needs: pip install -r requirements-hf.txt\n"
            "Or switch HF_MODEL in multi_agent_hf/llm.py"
        ) from exc


def get_llm(temperature: float = 0.2):
    raise RuntimeError(
        "multi_agent_hf uses invoke_text() with a local HF model by default. "
        "Tool-calling create_agent demos remain in multi_agent/ (Gemini)."
    )
