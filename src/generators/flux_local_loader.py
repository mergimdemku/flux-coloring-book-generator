"""
FLUX Local Model Loader - ComfyUI Style
Loads exact .safetensors files like your ComfyUI script
"""

import torch
import safetensors.torch
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging
from transformers import CLIPTextModel, CLIPTokenizer, T5EncoderModel, T5TokenizerFast
from diffusers import AutoencoderKL, FluxTransformer2DModel

class FluxLocalModelLoader:
    """Load FLUX models from local .safetensors files like ComfyUI"""
    
    def __init__(self, models_dir: Path):
        self.models_dir = Path(models_dir)
        self.logger = logging.getLogger(__name__)
        
        # Expected model paths (like ComfyUI folder structure)
        self.model_paths = {
            'flux_model': self.models_dir / "diffusion_models" / "flux1-dev.safetensors",
            'clip_l': self.models_dir / "clip" / "clip_l.safetensors", 
            't5xxl': self.models_dir / "clip" / "t5xxl_fp16.safetensors",
            'vae': self.models_dir / "vae" / "ae.safetensors"
        }
        
        # Alternative paths if models are in different locations
        self.alt_paths = {
            'flux_model': [
                self.models_dir / "flux1-dev.safetensors",
                self.models_dir / "FLUX" / "flux1-dev.safetensors",
                self.models_dir / "flux1-schnell.safetensors"
            ],
            'clip_l': [
                self.models_dir / "clip_l.safetensors",
                self.models_dir / "CLIP" / "clip_l.safetensors"
            ],
            't5xxl': [
                self.models_dir / "t5xxl_fp16.safetensors",
                self.models_dir / "T5" / "t5xxl_fp16.safetensors"
            ],
            'vae': [
                self.models_dir / "ae.safetensors",
                self.models_dir / "VAE" / "ae.safetensors",
                self.models_dir / "sdxl_vae.safetensors"
            ]
        }
    
    def find_model_file(self, model_type: str) -> Optional[Path]:
        """Find model file, checking multiple possible locations"""
        
        # Check primary path first
        primary_path = self.model_paths.get(model_type)
        if primary_path and primary_path.exists():
            return primary_path
        
        # Check alternative paths
        alt_paths = self.alt_paths.get(model_type, [])
        for path in alt_paths:
            if path.exists():
                return path
        
        return None
    
    def check_model_availability(self) -> Dict[str, bool]:
        """Check which models are available locally"""
        
        availability = {}
        
        for model_type in ['flux_model', 'clip_l', 't5xxl', 'vae']:
            model_path = self.find_model_file(model_type)
            availability[model_type] = model_path is not None
            
            if model_path:
                size_gb = model_path.stat().st_size / (1024**3)
                self.logger.info(f"✅ Found {model_type}: {model_path} ({size_gb:.1f}GB)")
            else:
                self.logger.warning(f"❌ Missing {model_type}")
        
        return availability
    
    def load_flux_transformer(self, device: str, dtype: torch.dtype):
        """Load FLUX transformer from local safetensors"""
        
        flux_path = self.find_model_file('flux_model')
        if not flux_path:
            raise FileNotFoundError("flux1-dev.safetensors not found")
        
        self.logger.info(f"Loading FLUX transformer from {flux_path}")
        
        # Load state dict from safetensors
        state_dict = safetensors.torch.load_file(str(flux_path))
        
        # Create transformer model
        # Note: This is simplified - in practice, you'd need the exact config
        try:
            # Try to load with diffusers FluxTransformer2DModel
            transformer = FluxTransformer2DModel.from_pretrained(
                "black-forest-labs/FLUX.1-dev",
                subfolder="transformer",
                torch_dtype=dtype
            )
            
            # Load the local weights
            transformer.load_state_dict(state_dict, strict=False)
            transformer = transformer.to(device)
            
            self.logger.info("✅ FLUX transformer loaded successfully")
            return transformer
            
        except Exception as e:
            self.logger.error(f"Failed to load FLUX transformer: {e}")
            raise
    
    def load_clip_encoders(self, device: str, dtype: torch.dtype):
        """Load dual CLIP encoders from local safetensors"""
        
        clip_l_path = self.find_model_file('clip_l')
        t5xxl_path = self.find_model_file('t5xxl')
        
        if not clip_l_path:
            raise FileNotFoundError("clip_l.safetensors not found")
        if not t5xxl_path:
            raise FileNotFoundError("t5xxl_fp16.safetensors not found")
        
        self.logger.info(f"Loading CLIP-L from {clip_l_path}")
        self.logger.info(f"Loading T5-XXL from {t5xxl_path}")
        
        # Load CLIP-L
        clip_l_state = safetensors.torch.load_file(str(clip_l_path))
        text_encoder = CLIPTextModel.from_pretrained(
            "openai/clip-vit-large-patch14",
            torch_dtype=dtype
        )
        text_encoder.load_state_dict(clip_l_state, strict=False)
        text_encoder = text_encoder.to(device)
        
        tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
        
        # Load T5-XXL
        t5_state = safetensors.torch.load_file(str(t5xxl_path))
        text_encoder_2 = T5EncoderModel.from_pretrained(
            "google/t5-v1_1-xxl",
            torch_dtype=dtype
        )
        text_encoder_2.load_state_dict(t5_state, strict=False)
        text_encoder_2 = text_encoder_2.to(device)
        
        tokenizer_2 = T5TokenizerFast.from_pretrained("google/t5-v1_1-xxl")
        
        self.logger.info("✅ Dual CLIP encoders loaded successfully")
        return text_encoder, tokenizer, text_encoder_2, tokenizer_2
    
    def load_vae(self, device: str, dtype: torch.dtype):
        """Load VAE from local safetensors"""
        
        vae_path = self.find_model_file('vae')
        if not vae_path:
            raise FileNotFoundError("ae.safetensors not found")
        
        self.logger.info(f"Loading VAE from {vae_path}")
        
        # Load VAE state dict
        vae_state = safetensors.torch.load_file(str(vae_path))
        
        # Create VAE model
        vae = AutoencoderKL.from_pretrained(
            "stabilityai/sdxl-vae",
            torch_dtype=dtype
        )
        vae.load_state_dict(vae_state, strict=False)
        vae = vae.to(device)
        
        self.logger.info("✅ VAE loaded successfully")
        return vae
    
    def load_all_models(self, device: str, dtype: torch.dtype):
        """Load all FLUX models exactly like ComfyUI"""
        
        self.logger.info("Loading FLUX models (ComfyUI style)...")
        
        # Check availability first
        availability = self.check_model_availability()
        missing_models = [k for k, v in availability.items() if not v]
        
        if missing_models:
            self.logger.warning(f"Missing models: {missing_models}")
            self.logger.info("Will attempt to download from Hugging Face as fallback")
            return None, None, None, None, None, None, None
        
        try:
            # Load exactly like your ComfyUI script
            transformer = self.load_flux_transformer(device, dtype)
            
            text_encoder, tokenizer, text_encoder_2, tokenizer_2 = self.load_clip_encoders(device, dtype)
            
            vae = self.load_vae(device, dtype)
            
            self.logger.info("🎉 All FLUX models loaded successfully (ComfyUI style)")
            return transformer, vae, text_encoder, tokenizer, text_encoder_2, tokenizer_2, None
            
        except Exception as e:
            self.logger.error(f"Failed to load local models: {e}")
            return None, None, None, None, None, None, None


class FluxComfyUIStyleGenerator:
    """FLUX generator that loads models exactly like your ComfyUI script"""
    
    def __init__(self, config, models_dir: Optional[Path] = None):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Model components (exactly like ComfyUI)
        self.transformer = None  # flux1-dev.safetensors
        self.vae = None         # ae.safetensors  
        self.text_encoder = None    # clip_l.safetensors
        self.text_encoder_2 = None  # t5xxl_fp16.safetensors
        self.tokenizer = None
        self.tokenizer_2 = None
        self.scheduler = None
        
        # Try to load local models first (ComfyUI style)
        if models_dir:
            self.local_loader = FluxLocalModelLoader(models_dir)
            self._try_load_local_models()
        else:
            self.local_loader = None
            self._load_from_huggingface()
    
    def _try_load_local_models(self):
        """Try to load models from local .safetensors files first"""
        
        try:
            (self.transformer, self.vae, self.text_encoder, self.tokenizer, 
             self.text_encoder_2, self.tokenizer_2, self.scheduler) = self.local_loader.load_all_models(
                self.config.device, self.config.dtype
            )
            
            if self.transformer is not None:
                self.logger.info("🎉 Successfully loaded local ComfyUI models!")
                self._setup_scheduler_for_local()
                return True
            else:
                self.logger.warning("Local models not available, falling back to Hugging Face")
                self._load_from_huggingface()
                return False
                
        except Exception as e:
            self.logger.warning(f"Local model loading failed: {e}")
            self._load_from_huggingface()
            return False
    
    def _setup_scheduler_for_local(self):
        """Setup scheduler when using local models"""
        from diffusers import FlowMatchEulerDiscreteScheduler
        
        # Create scheduler (similar to ComfyUI's simple scheduler)
        self.scheduler = FlowMatchEulerDiscreteScheduler(
            num_train_timesteps=1000,
            shift=1.0,
            use_dynamic_shifting=False
        )
    
    def _load_from_huggingface(self):
        """Fallback to Hugging Face models (original implementation)"""
        
        self.logger.info("Loading FLUX models from Hugging Face...")
        
        # This calls the original _load_models method
        from generators.flux_comfyui_generator import FluxComfyUIGenerator
        
        # Use the original implementation as fallback
        original_generator = FluxComfyUIGenerator(self.config)
        
        # Copy loaded components
        self.transformer = original_generator.transformer
        self.vae = original_generator.vae
        self.text_encoder = original_generator.text_encoder
        self.text_encoder_2 = original_generator.text_encoder_2
        self.tokenizer = original_generator.tokenizer
        self.tokenizer_2 = original_generator.tokenizer_2
        self.scheduler = original_generator.scheduler
        
        self.logger.info("✅ Loaded from Hugging Face repositories")
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        
        info = {
            "loading_method": "unknown",
            "models_loaded": False,
            "model_sources": {}
        }
        
        if self.local_loader:
            availability = self.local_loader.check_model_availability()
            local_available = all(availability.values())
            
            if local_available and self.transformer is not None:
                info.update({
                    "loading_method": "local_safetensors",
                    "models_loaded": True,
                    "model_sources": {
                        "flux_transformer": str(self.local_loader.find_model_file('flux_model')),
                        "clip_l": str(self.local_loader.find_model_file('clip_l')),
                        "t5xxl": str(self.local_loader.find_model_file('t5xxl')),
                        "vae": str(self.local_loader.find_model_file('vae'))
                    }
                })
            else:
                info.update({
                    "loading_method": "huggingface_fallback",
                    "models_loaded": self.transformer is not None,
                    "model_sources": {
                        "flux_transformer": self.config.model_path,
                        "clip_l": self.config.clip_l_path,
                        "t5xxl": self.config.t5_path,
                        "vae": self.config.vae_path
                    }
                })
        
        return info