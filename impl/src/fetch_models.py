"""Pre-download every model the framework needs, so experiments start fast."""
import os, sys
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
from huggingface_hub import snapshot_download

MODELS = [
    "sentence-transformers/all-MiniLM-L6-v2",
    "BAAI/bge-m3",
    "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "cross-encoder/nli-deberta-v3-small",
]
for m in MODELS:
    print(f"[fetch] {m}", flush=True)
    p = snapshot_download(repo_id=m, allow_patterns=["*.json", "*.txt", "*.bin", "*.safetensors", "*.model", "*.spm"])
    print(f"[ok]    {m} -> {p}", flush=True)
print("ALL MODELS READY", flush=True)
