#!/usr/bin/env python3
"""
Manual FLUX Pipeline Building - Load each component separately
Based on diffusers documentation approach
"""

import os
# Force offline mode for safety
os.environ["HF_HUB_OFFLINE"] = "1"

import torch
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Build FLUX pipeline manually from components"""
    
    logger.info("\n" + "="*70)
    logger.info("MANUAL FLUX PIPELINE BUILDING")
    logger.info("="*70)
    
    # Check models
    models_dir = Path("models")
    flux_file = models_dir / "flux" / "flux1-schnell.safetensors"
    vae_file = models_dir / "vae" / "ae.safetensors"
    clip_file = models_dir / "clip" / "clip_l.safetensors"
    t5_file = models_dir / "clip" / "t5xxl_fp16.safetensors"
    
    logger.info("Checking model files...")
    for name, path in [("FLUX", flux_file), ("VAE", vae_file), ("CLIP", clip_file), ("T5", t5_file)]:
        if path.exists():
            size = path.stat().st_size / (1024**3)
            logger.info(f"✅ {name}: {size:.1f}GB")
        else:
            logger.error(f"❌ Missing: {name} at {path}")
            return
    
    try:
        logger.info("\n🔧 Loading components...")
        
        from diffusers import FluxTransformer2DModel, AutoencoderKL, FluxPipeline
        from diffusers import FlowMatchEulerDiscreteScheduler
        
        # Load transformer from safetensors
        logger.info("Loading FLUX transformer...")
        transformer = FluxTransformer2DModel.from_single_file(
            str(flux_file),
            torch_dtype=torch.float16
        )
        
        # Load VAE from safetensors
        logger.info("Loading VAE...")
        vae = AutoencoderKL.from_single_file(
            str(vae_file),
            torch_dtype=torch.float16
        )
        
        # Create scheduler
        scheduler = FlowMatchEulerDiscreteScheduler()
        
        logger.info("✅ Core components loaded!")
        
        # Now try to load text encoders
        # Method 1: Try loading from local safetensors (probably won't work directly)
        logger.info("\nTrying to load text encoders...")
        
        try:
            from transformers import CLIPTextModel, CLIPTokenizer
            from transformers import T5EncoderModel, T5TokenizerFast
            
            # These will likely fail without proper configs
            # But let's see what happens
            logger.info("Attempting text encoder loading...")
            
            # CLIP
            text_encoder = CLIPTextModel.from_pretrained(
                "openai/clip-vit-large-patch14",
                torch_dtype=torch.float16,
                local_files_only=True
            )
            tokenizer = CLIPTokenizer.from_pretrained(
                "openai/clip-vit-large-patch14",
                local_files_only=True
            )
            
            # T5
            text_encoder_2 = T5EncoderModel.from_pretrained(
                "google/t5-v1_1-xxl",
                torch_dtype=torch.float16,
                local_files_only=True
            )
            tokenizer_2 = T5TokenizerFast.from_pretrained(
                "google/t5-v1_1-xxl",
                local_files_only=True
            )
            
            logger.info("✅ Text encoders loaded!")
            
            # Build complete pipeline
            pipeline = FluxPipeline(
                transformer=transformer,
                vae=vae,
                text_encoder=text_encoder,
                text_encoder_2=text_encoder_2,
                tokenizer=tokenizer,
                tokenizer_2=tokenizer_2,
                scheduler=scheduler
            )
            
            logger.info("🎉 COMPLETE PIPELINE BUILT!")
            logger.info("Ready for generation!")
            
            # Test generation
            pipeline.to("cuda")
            
            logger.info("\n🎨 Testing generation...")
            with torch.no_grad():
                image = pipeline(
                    prompt="coloring book page of a dragon, black and white line art",
                    num_inference_steps=4,  # schnell optimal
                    guidance_scale=0.0,     # schnell doesn't use guidance
                    height=512,
                    width=512
                ).images[0]
            
            image.save("test_generation.png")
            logger.info("✅ Generated test_generation.png!")
            
        except Exception as e:
            logger.warning(f"Text encoder loading failed: {e}")
            logger.info("This is expected - need cached text encoders")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")

if __name__ == "__main__":
    main()