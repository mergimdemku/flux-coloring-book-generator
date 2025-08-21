#!/usr/bin/env python3
"""
FLUX GPU WORKING - Find correct cache and run on RTX 5090
"""

import os
import torch
from pathlib import Path
import logging
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ["CUDA_LAUNCH_BLOCKING"] = "0"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_flux_cache():
    """Find the actual FLUX cache with model files"""
    
    # Check multiple possible locations
    search_paths = [
        Path("cache"),
        Path.home() / ".cache/huggingface/hub",
        Path("/root/.cache/huggingface/hub"),
    ]
    
    for base_path in search_paths:
        if not base_path.exists():
            continue
            
        # Look for FLUX directories
        flux_dirs = list(base_path.glob("**/models--black-forest-labs--FLUX.1-schnell/snapshots/*"))
        
        for flux_dir in flux_dirs:
            # Check if this directory has the actual model files
            has_transformer = (flux_dir / "transformer").exists()
            has_vae = (flux_dir / "vae").exists()
            has_index = (flux_dir / "model_index.json").exists()
            
            if has_transformer or has_vae or has_index:
                logger.info(f"✅ Found FLUX cache with models: {flux_dir}")
                return flux_dir
    
    # If not found in standard structure, look for downloaded files
    for base_path in search_paths:
        if not base_path.exists():
            continue
        
        # Look for any directory with transformer subdirectory
        transformer_dirs = list(base_path.glob("**/transformer"))
        for t_dir in transformer_dirs:
            parent = t_dir.parent
            if (parent / "vae").exists() or (parent / "model_index.json").exists():
                logger.info(f"✅ Found FLUX cache: {parent}")
                return parent
    
    return None

def main():
    """Run FLUX on RTX 5090"""
    
    logger.info("\n" + "="*70)
    logger.info("FLUX GPU WORKING - RTX 5090")
    logger.info("="*70)
    
    # GPU info
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        logger.info(f"GPU: {gpu_name} ({vram:.1f}GB)")
    
    device = "cuda"
    dtype = torch.float16
    
    # Find the correct cache
    cache_path = find_flux_cache()
    
    if not cache_path:
        logger.error("❌ No FLUX cache found!")
        logger.info("\nLooking for cache in:")
        logger.info("  - cache/")
        logger.info("  - ~/.cache/huggingface/hub/")
        
        # Try to find any safetensors files
        logger.info("\nSearching for model files...")
        for ext in ["*.safetensors", "*.bin"]:
            files = list(Path(".").glob(f"**/{ext}"))[:5]
            if files:
                logger.info(f"Found {ext} files:")
                for f in files:
                    logger.info(f"  - {f}")
        return
    
    logger.info(f"\n📁 Using cache: {cache_path}")
    
    # List what's in the cache
    cache_contents = list(cache_path.glob("*"))[:10]
    logger.info("Cache contents:")
    for item in cache_contents:
        if item.is_dir():
            logger.info(f"  📁 {item.name}/")
        else:
            logger.info(f"  📄 {item.name}")
    
    try:
        from diffusers import FluxPipeline
        
        logger.info("\n🚀 Loading FLUX pipeline...")
        
        # Load from the found cache directory
        pipeline = FluxPipeline.from_pretrained(
            str(cache_path),
            torch_dtype=dtype,
            local_files_only=True
        )
        
        logger.info("✅ Pipeline loaded!")
        
        # Move to GPU
        logger.info(f"Moving to {device}...")
        pipeline = pipeline.to(device)
        logger.info(f"✅ On GPU!")
        
        # Enable optimizations
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            pipeline.enable_model_cpu_offload()
            logger.info("✅ Enabled CPU offload")
        
        # Test generation
        logger.info("\n🎨 Generating on RTX 5090...")
        
        prompt = "coloring book page of a dragon, black and white line art"
        
        try:
            with torch.cuda.amp.autocast():
                image = pipeline(
                    prompt=prompt,
                    num_inference_steps=4,
                    guidance_scale=0.0,
                    height=1024,
                    width=1024,
                    generator=torch.Generator(device=device).manual_seed(42)
                ).images[0]
            
            output_path = "rtx5090_generated.png"
            image.save(output_path)
            
            logger.info(f"✅ SUCCESS! Generated: {output_path}")
            logger.info("\n🎊 RTX 5090 WORKS WITH FLUX!")
            
        except RuntimeError as e:
            if "no kernel image" in str(e) or "CUDA error" in str(e):
                logger.error("❌ CUDA kernel error")
                logger.info("\nThe PyTorch nightly might not have full sm_120 support yet.")
                logger.info("Try running with smaller resolution:")
                logger.info("  height=512, width=512")
            else:
                raise
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()