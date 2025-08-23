#!/usr/bin/env python3
"""
LOCAL SETUP FOR RTX 3070 - Optimized for 8GB VRAM + 128GB RAM
Perfect for local development and testing
"""

import os
import sys
from pathlib import Path

print("=" * 70)
print("FLUX LOCAL SETUP - RTX 3070 + 128GB RAM")
print("=" * 70)

# Check Python version
print(f"\nPython: {sys.version}")

# Create setup script
setup_commands = """
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
# Windows: venv\\Scripts\\activate
# Linux/Mac: source venv/bin/activate

# 3. Install PyTorch for RTX 3070 (CUDA 11.8 or 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 4. Install required packages
pip install diffusers transformers accelerate safetensors
pip install xformers  # For memory efficiency
pip install flask pillow opencv-python
pip install huggingface-hub

# 5. Create directory structure
mkdir -p models/flux
mkdir -p models/vae  
mkdir -p models/clip
mkdir -p output
mkdir -p cache
"""

print("\n📋 SETUP INSTRUCTIONS:")
print(setup_commands)

print("\n" + "=" * 70)
print("DOWNLOAD INSTRUCTIONS")
print("=" * 70)

download_script = """
# Set your HuggingFace token
export HF_TOKEN=your_token_here

# Download FLUX schnell (4-step fast model, better for 8GB VRAM)
huggingface-cli download black-forest-labs/FLUX.1-schnell \\
    --local-dir ./cache/flux-schnell \\
    --token $HF_TOKEN

# Or download individual files to save space:
# Just the essential files for inference
huggingface-cli download black-forest-labs/FLUX.1-schnell \\
    transformer/diffusion_pytorch_model.safetensors \\
    vae/diffusion_pytorch_model.safetensors \\
    --local-dir ./cache/flux-schnell \\
    --token $HF_TOKEN
"""

print("\n📥 DOWNLOAD COMMANDS:")
print(download_script)

print("\n" + "=" * 70)
print("RTX 3070 OPTIMIZATION TIPS")
print("=" * 70)

tips = """
1. USE FLUX.1-schnell (4 steps) not FLUX.1-dev (50 steps)
2. Start with 512x512 or 768x768 resolution
3. Use float16 precision
4. Enable xformers for memory efficiency
5. Use CPU offloading for large models
6. Your 128GB RAM is PERFECT for model offloading!

VRAM USAGE ESTIMATES:
- 512x512: ~6-7GB VRAM
- 768x768: ~7-8GB VRAM  
- 1024x1024: May OOM, use CPU offload

YOUR ADVANTAGE: 128GB RAM means you can:
- Load full models without compression
- Use CPU offloading aggressively
- Run multiple generations in sequence
- Cache everything in RAM
"""

print(tips)

# Save config file
config = {
    "device": "cuda",
    "dtype": "float16",
    "model": "FLUX.1-schnell",
    "resolution": 768,
    "steps": 4,
    "cpu_offload": True,
    "use_xformers": True,
    "cache_dir": "./cache",
    "output_dir": "./output"
}

import json
with open("rtx3070_config.json", "w") as f:
    json.dump(config, f, indent=2)

print("\n✅ Created rtx3070_config.json")
print("\nNext: Run local_flux_rtx3070.py after setup")