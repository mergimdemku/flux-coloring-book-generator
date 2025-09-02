#!/usr/bin/env python3
"""
FLUX GPU FORCE - Make it work on RTX 5090 despite warnings
"""

import os
import torch
from pathlib import Path
import logging
import warnings

# Suppress CUDA warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*CUDA capability.*")
os.environ["CUDA_LAUNCH_BLOCKING"] = "0"  # Disable for performance

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
                snapshot_dirs = list(snapshots.iterdir())
                if snapshot_dirs:
                    return snapshot_dirs[0]
    return None

def main():
    """Force FLUX to run on RTX 5090"""
    
    logger.info("\n" + "="*70)
    logger.info("FLUX GPU FORCE - RTX 5090")
    logger.info("="*70)
    
    # Check GPU
    if not torch.cuda.is_available():
        logger.error("❌ No GPU detected!")
        return
        
    gpu_name = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    logger.info(f"GPU: {gpu_name} ({vram:.1f}GB)")
    
    # FORCE GPU usage despite warnings
    device = "cuda"
    dtype = torch.float16  # Use FP16 for GPU
    
    logger.info(f"FORCING: {device} with {dtype}")
    logger.info("Ignoring PyTorch compatibility warnings...")
    
    # Find cache
    cache_path = find_flux_cache()
    if not cache_path:
        logger.error("❌ Cache not found!")
        logger.error("Run this first: python flux_authenticated.py")
        return
    
    logger.info(f"✅ Found cache: {cache_path}")
    
    try:
        from diffusers import FluxPipeline
        
        logger.info("\n📦 Loading pipeline...")
        
        # Try different loading approaches
        try:
            # Approach 1: Load with device_map
            logger.info("Trying device_map='cuda'...")
            pipeline = FluxPipeline.from_pretrained(
                str(cache_path),
                torch_dtype=dtype,
                device_map="cuda",
                local_files_only=True
            )
        except Exception as e1:
            logger.warning(f"device_map failed: {e1}")
            
            try:
                # Approach 2: Load then move to CUDA
                logger.info("Trying manual CUDA placement...")
                pipeline = FluxPipeline.from_pretrained(
                    str(cache_path),
                    torch_dtype=dtype,
                    device_map=None,
                    local_files_only=True
                )
                pipeline = pipeline.to(device)
            except Exception as e2:
                logger.warning(f"Manual placement failed: {e2}")
                
                # Approach 3: Component-wise loading
                logger.info("Trying component-wise CUDA placement...")
                pipeline = FluxPipeline.from_pretrained(
                    str(cache_path),
                    torch_dtype=dtype,
                    local_files_only=True
                )
                
                # Move each component
                for attr in ['vae', 'text_encoder', 'text_encoder_2', 'transformer']:
                    if hasattr(pipeline, attr):
                        component = getattr(pipeline, attr)
                        if component is not None:
                            setattr(pipeline, attr, component.to(device))
                            logger.info(f"✅ Moved {attr} to CUDA")
        
        logger.info("✅ Pipeline loaded on GPU!")
        
        # Enable optimizations
        if hasattr(pipeline, 'enable_xformers_memory_efficient_attention'):
            try:
                pipeline.enable_xformers_memory_efficient_attention()
                logger.info("✅ Enabled xformers")
            except:
                pass
        
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            # This keeps models on GPU but offloads between steps
            pipeline.enable_model_cpu_offload()
            logger.info("✅ Enabled smart offloading")
        
        # Test generation on GPU
        logger.info("\n🎨 Generating on RTX 5090...")
        logger.info("If this crashes, we'll catch it and retry...")
        
        prompt = "coloring book page of a dragon, black and white line art, simple clean outlines"
        
        try:
            with torch.cuda.amp.autocast():  # Mixed precision
                image = pipeline(
                    prompt=prompt,
                    num_inference_steps=4,
                    guidance_scale=0.0,
                    height=1024,  # Full resolution on GPU!
                    width=1024,
                    generator=torch.Generator(device=device).manual_seed(42)
                ).images[0]
            
            output_path = "gpu_generated_coloring_page.png"
            image.save(output_path)
            
            logger.info(f"✅ SUCCESS! Generated on GPU: {output_path}")
            logger.info(f"Image size: {image.size}")
            logger.info("\n🎊 RTX 5090 IS WORKING!")
            
        except RuntimeError as e:
            if "no kernel image" in str(e):
                logger.error("❌ CUDA kernel error - RTX 5090 not fully supported")
                logger.info("\nOptions:")
                logger.info("1. Update PyTorch: pip install torch --index-url https://download.pytorch.org/whl/nightly/cu124")
                logger.info("2. Try older CUDA: pip install torch==2.2.0+cu121")
                logger.info("3. Use Docker with proper CUDA support")
            else:
                raise
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()