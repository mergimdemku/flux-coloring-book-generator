"""
FLUX image generation system for coloring book pages
"""

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass

# Use Stable Diffusion instead of FLUX (already downloaded)
FluxPipeline = StableDiffusionPipeline

@dataclass
class GenerationConfig:
    """Configuration for image generation"""
    model_name: str = "runwayml/stable-diffusion-v1-5"
    width: int = 512  # SD optimal size
    height: int = 768  # Taller for coloring pages
    num_inference_steps: int = 30  # More steps for quality
    guidance_scale: float = 7.5
    seed: Optional[int] = None
    device: str = "auto"

class FluxGenerator:
    """FLUX-based image generator for coloring book pages"""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.pipeline = None
        self.device = self._determine_device()
        self.logger = logging.getLogger(__name__)
        
        # Initialize pipeline
        self._load_pipeline()
    
    def _determine_device(self) -> str:
        """Determine the best device for generation"""
        if self.config.device != "auto":
            return self.config.device
        
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    def _load_pipeline(self):
        """Load the FLUX pipeline"""
        try:
            self.logger.info(f"Loading FLUX pipeline on {self.device}")
            
            # Load pipeline with optimizations
            self.pipeline = FluxPipeline.from_pretrained(
                self.config.model_name,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
            )
            
            # Move to device
            if self.device != "cuda":  # device_map="auto" handles CUDA
                self.pipeline = self.pipeline.to(self.device)
            
            # Enable memory efficient attention if available
            if hasattr(self.pipeline.unet, 'enable_memory_efficient_attention'):
                self.pipeline.unet.enable_memory_efficient_attention()
            
            # Enable attention slicing for memory efficiency
            self.pipeline.enable_attention_slicing()
            
            self.logger.info("FLUX pipeline loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load FLUX pipeline: {e}")
            raise
    
    def generate_image(self, prompt: str, negative_prompt: str = "", 
                      seed: Optional[int] = None, **kwargs) -> Image.Image:
        """Generate a single image from prompt"""
        
        if self.pipeline is None:
            raise RuntimeError("Pipeline not loaded")
        
        # Use provided seed or config seed
        generation_seed = seed if seed is not None else self.config.seed
        
        # Set up generator for reproducibility
        generator = None
        if generation_seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(generation_seed)
        
        # Generation parameters
        gen_params = {
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'width': self.config.width,
            'height': self.config.height,
            'num_inference_steps': self.config.num_inference_steps,
            'guidance_scale': self.config.guidance_scale,
            'generator': generator,
            **kwargs
        }
        
        try:
            self.logger.info(f"Generating image with prompt: {prompt[:100]}...")
            
            # Generate image
            with torch.autocast(self.device, dtype=torch.float16 if self.device != "cpu" else torch.float32):
                result = self.pipeline(**gen_params)
            
            image = result.images[0]
            
            self.logger.info("Image generation completed")
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to generate image: {e}")
            raise
    
    def generate_batch(self, prompts: List[Dict[str, Any]], 
                      progress_callback=None) -> List[Tuple[Image.Image, Dict]]:
        """Generate multiple images from prompts"""
        
        results = []
        total = len(prompts)
        
        for i, prompt_data in enumerate(prompts):
            try:
                if progress_callback:
                    progress_callback(i, total, f"Generating page {i+1}/{total}")
                
                # Extract prompt and metadata
                prompt = prompt_data['prompt']
                negative_prompt = prompt_data.get('negative_prompt', '')
                scene_info = prompt_data.get('scene_info', {})
                
                # Generate with character consistency seed if available
                seed = self._get_consistency_seed(prompt_data, i)
                
                image = self.generate_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    seed=seed
                )
                
                results.append((image, {
                    'prompt_data': prompt_data,
                    'generation_seed': seed,
                    'page_number': i + 1
                }))
                
            except Exception as e:
                self.logger.error(f"Failed to generate image {i+1}: {e}")
                # Create placeholder image for failed generation
                placeholder = self._create_placeholder_image(f"Generation failed for page {i+1}")
                results.append((placeholder, {
                    'prompt_data': prompt_data,
                    'generation_seed': None,
                    'page_number': i + 1,
                    'error': str(e)
                }))
        
        if progress_callback:
            progress_callback(total, total, "Generation complete")
        
        return results
    
    def _get_consistency_seed(self, prompt_data: Dict, page_index: int) -> Optional[int]:
        """Get seed for character consistency"""
        
        # Use base seed + page offset for variation while maintaining consistency
        base_seed = self.config.seed or 42
        
        # Character scenes use base seed, covers/activities use variations
        page_type = prompt_data.get('page_type', 'scene')
        
        if page_type == 'scene':
            # Main scenes use base seed for character consistency
            return base_seed
        elif page_type in ['cover', 'back_cover']:
            # Covers use base seed + small offset
            return base_seed + 100
        else:  # activity pages
            # Activities use base seed + larger offset
            return base_seed + 1000 + page_index
    
    def _create_placeholder_image(self, message: str) -> Image.Image:
        """Create a placeholder image for failed generations"""
        
        image = Image.new('RGB', (self.config.width, self.config.height), 'white')
        
        # Add simple placeholder text (would need PIL ImageDraw for actual text)
        # For now, return white image
        return image
    
    def optimize_for_coloring(self, image: Image.Image) -> Image.Image:
        """Quick optimization to make image more suitable for coloring"""
        
        # Convert to grayscale first
        if image.mode != 'L':
            image = image.convert('L')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Simple threshold to create strong black/white contrast
        threshold = 128
        img_array = np.where(img_array > threshold, 255, 0)
        
        # Convert back to PIL image
        result = Image.fromarray(img_array.astype(np.uint8), 'L')
        
        # Convert to RGB for consistency
        return result.convert('RGB')
    
    def cleanup(self):
        """Clean up GPU memory"""
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        stats = {}
        
        if torch.cuda.is_available():
            stats['cuda_allocated'] = torch.cuda.memory_allocated() / 1024**3  # GB
            stats['cuda_reserved'] = torch.cuda.memory_reserved() / 1024**3   # GB
            stats['cuda_max_allocated'] = torch.cuda.max_memory_allocated() / 1024**3  # GB
        
        return stats
    
    def test_generation(self) -> bool:
        """Test if the generator is working properly"""
        try:
            test_prompt = "simple line drawing of a circle, black outline on white background"
            test_image = self.generate_image(
                prompt=test_prompt,
                negative_prompt="color, shading",
                seed=42
            )
            
            # Basic validation
            if test_image.size[0] > 0 and test_image.size[1] > 0:
                self.logger.info("Generator test passed")
                return True
            else:
                self.logger.error("Generator test failed: invalid image size")
                return False
                
        except Exception as e:
            self.logger.error(f"Generator test failed: {e}")
            return False

class GenerationManager:
    """High-level manager for the generation process"""
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.generator = None
        self.logger = logging.getLogger(__name__)
    
    def initialize(self) -> bool:
        """Initialize the generation system"""
        try:
            self.generator = FluxGenerator(self.config)
            return self.generator.test_generation()
        except Exception as e:
            self.logger.error(f"Failed to initialize generator: {e}")
            return False
    
    def generate_coloring_book(self, prompts: List[Dict[str, Any]], 
                             output_dir: Path, progress_callback=None) -> List[Path]:
        """Generate complete coloring book and save images"""
        
        if not self.generator:
            raise RuntimeError("Generator not initialized")
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate all images
        results = self.generator.generate_batch(prompts, progress_callback)
        
        # Save images
        saved_paths = []
        
        for i, (image, metadata) in enumerate(results):
            try:
                # Determine filename based on page type
                page_type = metadata['prompt_data'].get('page_type', 'scene')
                page_num = metadata['page_number']
                
                if page_type == 'cover':
                    filename = f"00_cover.png"
                elif page_type == 'back_cover':
                    filename = f"99_back_cover.png"
                elif page_type == 'activity':
                    activity_num = page_num - len([p for p in prompts if p.get('page_type') == 'scene']) - 1
                    filename = f"90_activity_{activity_num:02d}.png"
                else:  # scene
                    scene_num = metadata['prompt_data'].get('scene_info', {}).get('scene_number', page_num)
                    filename = f"{scene_num:02d}_scene.png"
                
                # Save image
                image_path = output_dir / filename
                image.save(image_path, 'PNG', dpi=(300, 300))
                saved_paths.append(image_path)
                
                # Save metadata
                metadata_path = output_dir / f"{filename.stem}_metadata.json"
                import json
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2, default=str)
                
                self.logger.info(f"Saved {filename}")
                
            except Exception as e:
                self.logger.error(f"Failed to save image {i+1}: {e}")
        
        return saved_paths
    
    def cleanup(self):
        """Cleanup resources"""
        if self.generator:
            self.generator.cleanup()