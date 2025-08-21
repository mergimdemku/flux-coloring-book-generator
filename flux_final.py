#!/usr/bin/env python3
"""
FLUX FINAL - Handle CUDA compatibility and use cached models
"""

import os
import torch
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Final FLUX loader with CUDA compatibility fixes"""
    
    logger.info("\n" + "="*70)
    logger.info("FLUX FINAL - RTX 5090 Compatible")
    logger.info("="*70)
    
    # Check CUDA compatibility
    if torch.cuda.is_available():
        gpu = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        capability = torch.cuda.get_device_capability()
        logger.info(f"GPU: {gpu} ({vram:.1f}GB)")
        logger.info(f"CUDA Capability: sm_{capability[0]}{capability[1]}")
        
        # Check PyTorch CUDA support
        cuda_version = torch.version.cuda
        logger.info(f"PyTorch CUDA: {cuda_version}")
        
        if capability >= (12, 0):  # RTX 5090 is sm_120
            logger.warning("⚠️  RTX 5090 detected - using CPU fallback for compatibility")
            device = "cpu"
            dtype = torch.float32  # CPU doesn't support float16 well
        else:
            device = "cuda"
            dtype = torch.float16
    else:
        device = "cpu"
        dtype = torch.float32
        
    logger.info(f"Using device: {device}, dtype: {dtype}")
    
    try:
        from diffusers import FluxPipeline
        
        # Use the cached models from previous download
        logger.info("\n📦 Loading from cache (no downloads)...")
        
        # Force offline mode
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        
        # Load the full pipeline from cache
        pipeline = FluxPipeline.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            torch_dtype=dtype,
            device_map=None,  # Manual device placement
            local_files_only=True,
            cache_dir="cache"
        )
        
        logger.info("✅ Pipeline loaded from cache")
        
        # Move to appropriate device
        pipeline = pipeline.to(device)
        logger.info(f"✅ Moved to {device}")
        
        # Test generation
        logger.info("\n🎨 Testing image generation...")
        
        prompt = "coloring book page of a cute dragon, black and white line art, simple outlines"
        
        # Generate with appropriate settings for device
        if device == "cpu":
            logger.info("Generating on CPU (will be slower but stable)...")
            with torch.no_grad():
                image = pipeline(
                    prompt=prompt,
                    num_inference_steps=4,  # schnell optimal
                    guidance_scale=0.0,     # schnell doesn't use guidance
                    height=512,             # Smaller for CPU
                    width=512,
                    generator=torch.Generator().manual_seed(42)
                ).images[0]
        else:
            logger.info("Generating on GPU...")
            with torch.no_grad():
                image = pipeline(
                    prompt=prompt,
                    num_inference_steps=4,
                    guidance_scale=0.0,
                    height=1024,
                    width=1024,
                    generator=torch.Generator(device=device).manual_seed(42)
                ).images[0]
        
        # Save result
        output_path = "generated_coloring_page.png"
        image.save(output_path)
        
        logger.info(f"✅ Generated and saved: {output_path}")
        logger.info("\n🎊 COMPLETE SUCCESS!")
        logger.info("Your FLUX coloring book generator is working!")
        
        # Show image info
        logger.info(f"Image size: {image.size}")
        logger.info(f"Prompt: {prompt}")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.info("\nTroubleshooting:")
        logger.info("1. Check if cache exists: ls -la cache/")
        logger.info("2. Try running with CUDA_LAUNCH_BLOCKING=1")
        logger.info("3. Consider using CPU mode for RTX 5090 compatibility")
        
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()