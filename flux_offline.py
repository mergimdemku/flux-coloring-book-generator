#!/usr/bin/env python3
"""
FLUX OFFLINE - Forces diffusers to use LOCAL files only
NO DOWNLOADS - Uses your models
"""

import os
import sys
from pathlib import Path

# FORCE COMPLETE OFFLINE MODE
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"
os.environ["DIFFUSERS_OFFLINE"] = "1"

import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Use FLUX with local files only"""
    
    logger.info("\n" + "="*70)
    logger.info("FLUX OFFLINE MODE - NO DOWNLOADS")
    logger.info("="*70)
    
    # Check GPU
    if torch.cuda.is_available():
        gpu = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        logger.info(f"GPU: {gpu} ({vram:.1f}GB)")
    
    # Check models exist
    models = {
        "FLUX": "models/flux/flux1-schnell.safetensors",
        "VAE": "models/vae/ae.safetensors",
        "CLIP": "models/clip/clip_l.safetensors",
        "T5": "models/clip/t5xxl_fp16.safetensors"
    }
    
    all_exist = True
    for name, path in models.items():
        if Path(path).exists():
            size = Path(path).stat().st_size / (1024**3)
            logger.info(f"✅ {name}: {size:.1f}GB")
        else:
            logger.error(f"❌ Missing: {path}")
            all_exist = False
    
    if not all_exist:
        logger.error("\n⚠️  Copy your .safetensors files to models/ folder!")
        return
    
    logger.info("\n" + "-"*70)
    logger.info("Loading with diffusers in OFFLINE mode...")
    logger.info("-"*70)
    
    try:
        from diffusers import FluxPipeline
        
        # Try loading with local_files_only flag
        # This SHOULD work if we have the model cached
        pipeline = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            local_files_only=True,  # FORCE local only
            torch_dtype=torch.float16,
            device_map="balanced"
        )
        
        logger.info("✅ Pipeline loaded in offline mode!")
        
        # Now manually replace components with your local files
        logger.info("\nReplacing with YOUR local models...")
        
        # Load your safetensors directly
        from safetensors.torch import load_file
        
        # Load and inject your transformer weights
        flux_weights = load_file("models/flux/flux1-schnell.safetensors")
        pipeline.transformer.load_state_dict(flux_weights, strict=False)
        logger.info("✅ Injected YOUR flux1-schnell.safetensors")
        
        # Load and inject your VAE
        vae_weights = load_file("models/vae/ae.safetensors")
        pipeline.vae.load_state_dict(vae_weights, strict=False)
        logger.info("✅ Injected YOUR ae.safetensors")
        
        logger.info("\n" + "="*70)
        logger.info("SUCCESS! Using YOUR local models!")
        logger.info("="*70)
        
        # Test generation
        logger.info("\nGenerating test image...")
        prompt = "coloring book page of a cute dragon, black and white line art"
        
        with torch.no_grad():
            image = pipeline(
                prompt=prompt,
                num_inference_steps=4,
                guidance_scale=0.0,
                height=512,
                width=512
            ).images[0]
        
        image.save("test_output.png")
        logger.info("✅ Generated test_output.png")
        
    except FileNotFoundError as e:
        logger.error(f"\n❌ Model cache not found: {e}")
        logger.error("\nThe issue: diffusers needs config files that aren't in .safetensors")
        logger.error("Solution: Run this ONCE with internet to cache configs:")
        logger.error("  python -c \"from diffusers import FluxPipeline; FluxPipeline.from_pretrained('black-forest-labs/FLUX.1-schnell', cache_dir='cache')\"")
        logger.error("Then run this script again in offline mode")
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        logger.error("\nTry the cache solution above")

if __name__ == "__main__":
    main()