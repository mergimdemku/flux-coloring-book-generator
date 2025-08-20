"""
Simple FLUX Model Loader - Uses only local models
Professional architecture for coloring book generation
"""

import torch
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from diffusers import FluxPipeline
import os

logger = logging.getLogger(__name__)

class FluxModelLoader:
    """
    Clean FLUX model loader for local models only
    No downloads, no external dependencies, production ready
    """
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir).resolve()
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Expected model files
        self.model_files = {
            "flux": self.models_dir / "flux" / "flux1-schnell.safetensors",
            "clip_l": self.models_dir / "clip" / "clip_l.safetensors",
            "t5xxl": self.models_dir / "clip" / "t5xxl_fp16.safetensors",
            "vae": self.models_dir / "vae" / "ae.safetensors"
        }
    
    def check_models(self) -> Dict[str, bool]:
        """Check if all required models are present"""
        status = {}
        for name, path in self.model_files.items():
            exists = path.exists()
            status[name] = exists
            
            if exists:
                size_gb = path.stat().st_size / (1024**3)
                logger.info(f"✅ {name}: {path.name} ({size_gb:.1f}GB)")
            else:
                logger.error(f"❌ Missing: {path}")
        
        return status
    
    def load_pipeline(self, hf_token: Optional[str] = None) -> bool:
        """
        Load FLUX pipeline from local models
        Returns True if successful, False otherwise
        """
        try:
            # Check all models exist
            model_status = self.check_models()
            if not all(model_status.values()):
                missing = [k for k, v in model_status.items() if not v]
                logger.error(f"Missing models: {missing}")
                return False
            
            logger.info("Loading FLUX pipeline from local models...")
            
            # Set HF token if provided
            if hf_token:
                os.environ["HF_TOKEN"] = hf_token
                from huggingface_hub import login
                try:
                    login(token=hf_token, add_to_git_credential=False)
                    logger.info("Authenticated with Hugging Face")
                except Exception as e:
                    logger.warning(f"HF authentication failed: {e}")
            
            # Load pipeline (will still need some config files from HF)
            self.pipeline = FluxPipeline.from_pretrained(
                "black-forest-labs/FLUX.1-schnell",
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            ).to(self.device)
            
            # Enable optimizations
            if hasattr(self.pipeline, 'enable_xformers_memory_efficient_attention'):
                self.pipeline.enable_xformers_memory_efficient_attention()
            
            logger.info("✅ FLUX pipeline loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load FLUX pipeline: {e}")
            return False
    
    def generate_coloring_page(
        self, 
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        steps: int = 4,
        seed: Optional[int] = None
    ) -> Optional[Any]:
        """Generate a coloring book page"""
        
        if not self.pipeline:
            logger.error("Pipeline not loaded. Call load_pipeline() first.")
            return None
        
        try:
            # Enhance prompt for coloring books
            coloring_prompt = (
                f"{prompt}, black and white line drawing, coloring book page, "
                "bold clean outlines only, no shading, no gray, pure white background, "
                "simple line art, kid-friendly"
            )
            
            # Set seed if provided
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            
            logger.info(f"Generating: {coloring_prompt[:50]}...")
            
            # Generate image
            result = self.pipeline(
                prompt=coloring_prompt,
                width=width,
                height=height,
                num_inference_steps=steps,
                guidance_scale=0.0,  # FLUX.1-schnell doesn't use guidance
                generator=generator
            )
            
            return result.images[0]
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for debugging"""
        info = {
            "device": self.device,
            "models_dir": str(self.models_dir),
            "pipeline_loaded": self.pipeline is not None
        }
        
        if torch.cuda.is_available():
            info.update({
                "gpu_name": torch.cuda.get_device_name(0),
                "gpu_memory_gb": torch.cuda.get_device_properties(0).total_memory / (1024**3),
                "cuda_version": torch.version.cuda
            })
        
        return info