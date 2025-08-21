# Models Directory

Place your FLUX models in the following structure:

## Required Models

### FLUX Transformer Model
- **File**: `flux/flux1-schnell.safetensors` (22GB)
- **Source**: https://huggingface.co/black-forest-labs/FLUX.1-schnell
- **Description**: Main FLUX.1-schnell model for fast generation

### Text Encoders
- **File**: `clip/clip_l.safetensors` (246MB)
- **Source**: https://huggingface.co/comfyanonymous/flux_text_encoders
- **Description**: CLIP-L text encoder

- **File**: `clip/t5xxl_fp16.safetensors` (9.8GB)
- **Source**: https://huggingface.co/comfyanonymous/flux_text_encoders
- **Description**: T5-XXL text encoder

### VAE Model
- **File**: `vae/ae.safetensors` (335MB)
- **Source**: https://huggingface.co/black-forest-labs/FLUX.1-schnell
- **Description**: FLUX autoencoder

## Directory Structure
```
models/
├── flux/
│   └── flux1-schnell.safetensors
├── clip/
│   ├── clip_l.safetensors
│   └── t5xxl_fp16.safetensors
└── vae/
    └── ae.safetensors
```

**Total Size**: ~32GB

## Download Instructions

1. Get Hugging Face token from https://huggingface.co/settings/tokens
2. Login: `huggingface-cli login`
3. Download models to respective folders
4. Application will automatically detect and load local models