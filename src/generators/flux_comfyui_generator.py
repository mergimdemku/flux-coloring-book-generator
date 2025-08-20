"""
FLUX image generation using ComfyUI-style implementation
Adapted from user's working flux-story-sampler.py
"""

import torch
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
import json
import time

# Import diffusers components
from diffusers import (
    FluxPipeline,
    FluxTransformer2DModel,
    AutoencoderKL,
    FlowMatchEulerDiscreteScheduler
)
from transformers import CLIPTextModel, CLIPTokenizer, T5EncoderModel, T5TokenizerFast

@dataclass
class FluxConfig:
    """Configuration for FLUX generation - RTX 3070 Optimized"""
    model_path: str = "black-forest-labs/FLUX.1-schnell"  # Fast 4-step model
    clip_l_path: str = "openai/clip-vit-large-patch14"
    t5_path: str = "google/t5-v1_1-xxl"
    vae_path: str = "stabilityai/sdxl-vae"
    width: int = 512  # Reduced for RTX 3070
    height: int = 768  # Good for coloring pages
    num_inference_steps: int = 4  # Schnell optimal steps
    guidance_scale: float = 0.0  # Schnell doesn't use guidance
    seed: Optional[int] = None
    device: str = "cuda"
    dtype: torch.dtype = torch.float16
    use_fp8: bool = False  # RTX 3070 doesn't support FP8
    enable_cpu_offload: bool = True  # For 8GB VRAM
    enable_sequential_cpu_offload: bool = True  # More aggressive offloading
    # ComfyUI-style local models support
    local_models_dir: Optional[str] = None  # Path to local .safetensors files
    prefer_local_models: bool = True  # Try local first, fallback to HF

class FluxComfyUIGenerator:
    """FLUX generator with ComfyUI-style implementation for coloring books"""
    
    def __init__(self, config: FluxConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Model components
        self.transformer = None
        self.vae = None
        self.text_encoder = None
        self.text_encoder_2 = None
        self.tokenizer = None
        self.tokenizer_2 = None
        self.scheduler = None
        
        # Load models
        self._load_models()
        
        # Style definitions from ComfyUI script
        self.style_definitions = self._load_style_definitions()
    
    def _load_models(self):
        """Load FLUX models similar to ComfyUI approach"""
        self.logger.info("Loading FLUX models...")
        
        # Try ComfyUI-style local models first if enabled
        if self.config.local_models_dir and self.config.prefer_local_models:
            if self._try_load_local_comfyui_models():
                return
        
        # Fallback to Hugging Face models
        self._load_huggingface_models()
    
    def _try_load_local_comfyui_models(self) -> bool:
        """Try to load local .safetensors models like ComfyUI"""
        try:
            from generators.flux_local_loader import FluxLocalModelLoader
            from pathlib import Path
            
            models_dir = Path(self.config.local_models_dir)
            local_loader = FluxLocalModelLoader(models_dir)
            
            self.logger.info(f"🔍 Checking for local ComfyUI models in {models_dir}")
            
            # Check availability
            availability = local_loader.check_model_availability()
            missing = [k for k, v in availability.items() if not v]
            
            if missing:
                self.logger.warning(f"Missing local models: {missing}")
                self.logger.info("Falling back to Hugging Face models")
                return False
            
            # Load all models
            (self.transformer, self.vae, self.text_encoder, self.tokenizer,
             self.text_encoder_2, self.tokenizer_2, _) = local_loader.load_all_models(
                self.config.device, self.config.dtype
            )
            
            if self.transformer is None:
                return False
            
            # Setup scheduler manually for local models
            self.scheduler = FlowMatchEulerDiscreteScheduler(
                num_train_timesteps=1000,
                shift=1.0,
                use_dynamic_shifting=False
            )
            
            # Apply optimizations
            self._apply_optimizations()
            
            self.logger.info("🎉 Successfully loaded ComfyUI-style local models!")
            self.logger.info(f"   • FLUX: {local_loader.find_model_file('flux_model')}")
            self.logger.info(f"   • CLIP-L: {local_loader.find_model_file('clip_l')}")
            self.logger.info(f"   • T5-XXL: {local_loader.find_model_file('t5xxl')}")
            self.logger.info(f"   • VAE: {local_loader.find_model_file('vae')}")
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Local ComfyUI model loading failed: {e}")
            return False
    
    def _load_huggingface_models(self):
        """Load models from Hugging Face (original implementation)"""
        try:
            self.logger.info("Loading from Hugging Face repositories...")
            
            # Load VAE (ae.safetensors equivalent)
            self.logger.info("Loading VAE...")
            self.vae = AutoencoderKL.from_pretrained(
                self.config.vae_path,
                torch_dtype=self.config.dtype
            ).to(self.config.device)
            
            # Load CLIP-L (clip_l.safetensors equivalent)
            self.logger.info("Loading CLIP-L encoder...")
            self.text_encoder = CLIPTextModel.from_pretrained(
                self.config.clip_l_path,
                torch_dtype=self.config.dtype
            ).to(self.config.device)
            
            self.tokenizer = CLIPTokenizer.from_pretrained(self.config.clip_l_path)
            
            # Load T5-XXL (t5xxl_fp16.safetensors equivalent)
            self.logger.info("Loading T5-XXL encoder...")
            self.text_encoder_2 = T5EncoderModel.from_pretrained(
                self.config.t5_path,
                torch_dtype=self.config.dtype
            ).to(self.config.device)
            
            self.tokenizer_2 = T5TokenizerFast.from_pretrained(self.config.t5_path)
            
            # Load FLUX transformer (flux1-dev.safetensors equivalent)
            self.logger.info("Loading FLUX transformer...")
            self.transformer = FluxTransformer2DModel.from_pretrained(
                self.config.model_path,
                subfolder="transformer",
                torch_dtype=self.config.dtype
            ).to(self.config.device)
            
            # Setup scheduler
            self.scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained(
                self.config.model_path,
                subfolder="scheduler"
            )
            
            # Apply optimizations
            self._apply_optimizations()
            
            self.logger.info("All FLUX models loaded from Hugging Face successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load FLUX models: {e}")
            # Fallback to trying unified pipeline
            self._load_unified_pipeline()
    
    def _load_unified_pipeline(self):
        """Fallback to unified FLUX pipeline if individual loading fails"""
        try:
            self.logger.info("Loading unified FLUX pipeline...")
            
            from diffusers import FluxPipeline
            
            self.pipeline = FluxPipeline.from_pretrained(
                self.config.model_path,
                torch_dtype=self.config.dtype
            ).to(self.config.device)
            
            # Extract components
            self.transformer = self.pipeline.transformer
            self.vae = self.pipeline.vae
            self.text_encoder = self.pipeline.text_encoder
            self.text_encoder_2 = self.pipeline.text_encoder_2
            self.tokenizer = self.pipeline.tokenizer
            self.tokenizer_2 = self.pipeline.tokenizer_2
            self.scheduler = self.pipeline.scheduler
            
            self.logger.info("Unified pipeline loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load unified pipeline: {e}")
            raise
    
    def _apply_optimizations(self):
        """Apply RTX 3070 specific optimizations (8GB VRAM)"""
        
        # Check GPU capability
        if torch.cuda.is_available():
            capability = torch.cuda.get_device_capability()
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            self.logger.info(f"GPU: RTX 3070 - {vram_gb:.1f}GB VRAM, Compute {capability[0]}.{capability[1]}")
        
        # Enable CPU offloading for 8GB VRAM
        if self.config.enable_sequential_cpu_offload:
            try:
                # Sequential CPU offload - most memory efficient
                if hasattr(self, 'pipeline') and self.pipeline:
                    self.pipeline.enable_sequential_cpu_offload()
                    self.logger.info("✅ Sequential CPU offload enabled")
                else:
                    # Manual component offloading
                    self._enable_component_offloading()
            except Exception as e:
                self.logger.warning(f"CPU offload failed: {e}")
        
        # Enable memory efficient attention
        if hasattr(self.transformer, 'enable_memory_efficient_attention'):
            self.transformer.enable_memory_efficient_attention()
            self.logger.info("✅ Memory efficient attention enabled")
        
        # Enable xformers if available
        try:
            import xformers
            if hasattr(self.transformer, 'enable_xformers_memory_efficient_attention'):
                self.transformer.enable_xformers_memory_efficient_attention()
                self.logger.info("✅ xformers memory efficient attention enabled")
        except ImportError:
            self.logger.info("xformers not available - using standard attention")
        
        # Enable attention slicing for lower VRAM
        try:
            if hasattr(self.transformer, 'enable_attention_slicing'):
                self.transformer.enable_attention_slicing("auto")
                self.logger.info("✅ Attention slicing enabled")
        except:
            pass
        
        # Enable VAE slicing for lower VRAM
        try:
            if hasattr(self.vae, 'enable_slicing'):
                self.vae.enable_slicing()
                self.logger.info("✅ VAE slicing enabled")
        except:
            pass
    
    def _enable_component_offloading(self):
        """Enable component-level CPU offloading for RTX 3070"""
        components = [
            ('text_encoder', self.text_encoder),
            ('text_encoder_2', self.text_encoder_2),
            ('transformer', self.transformer),
            ('vae', self.vae)
        ]
        
        for name, component in components:
            if component and hasattr(component, 'to'):
                # Move to CPU after use pattern will be handled in generation
                self.logger.info(f"✅ {name} configured for CPU offloading")
    
    def _load_style_definitions(self) -> Dict[str, Dict[str, str]]:
        """Load style definitions from ComfyUI script"""
        return {
            "Coloring Book": {
                "style": "black and white line drawing, coloring book page, bold clean black outlines only, no shading, no gray",
                "quality": "pure white background, simple line art, thick lines, high contrast, minimal detail",
                "camera": "centered composition, kid-friendly, monochrome outline"
            },
            "Simple": {
                "style": "very simple shapes, minimal details, thick outlines, basic geometric forms",
                "quality": "extra thick black lines, maximum simplicity, toddler-friendly",
                "camera": "centered subject, clear composition, no background clutter"
            },
            "Detailed": {
                "style": "detailed line art, intricate patterns, fine lines, complex scenes",
                "quality": "varied line weights, detailed backgrounds, advanced coloring",
                "camera": "dynamic composition, multiple elements, engaging scenes"
            }
        }
    
    def encode_prompt(
        self,
        prompt: str,
        negative_prompt: str = ""
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode prompt using dual CLIP encoders like ComfyUI"""
        
        # Tokenize for CLIP-L
        clip_inputs = self.tokenizer(
            prompt,
            padding="max_length",
            max_length=77,
            truncation=True,
            return_tensors="pt"
        ).to(self.config.device)
        
        # Tokenize for T5-XXL
        t5_inputs = self.tokenizer_2(
            prompt,
            padding="max_length",
            max_length=512,
            truncation=True,
            return_tensors="pt"
        ).to(self.config.device)
        
        # Encode with CLIP-L
        with torch.no_grad():
            clip_embeds = self.text_encoder(
                clip_inputs.input_ids,
                attention_mask=clip_inputs.attention_mask
            ).last_hidden_state
            
            # Encode with T5-XXL
            t5_embeds = self.text_encoder_2(
                t5_inputs.input_ids,
                attention_mask=t5_inputs.attention_mask
            ).last_hidden_state
        
        # Combine embeddings (FLUX uses concatenation)
        positive_embeds = torch.cat([clip_embeds, t5_embeds], dim=-1)
        
        # Process negative prompt
        if negative_prompt:
            neg_clip_inputs = self.tokenizer(
                negative_prompt,
                padding="max_length",
                max_length=77,
                truncation=True,
                return_tensors="pt"
            ).to(self.config.device)
            
            neg_t5_inputs = self.tokenizer_2(
                negative_prompt,
                padding="max_length",
                max_length=512,
                truncation=True,
                return_tensors="pt"
            ).to(self.config.device)
            
            with torch.no_grad():
                neg_clip_embeds = self.text_encoder(
                    neg_clip_inputs.input_ids,
                    attention_mask=neg_clip_inputs.attention_mask
                ).last_hidden_state
                
                neg_t5_embeds = self.text_encoder_2(
                    neg_t5_inputs.input_ids,
                    attention_mask=neg_t5_inputs.attention_mask
                ).last_hidden_state
            
            negative_embeds = torch.cat([neg_clip_embeds, neg_t5_embeds], dim=-1)
        else:
            negative_embeds = torch.zeros_like(positive_embeds)
        
        return positive_embeds, negative_embeds
    
    def enhance_prompt_for_coloring(
        self,
        prompt: str,
        character_desc: str,
        age_range: str,
        style: str = "Coloring Book"
    ) -> str:
        """Enhance prompt specifically for coloring book generation"""
        
        # Get style definition
        style_def = self.style_definitions.get(style, self.style_definitions["Coloring Book"])
        
        # Age-specific complexity
        age_complexity = {
            '2-4 years': 'very simple shapes, minimal details, extra thick outlines',
            '3-6 years': 'simple clear shapes, moderate details, bold outlines',
            '5-8 years': 'detailed scenes, fine outlines, multiple objects',
            '6-10 years': 'complex scenes, intricate details, varied line weights'
        }
        
        complexity = age_complexity.get(age_range, age_complexity['3-6 years'])
        
        # Build enhanced prompt
        enhanced_parts = [
            prompt,
            character_desc,
            style_def['style'],
            style_def['quality'],
            style_def['camera'],
            complexity,
            "perfect for coloring book",
            "high quality line art"
        ]
        
        return ", ".join(enhanced_parts)
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        seed: Optional[int] = None,
        character_consistency: bool = True
    ) -> Image.Image:
        """Generate single image using FLUX with RTX 3070 optimizations"""
        
        # Set seed for reproducibility
        if seed is None:
            seed = torch.randint(0, 2**32, (1,)).item()
        
        generator = torch.Generator(device=self.config.device).manual_seed(seed)
        
        self.logger.info(f"Generating {self.config.width}x{self.config.height} with seed {seed}")
        
        # RTX 3070 Memory Management
        if torch.cuda.is_available():
            torch.cuda.empty_cache()  # Clear cache before generation
        
        # Move text encoders to GPU only when needed
        if self.config.enable_cpu_offload:
            self.text_encoder = self.text_encoder.to(self.config.device)
            self.text_encoder_2 = self.text_encoder_2.to(self.config.device)
        
        # Encode prompts
        positive_embeds, negative_embeds = self.encode_prompt(prompt, negative_prompt)
        
        # Move text encoders back to CPU to save VRAM
        if self.config.enable_cpu_offload:
            self.text_encoder = self.text_encoder.to('cpu')
            self.text_encoder_2 = self.text_encoder_2.to('cpu')
            torch.cuda.empty_cache()
        
        # Prepare latents
        latent_height = self.config.height // 8
        latent_width = self.config.width // 8
        
        # FLUX uses 16 channels
        latents = torch.randn(
            (1, 16, latent_height, latent_width),
            generator=generator,
            device=self.config.device,
            dtype=self.config.dtype
        )
        
        # Setup scheduler
        self.scheduler.set_timesteps(self.config.num_inference_steps, device=self.config.device)
        timesteps = self.scheduler.timesteps
        
        # Scale initial noise by scheduler
        latents = latents * self.scheduler.init_noise_sigma
        
        # Move transformer to GPU for generation
        if self.config.enable_cpu_offload:
            self.transformer = self.transformer.to(self.config.device)
        
        # Denoising loop with memory management
        with torch.no_grad():
            for i, t in enumerate(timesteps):
                self.logger.info(f"Step {i+1}/{len(timesteps)}")
                
                # FLUX.1-schnell doesn't use CFG (guidance_scale = 0.0)
                latent_model_input = latents
                
                # Predict noise
                noise_pred = self.transformer(
                    latent_model_input,
                    timestep=t,
                    encoder_hidden_states=positive_embeds,
                    return_dict=False
                )[0]
                
                # Scheduler step
                latents = self.scheduler.step(noise_pred, t, latents, generator=generator).prev_sample
                
                # Clear intermediate tensors
                del noise_pred
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
        
        # Move transformer back to CPU
        if self.config.enable_cpu_offload:
            self.transformer = self.transformer.to('cpu')
            torch.cuda.empty_cache()
        
        # Move VAE to GPU for decoding
        if self.config.enable_cpu_offload:
            self.vae = self.vae.to(self.config.device)
        
        # Decode latents
        latents = latents / self.vae.config.scaling_factor
        
        # VAE decode with slicing for memory efficiency
        if hasattr(self.vae, 'enable_slicing'):
            self.vae.enable_slicing()
        
        image = self.vae.decode(latents, return_dict=False)[0]
        
        # Move VAE back to CPU
        if self.config.enable_cpu_offload:
            self.vae = self.vae.to('cpu')
            torch.cuda.empty_cache()
        
        # Post-process
        image = (image / 2 + 0.5).clamp(0, 1)
        image = image.cpu().permute(0, 2, 3, 1).float().numpy()
        image = (image * 255).round().astype(np.uint8)
        
        self.logger.info("✅ Generation completed successfully")
        return Image.fromarray(image[0])
    
    def generate_story_batch(
        self,
        prompts: List[Dict[str, Any]],
        character_card: str,
        age_range: str,
        progress_callback=None
    ) -> List[Tuple[Image.Image, Dict]]:
        """Generate batch of story images with character consistency"""
        
        results = []
        base_seed = self.config.seed or torch.randint(0, 2**32, (1,)).item()
        
        for i, prompt_data in enumerate(prompts):
            if progress_callback:
                progress_callback(i, len(prompts), f"Generating page {i+1}")
            
            try:
                # Enhance prompt for coloring book
                enhanced_prompt = self.enhance_prompt_for_coloring(
                    prompt_data['prompt'],
                    character_card,
                    age_range
                )
                
                # Use consistent seed for character pages
                if prompt_data.get('page_type') == 'scene':
                    seed = base_seed  # Same seed for character consistency
                else:
                    seed = base_seed + 1000 + i  # Different for covers/activities
                
                # Generate image
                image = self.generate_image(
                    enhanced_prompt,
                    prompt_data.get('negative_prompt', ''),
                    seed=seed,
                    character_consistency=True
                )
                
                # Post-process for coloring book
                image = self.optimize_for_coloring(image, age_range)
                
                results.append((image, {
                    'prompt_data': prompt_data,
                    'seed': seed,
                    'page_number': i + 1
                }))
                
            except Exception as e:
                self.logger.error(f"Failed to generate page {i+1}: {e}")
                # Create placeholder
                placeholder = Image.new('RGB', (self.config.width, self.config.height), 'white')
                results.append((placeholder, {
                    'prompt_data': prompt_data,
                    'error': str(e),
                    'page_number': i + 1
                }))
        
        if progress_callback:
            progress_callback(len(prompts), len(prompts), "Generation complete")
        
        return results
    
    def optimize_for_coloring(self, image: Image.Image, age_range: str) -> Image.Image:
        """Optimize image for coloring book output"""
        
        import cv2
        
        # Convert to numpy array
        img = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Apply adaptive threshold for clean lines
        if age_range in ['2-4 years', '3-6 years']:
            # Thicker lines for younger kids
            kernel_size = 5
            block_size = 11
        else:
            # Finer lines for older kids
            kernel_size = 3
            block_size = 9
        
        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size, 2
        )
        
        # Invert (we want black lines on white)
        thresh = 255 - thresh
        
        # Morphological operations to clean up
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        
        # Close small gaps
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        # Remove small noise
        cleaned = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Ensure pure black and white
        _, final = cv2.threshold(cleaned, 127, 255, cv2.THRESH_BINARY)
        
        # Convert back to RGB
        result = cv2.cvtColor(final, cv2.COLOR_GRAY2RGB)
        
        return Image.fromarray(result)
    
    def cleanup(self):
        """Clean up GPU memory"""
        components = [
            self.transformer, self.vae, 
            self.text_encoder, self.text_encoder_2
        ]
        
        for component in components:
            if component is not None:
                del component
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.logger.info("Cleaned up GPU memory")


class FluxServerOptimizer:
    """Optimizer for running FLUX on RTX 3070 server"""
    
    @staticmethod
    def get_optimal_config() -> FluxConfig:
        """Get optimal configuration for RTX 3070 (8GB VRAM)"""
        
        config = FluxConfig(
            model_path="black-forest-labs/FLUX.1-schnell",  # Only schnell fits in 8GB
            width=512,  # Reduced resolution for VRAM constraints
            height=768,  # Good aspect ratio for coloring books
            num_inference_steps=4,  # Schnell optimal (fast)
            guidance_scale=0.0,  # Schnell doesn't use CFG
            device="cuda",
            dtype=torch.float16,  # Essential for VRAM efficiency
            use_fp8=False,  # RTX 3070 doesn't support FP8
            enable_cpu_offload=True,  # Essential for 8GB VRAM
            enable_sequential_cpu_offload=True  # Most aggressive offloading
        )
        
        # Check available VRAM and adjust
        if torch.cuda.is_available():
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            
            if vram_gb < 8:  # Less than RTX 3070
                # Further reduce resolution
                config.width = 384
                config.height = 512
                print(f"⚠️  Low VRAM detected ({vram_gb:.1f}GB), using {config.width}x{config.height}")
            elif vram_gb >= 10:  # RTX 3080 or better
                # Can use slightly higher resolution
                config.width = 768
                config.height = 768
                print(f"✅ Higher VRAM detected ({vram_gb:.1f}GB), using {config.width}x{config.height}")
            else:  # RTX 3070 (8GB)
                print(f"✅ RTX 3070 detected ({vram_gb:.1f}GB), optimized for 8GB VRAM")
        
        return config
    
    @staticmethod
    def benchmark_generation(generator: FluxComfyUIGenerator) -> Dict[str, float]:
        """Benchmark generation performance"""
        
        import time
        
        results = {}
        
        # Warmup
        generator.generate_image("test", seed=42)
        
        # Single image benchmark
        start = time.time()
        generator.generate_image(
            "simple coloring book page of a dog",
            negative_prompt="color, shading",
            seed=42
        )
        results['single_image_time'] = time.time() - start
        
        # Batch benchmark
        test_prompts = [
            {"prompt": f"coloring page scene {i}", "negative_prompt": "color"}
            for i in range(10)
        ]
        
        start = time.time()
        generator.generate_story_batch(
            test_prompts,
            "test character",
            "3-6 years"
        )
        results['batch_10_time'] = time.time() - start
        results['avg_image_time'] = results['batch_10_time'] / 10
        
        # Memory usage
        if torch.cuda.is_available():
            results['vram_used_gb'] = torch.cuda.max_memory_allocated() / (1024**3)
            torch.cuda.reset_peak_memory_stats()
        
        return results