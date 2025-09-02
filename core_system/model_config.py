"""
Model Configuration - Points to existing cached FLUX models
"""

import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Set the cache directory to your existing model cache
CACHE_DIR = PROJECT_ROOT / "cache"
MODEL_CACHE_DIR = CACHE_DIR / "models--black-forest-labs--FLUX.1-schnell"

# Configure HuggingFace to use your local cache
os.environ['HF_HOME'] = str(CACHE_DIR)
os.environ['HUGGINGFACE_HUB_CACHE'] = str(CACHE_DIR)
os.environ['TRANSFORMERS_CACHE'] = str(CACHE_DIR)

# Model configuration
MODEL_CONFIG = {
    'model_id': 'black-forest-labs/FLUX.1-schnell',
    'cache_dir': str(CACHE_DIR),
    'local_files_only': True,  # IMPORTANT: Use only local files, don't download
    'revision': 'main',
    'torch_dtype': 'float16'  # or 'float32' for CPU
}

print(f"✅ Model cache configured at: {CACHE_DIR}")
print(f"✅ Using existing models - no download needed")