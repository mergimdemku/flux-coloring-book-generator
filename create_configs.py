#!/usr/bin/env python3
"""
Create minimal config files locally to avoid any downloads
"""

import json
from pathlib import Path

print("🔧 Creating local config files...")

# Create cache structure
cache_base = Path("cache/models--black-forest-labs--FLUX.1-schnell/snapshots/main")
cache_base.mkdir(parents=True, exist_ok=True)

# Minimal model_index.json
model_index = {
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

with open(cache_base / "model_index.json", "w") as f:
    json.dump(model_index, f, indent=2)

# Scheduler config
scheduler_dir = cache_base / "scheduler"
scheduler_dir.mkdir(exist_ok=True)

scheduler_config = {
    "_class_name": "FlowMatchEulerDiscreteScheduler",
    "_diffusers_version": "0.30.0",
    "base_image_seq_len": 256,
    "base_shift": 0.5,
    "max_image_seq_len": 4096,
    "max_shift": 1.15,
    "num_train_timesteps": 1000,
    "shift": 1.0,
    "use_dynamic_shifting": False
}

with open(scheduler_dir / "scheduler_config.json", "w") as f:
    json.dump(scheduler_config, f, indent=2)

# Transformer config
transformer_dir = cache_base / "transformer"
transformer_dir.mkdir(exist_ok=True)

transformer_config = {
    "_class_name": "FluxTransformer2DModel",
    "_diffusers_version": "0.30.0",
    "attention_head_dim": 128,
    "guidance_embeds": True,
    "in_channels": 16,
    "joint_attention_dim": 4096,
    "num_attention_heads": 24,
    "num_layers": 19,
    "num_single_layers": 38,
    "patch_size": 2,
    "pooled_projection_dim": 768,
    "axes_dims_rope": [16, 56, 56]
}

with open(transformer_dir / "config.json", "w") as f:
    json.dump(transformer_config, f, indent=2)

# VAE config
vae_dir = cache_base / "vae"
vae_dir.mkdir(exist_ok=True)

vae_config = {
    "_class_name": "AutoencoderKL",
    "_diffusers_version": "0.30.0",
    "act_fn": "silu",
    "block_out_channels": [128, 256, 512, 512],
    "down_block_types": ["DownEncoderBlock2D"] * 4,
    "in_channels": 3,
    "latent_channels": 16,
    "layers_per_block": 2,
    "norm_num_groups": 32,
    "out_channels": 3,
    "sample_size": 1024,
    "scaling_factor": 0.3611,
    "up_block_types": ["UpDecoderBlock2D"] * 4
}

with open(vae_dir / "config.json", "w") as f:
    json.dump(vae_config, f, indent=2)

print("✅ Created minimal configs in cache/")
print("Now run: python flux_offline.py")
print("\nNote: These are minimal configs - full generation may need more")