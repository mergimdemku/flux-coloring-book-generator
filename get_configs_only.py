#!/usr/bin/env python3
"""
Get ONLY the config files needed for FLUX - no model downloads
"""

import os
import json
from pathlib import Path
from huggingface_hub import hf_hub_download

# Create cache directory
cache_dir = Path("cache/configs")
cache_dir.mkdir(parents=True, exist_ok=True)

print("📥 Downloading ONLY config files (few KB)...")
print("NOT downloading models - you already have those!")

# Config files we need (small JSON files)
config_files = [
    "model_index.json",
    "scheduler/scheduler_config.json", 
    "text_encoder/config.json",
    "text_encoder_2/config.json",
    "tokenizer/tokenizer_config.json",
    "tokenizer/special_tokens_map.json",
    "tokenizer/merges.txt",
    "tokenizer/vocab.json",
    "tokenizer_2/tokenizer_config.json",
    "tokenizer_2/special_tokens_map.json",
    "tokenizer_2/spiece.model",
    "tokenizer_2/tokenizer.json",
    "transformer/config.json",
    "vae/config.json"
]

repo_id = "black-forest-labs/FLUX.1-schnell"

for file in config_files:
    try:
        print(f"  ↓ {file}")
        downloaded = hf_hub_download(
            repo_id=repo_id,
            filename=file,
            cache_dir=str(cache_dir),
            local_files_only=False
        )
        print(f"  ✓ {file}")
    except Exception as e:
        print(f"  ✗ {file}: {e}")

print("\n✅ Config files downloaded to cache/configs/")
print("Now you can run: python flux_offline.py")