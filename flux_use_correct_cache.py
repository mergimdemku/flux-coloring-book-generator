#!/usr/bin/env python3
"""
FLUX - Use the correct complete cache with all model files
"""

import os
import torch
from pathlib import Path
import logging
import warnings

warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Use the complete FLUX cache"""
    
    logger.info("\n" + "="*70)
    logger.info("FLUX RTX 5090 - Using Complete Cache")
    logger.info("="*70)
    
    # GPU info
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        logger.info(f"GPU: {gpu_name} ({vram:.1f}GB)")
    
    device = "cuda"
    dtype = torch.float16
    
    # Use the COMPLETE cache with actual model files
    cache_path = Path("cache/models--black-forest-labs--FLUX.1-schnell/snapshots/741f7c3ce8b383c54771c7003378a50191e9efe9")
    
    if not cache_path.exists():
        logger.error(f"❌ Cache not found at: {cache_path}")
        return
    
    logger.info(f"✅ Using complete cache: {cache_path}")
    
    # Verify model files exist
    transformer_files = list((cache_path / "transformer").glob("*.safetensors"))
    vae_files = list((cache_path / "vae").glob("*.safetensors"))
    
    logger.info(f"Found {len(transformer_files)} transformer files")
    logger.info(f"Found {len(vae_files)} VAE files")
    
    try:
        from diffusers import FluxPipeline
        
        logger.info("\n🚀 Loading FLUX from complete cache...")
        
        # Load from the complete cache
        pipeline = FluxPipeline.from_pretrained(
            str(cache_path),
            torch_dtype=dtype,
            local_files_only=True
        )
        
        logger.info("✅ Pipeline loaded successfully!")
        
        # Move to GPU
        logger.info(f"Moving to GPU...")
        pipeline = pipeline.to(device)
        logger.info(f"✅ On RTX 5090!")
        
        # Enable optimizations for RTX 5090
        if hasattr(pipeline, 'enable_model_cpu_offload'):
            pipeline.enable_model_cpu_offload()
            logger.info("✅ Enabled smart GPU/CPU offloading")
        
        # Test generation
        logger.info("\n🎨 Generating coloring book page on RTX 5090...")
        
        prompt = "coloring book page of a cute dragon, black and white line art, simple outlines, no shading"
        
        # Try generation with error handling
        for resolution in [1024, 768, 512]:
            try:
                logger.info(f"Trying {resolution}x{resolution}...")
                
                with torch.cuda.amp.autocast(dtype=dtype):
                    image = pipeline(
                        prompt=prompt,
                        num_inference_steps=4,  # schnell optimal
                        guidance_scale=0.0,     # schnell doesn't use guidance
                        height=resolution,
                        width=resolution,
                        generator=torch.Generator(device=device).manual_seed(42)
                    ).images[0]
                
                output_path = f"flux_rtx5090_{resolution}.png"
                image.save(output_path)
                
                logger.info(f"✅ SUCCESS! Generated {resolution}x{resolution}: {output_path}")
                logger.info("\n🎊 RTX 5090 WORKS WITH FLUX!")
                logger.info(f"Your coloring book page is ready: {output_path}")
                break
                
            except RuntimeError as e:
                if "out of memory" in str(e).lower():
                    logger.warning(f"Out of memory at {resolution}x{resolution}, trying smaller...")
                    torch.cuda.empty_cache()
                    continue
                elif "no kernel image" in str(e):
                    logger.error(f"CUDA kernel error at {resolution}x{resolution}")
                    logger.info("PyTorch doesn't fully support sm_120 yet")
                    logger.info("Try: pip install torch --pre --index-url https://download.pytorch.org/whl/nightly/cu124")
                    break
                else:
                    raise
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()