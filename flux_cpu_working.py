#!/usr/bin/env python3
"""
FLUX CPU WORKING - Find correct cache and run on CPU for RTX 5090
"""

import os
import torch
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_flux_cache():
    """Find where FLUX models are cached"""
    possible_locations = [
        Path("cache/models--black-forest-labs--FLUX.1-schnell"),
        Path.home() / ".cache/huggingface/hub/models--black-forest-labs--FLUX.1-schnell",
        Path("/root/.cache/huggingface/hub/models--black-forest-labs--FLUX.1-schnell"),
    ]
    
    for location in possible_locations:
        if location.exists():
            snapshots = location / "snapshots"
            if snapshots.exists():
                # Get the latest snapshot
                snapshot_dirs = list(snapshots.iterdir())
                if snapshot_dirs:
                    return snapshot_dirs[0]
    
    return None

def main():
    """Load FLUX from correct cache location"""
    
    logger.info("\n" + "="*70)
    logger.info("FLUX CPU WORKING - RTX 5090 Compatible")
    logger.info("="*70)
    
    # Force CPU mode for RTX 5090
    device = "cpu"
    dtype = torch.float32
    logger.info(f"Using: {device} with {dtype}")
    
    # Find cache
    cache_path = find_flux_cache()
    if not cache_path:
        logger.error("❌ Cache not found! Run flux_authenticated.py first to download.")
        return
    
    logger.info(f"✅ Found cache at: {cache_path}")
    
    # Check what's in cache
    if (cache_path / "model_index.json").exists():
        logger.info("✅ model_index.json found")
    
    try:
        from diffusers import FluxPipeline
        
        logger.info("\n📦 Loading from local cache...")
        
        # Load directly from cache directory
        pipeline = FluxPipeline.from_pretrained(
            str(cache_path),  # Use the exact cache path
            torch_dtype=dtype,
            device_map=None,
            local_files_only=True
        )
        
        logger.info("✅ Pipeline loaded from cache!")
        
        # Move to CPU
        pipeline = pipeline.to(device)
        logger.info(f"✅ Moved to {device}")
        
        # Enable CPU optimizations
        if hasattr(pipeline, 'enable_attention_slicing'):
            pipeline.enable_attention_slicing()
            logger.info("✅ Enabled attention slicing for CPU")
        
        # Test generation
        logger.info("\n🎨 Generating on CPU (will be slow but works)...")
        logger.info("⏱️  This may take 5-10 minutes on CPU...")
        
        prompt = "coloring book page of a dragon, black and white line art, simple outlines only"
        
        with torch.no_grad():
            # Use smaller size for CPU
            image = pipeline(
                prompt=prompt,
                num_inference_steps=4,  # schnell optimal
                guidance_scale=0.0,     # schnell doesn't use guidance
                height=256,             # Very small for CPU test
                width=256,
                generator=torch.Generator().manual_seed(42)
            ).images[0]
        
        # Save result
        output_path = "cpu_generated_coloring_page.png"
        image.save(output_path)
        
        logger.info(f"✅ Generated and saved: {output_path}")
        logger.info("\n🎊 SUCCESS! FLUX is working on CPU!")
        logger.info("Note: CPU generation is slow. For faster generation:")
        logger.info("1. Wait for PyTorch RTX 5090 support")
        logger.info("2. Use a different GPU (RTX 4090, etc.)")
        logger.info("3. Use cloud GPU services")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.info("\nDebug info:")
        logger.info(f"Cache path: {cache_path}")
        logger.info(f"Files in cache: {list(cache_path.glob('*'))[:5]}")
        
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()