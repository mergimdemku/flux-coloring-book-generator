#!/usr/bin/env python3
"""
Create configs in the HuggingFace cache directory where diffusers expects them
"""

import os
import json
from pathlib import Path

# Set HuggingFace cache location
cache_dir = Path(os.environ.get('HF_HOME', '/root/.cache/huggingface'))
print(f"Creating configs in: {cache_dir}")

# Create the full HuggingFace cache structure
repo_cache = cache_dir / "hub" / "models--black-forest-labs--FLUX.1-schnell"
snapshots_dir = repo_cache / "snapshots"
refs_dir = repo_cache / "refs"

# Create directories
snapshots_dir.mkdir(parents=True, exist_ok=True)
refs_dir.mkdir(parents=True, exist_ok=True)

# Create a snapshot hash (fake but consistent)
snapshot_hash = "a1234567890abcdef1234567890abcdef12345678"
snapshot_dir = snapshots_dir / snapshot_hash

snapshot_dir.mkdir(exist_ok=True)

# Create refs/main pointing to our snapshot
with open(refs_dir / "main", "w") as f:
    f.write(snapshot_hash)

print(f"📁 Created cache structure at: {snapshot_dir}")

# Now create all the config files in the snapshot directory
configs = {
    "model_index.json": {
        "_class_name": "FluxPipeline",
        "_diffusers_version": "0.30.0",
        "scheduler": ["diffusers", "FlowMatchEulerDiscreteScheduler"],
        "text_encoder": ["transformers", "CLIPTextModel"],
        "text_encoder_2": ["transformers", "T5EncoderModel"],
        "tokenizer": ["transformers", "CLIPTokenizer"],
        "tokenizer_2": ["transformers", "T5TokenizerFast"],
        "transformer": ["diffusers", "FluxTransformer2DModel"],
        "vae": ["diffusers", "AutoencoderKL"]
    }
}

# Write main config
for filename, config in configs.items():
    with open(snapshot_dir / filename, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Created {filename}")

# Create component configs
components = {
    "scheduler/scheduler_config.json": {
        "_class_name": "FlowMatchEulerDiscreteScheduler",
        "_diffusers_version": "0.30.0",
        "num_train_timesteps": 1000,
        "shift": 1.0,
        "use_dynamic_shifting": False
    },
    "transformer/config.json": {
        "_class_name": "FluxTransformer2DModel",
        "_diffusers_version": "0.30.0",
        "in_channels": 16,
        "joint_attention_dim": 4096,
        "num_attention_heads": 24,
        "num_layers": 19,
        "patch_size": 2
    },
    "vae/config.json": {
        "_class_name": "AutoencoderKL",
        "_diffusers_version": "0.30.0",
        "in_channels": 3,
        "latent_channels": 16,
        "out_channels": 3,
        "scaling_factor": 0.3611
    }
}

for path, config in components.items():
    config_path = snapshot_dir / path
    config_path.parent.mkdir(exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ Created {path}")

print(f"\n🎉 Cache structure created!")
print(f"Location: {snapshot_dir}")
print(f"\nNow try: python flux_offline.py")