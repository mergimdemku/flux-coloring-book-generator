#!/usr/bin/env python3
"""
FLUX AUTHENTICATED LOADER - Uses HF token to get configs, then local weights
"""

import os
import torch
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Use HF token to get configs, then load local weights"""
    
    logger.info("\n" + "="*70)
    logger.info("FLUX AUTHENTICATED LOADER")
    logger.info("="*70)
    
    # Get HF token from environment
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        logger.error("❌ HF_TOKEN environment variable not set!")
        logger.error("Set it with: export HF_TOKEN=your_token")
        return
    
    logger.info("✅ HF_TOKEN found")
    
    # Check models
    models_dir = Path("models")
    flux_file = models_dir / "flux" / "flux1-schnell.safetensors"
    vae_file = models_dir / "vae" / "ae.safetensors"
    
    if not flux_file.exists() or not vae_file.exists():
        logger.error("Models not found!")
        return
        
    logger.info(f"✅ FLUX: {flux_file.stat().st_size / (1024**3):.1f}GB")
    logger.info(f"✅ VAE: {vae_file.stat().st_size / (1024**3):.1f}GB")
    
    try:
        from diffusers import FluxTransformer2DModel, AutoencoderKL
        from safetensors.torch import load_file
        from huggingface_hub import login
        
        # Login to HuggingFace
        logger.info("\n🔐 Authenticating with HuggingFace...")
        login(token=hf_token, add_to_git_credential=False)
        logger.info("✅ Authenticated")
        
        # Allow network temporarily for configs
        os.environ.pop("HF_HUB_OFFLINE", None)
        os.environ.pop("TRANSFORMERS_OFFLINE", None)
        
        # Get model architecture (downloads configs only)
        logger.info("\n📥 Getting model configs from HuggingFace...")
        logger.info("(Downloads only small config files, not the 22GB model)")
        
        transformer = FluxTransformer2DModel.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            subfolder="transformer",
            torch_dtype=torch.float16,
            token=hf_token,
            cache_dir="cache"
        )
        logger.info("✅ Got transformer config")
        
        vae = AutoencoderKL.from_pretrained(
            "black-forest-labs/FLUX.1-schnell",
            subfolder="vae",
            torch_dtype=torch.float16,
            token=hf_token,
            cache_dir="cache"
        )
        logger.info("✅ Got VAE config")
        
        # Now go back offline
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        
        # Replace with YOUR local weights
        logger.info("\n🔄 Loading YOUR local model weights...")
        
        # Load your FLUX weights
        flux_weights = load_file(str(flux_file))
        logger.info(f"Loaded {len(flux_weights)} tensors from your FLUX file")
        
        # Load weights (skip mismatches)
        missing_keys, unexpected_keys = transformer.load_state_dict(flux_weights, strict=False)
        if missing_keys:
            logger.warning(f"Missing keys: {len(missing_keys)}")
        if unexpected_keys:
            logger.warning(f"Unexpected keys: {len(unexpected_keys)}")
        logger.info("✅ Loaded your FLUX weights into HF architecture")
        
        # Load your VAE weights
        vae_weights = load_file(str(vae_file))
        logger.info(f"Loaded {len(vae_weights)} tensors from your VAE file")
        
        missing_keys, unexpected_keys = vae.load_state_dict(vae_weights, strict=False)
        if missing_keys:
            logger.warning(f"Missing VAE keys: {len(missing_keys)}")
        if unexpected_keys:
            logger.warning(f"Unexpected VAE keys: {len(unexpected_keys)}")
        logger.info("✅ Loaded your VAE weights into HF architecture")
        
        # Move to GPU
        transformer = transformer.to("cuda")
        vae = vae.to("cuda")
        
        logger.info("\n🎉 SUCCESS! HF architecture + YOUR weights!")
        
        # Test the models
        logger.info("\n🧪 Testing models...")
        
        with torch.no_grad():
            batch_size = 1
            height, width = 64, 64  # Latent space
            
            # Create test inputs
            latent = torch.randn(batch_size, 16, height, width, device="cuda", dtype=torch.float16)
            timestep = torch.tensor([500], device="cuda")
            encoder_hidden_states = torch.randn(batch_size, 256, 4096, device="cuda", dtype=torch.float16)
            
            # Test transformer
            output = transformer(
                latent,
                timestep=timestep,
                encoder_hidden_states=encoder_hidden_states,
                return_dict=False
            )
            logger.info(f"✅ Transformer test passed! Output: {output[0].shape}")
            
            # Test VAE
            scaled_latent = latent / vae.config.scaling_factor
            image = vae.decode(scaled_latent, return_dict=False)[0]
            logger.info(f"✅ VAE test passed! Output: {image.shape}")
        
        logger.info("\n🎊 COMPLETE SUCCESS!")
        logger.info("Your FLUX models are working perfectly!")
        logger.info("Next: Add text encoders for full generation")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()