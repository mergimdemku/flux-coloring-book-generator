"""
Optimized FLUX Generator with CLIP Token Awareness
Respects 77 token limit for maximum quality
"""

import torch
from diffusers import FluxPipeline
import logging
from typing import Optional, Dict
import os
from PIL import Image
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OptimizedFluxGenerator:
    """FLUX generator optimized for CLIP's 77 token limit"""
    
    def __init__(self, model_path: str = "black-forest-labs/FLUX.1-schnell"):
        # Import and apply model configuration
        from model_config import MODEL_CONFIG, CACHE_DIR
        
        self.model_path = model_path
        self.cache_dir = str(CACHE_DIR)
        self.model_config = MODEL_CONFIG
        self.pipe = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Using model cache at: {self.cache_dir}")
        logger.info("Will use existing cached models - no download needed")
        
        # CRITICAL: Prioritized prompt elements (most important first)
        self.prompt_priorities = {
            'coloring_page': {
                'essential': [  # First 30-35 tokens - THESE WILL BE READ
                    'black white line art',
                    'coloring book page',
                    'no text no words',
                    'thick outlines only',
                    'white background'
                ],
                'character': [],  # 15-20 tokens for character description
                'style': [  # 10-15 tokens
                    'simple', 'clear', 'bold lines'
                ],
                'negative_critical': [  # For negative prompt
                    'color', 'gray', 'shading', 'text', 'words', 
                    'gradient', 'photo', 'realistic'
                ]
            },
            'cover': {
                'essential': [  # First 30-35 tokens
                    'colorful illustration',
                    'book cover',
                    'no text no title',
                    'full page art',
                    'vibrant colors'
                ],
                'character': [],  # 15-20 tokens for character
                'style': [  # 10-15 tokens
                    'cartoon', 'child-friendly', 'happy'
                ],
                'negative_critical': [
                    'text', 'words', 'title', 'letters',
                    'dark', 'scary', 'violent'
                ]
            }
        }
    
    def count_tokens(self, text: str) -> int:
        """Approximate token count (CLIP uses ~0.75 words per token)"""
        words = text.split()
        return int(len(words) * 1.33)  # Conservative estimate
    
    def build_optimized_prompt(self, 
                              character_desc: str,
                              scene_desc: str,
                              prompt_type: str = 'coloring_page',
                              style: str = 'simple') -> str:
        """
        Build prompt that fits within CLIP's 77 token limit
        Priority order: Essential > Character > Scene > Style
        """
        
        priorities = self.prompt_priorities[prompt_type]
        
        # Start with essentials (30-35 tokens)
        prompt_parts = priorities['essential'].copy()
        
        # Add character description (keep it SHORT - max 15 tokens)
        if character_desc:
            # Extract only the most important character elements
            char_parts = character_desc.split(',')[0].split(';')[0]
            char_words = char_parts.split()[:10]  # Max 10 words for character
            prompt_parts.append(' '.join(char_words))
        
        # Add scene action (keep it SHORT - max 10 tokens)  
        if scene_desc:
            # Extract only the action, not the background
            scene_parts = scene_desc.split(';')[0].split(',')[0]
            scene_words = scene_parts.split()[:7]  # Max 7 words for action
            prompt_parts.append(' '.join(scene_words))
        
        # Add style if space remains
        current_prompt = ', '.join(prompt_parts)
        current_tokens = self.count_tokens(current_prompt)
        
        if current_tokens < 65:  # Leave buffer for style
            prompt_parts.extend(priorities['style'])
        
        # Build final prompt
        final_prompt = ', '.join(prompt_parts)
        
        # Verify token count
        token_count = self.count_tokens(final_prompt)
        if token_count > 77:
            # Trim if needed
            words = final_prompt.split()[:57]  # ~77 tokens
            final_prompt = ' '.join(words)
            logger.warning(f"Prompt trimmed to fit 77 token limit")
        
        logger.info(f"Optimized prompt ({token_count} tokens): {final_prompt}")
        return final_prompt
    
    def build_optimized_negative(self, prompt_type: str = 'coloring_page') -> str:
        """Build negative prompt within token limits"""
        priorities = self.prompt_priorities[prompt_type]
        negative_parts = priorities['negative_critical']
        
        # Keep negative prompt short and focused
        negative_prompt = ', '.join(negative_parts[:10])  # Max 10 concepts
        
        token_count = self.count_tokens(negative_prompt)
        logger.info(f"Negative prompt ({token_count} tokens): {negative_prompt}")
        return negative_prompt
    
    def load_model(self):
        """Load FLUX model from cache"""
        if self.pipe is None:
            logger.info("Loading FLUX model from cache...")
            
            try:
                # Use your cached model - no download
                self.pipe = FluxPipeline.from_pretrained(
                    self.model_path,
                    cache_dir=self.cache_dir,
                    local_files_only=True,  # Don't download, use cached only
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
                self.pipe = self.pipe.to(self.device)
                logger.info(f"✅ Model loaded from cache on {self.device}")
                logger.info("✅ No download needed - using existing files")
                return True
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                return False
        return True  # Already loaded
    
    def generate_image(self,
                      character: str,
                      scene: str,
                      prompt_type: str = 'coloring_page',
                      style: str = 'simple',
                      seed: Optional[int] = None,
                      width: int = 592,
                      height: int = 840) -> Image.Image:
        """Generate image with optimized prompts"""
        
        self.load_model()
        
        # Build optimized prompts
        prompt = self.build_optimized_prompt(character, scene, prompt_type, style)
        negative_prompt = self.build_optimized_negative(prompt_type)
        
        # Set seed for consistency
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None
        
        # Generate with FLUX
        logger.info(f"Generating {prompt_type}...")
        
        num_steps = 8 if prompt_type == 'cover' else 4
        
        image = self.pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_steps,
            guidance_scale=0.0,  # FLUX.1-schnell uses 0.0
            width=width,
            height=height,
            generator=generator
        ).images[0]
        
        # Post-process for coloring pages
        if prompt_type == 'coloring_page':
            image = self.process_to_line_art(image)
        
        return image
    
    def process_to_line_art(self, image: Image.Image) -> Image.Image:
        """Simple, effective line art conversion"""
        # Convert to grayscale
        gray = image.convert('L')
        
        # Convert to numpy
        img_array = np.array(gray)
        
        # Simple threshold - works better than complex processing
        threshold = 200  # Higher threshold for cleaner lines
        binary = np.where(img_array < threshold, 0, 255).astype(np.uint8)
        
        # Convert back to PIL
        return Image.fromarray(binary, mode='L').convert('RGB')
    
    def generate_perfect_cover(self, character_desc: str = "", scene_desc: str = "", seed: Optional[int] = None, **kwargs) -> Image.Image:
        """Generate perfect cover - wrapper for compatibility"""
        logger.info("Generating cover with optimized prompts...")
        
        # Extract character and scene from prompt_data if provided
        prompt_data = kwargs.get('prompt_data', {})
        if prompt_data:
            character_desc = prompt_data.get('character', character_desc or "friendly character")
            scene_desc = prompt_data.get('scene', scene_desc or "happy scene")
        else:
            # If no prompt_data and no character/scene provided, use defaults
            character_desc = character_desc or "friendly character"
            scene_desc = scene_desc or "happy scene"
        
        return self.generate_image(
            character=character_desc,
            scene=scene_desc,
            prompt_type='cover',
            seed=seed
        )
    
    def generate_ultra_clean_coloring_page(self, character_desc: str = "", scene_desc: str = "", seed: Optional[int] = None, **kwargs) -> Image.Image:
        """Generate ultra clean coloring page - wrapper for compatibility"""
        logger.info("Generating coloring page with optimized prompts...")
        
        # Extract character and scene from prompt_data if provided
        prompt_data = kwargs.get('prompt_data', {})
        if prompt_data:
            character_desc = prompt_data.get('character', character_desc or "friendly character")
            scene_desc = prompt_data.get('scene', scene_desc or "simple scene")
        else:
            # If no prompt_data and no character/scene provided, use defaults
            character_desc = character_desc or "friendly character"
            scene_desc = scene_desc or "simple scene"
            
        return self.generate_image(
            character=character_desc,
            scene=scene_desc,
            prompt_type='coloring_page',
            seed=seed
        )


def demonstrate_optimization():
    """Show the difference between old and new approaches"""
    
    # Example scene from your story
    character = "friendly teacher with glasses and books"
    scene = "waking up; sunrise circle behind; small houses visible through window"
    
    print("=" * 70)
    print("PROMPT OPTIMIZATION DEMONSTRATION")
    print("=" * 70)
    
    # Old approach (what you were doing)
    old_prompt = f"cute {character} {scene}, ultra-detailed illustration, 8k quality, trending on artstation, masterpiece artwork, professional quality, highly detailed, intricate details, perfect composition, anatomically correct five fingers per hand, correct human anatomy, perfect body structure, normal human anatomy, realistic proportions, correct number of limbs, two arms two legs, five fingers per hand, symmetrical body, proper animal anatomy, realistic animal form, clear gender presentation, consistent character design, accurate species traits, black and white line art only, pure white background, NO TEXT AT ALL, NO WORDS, NO LETTERS, NO NUMBERS, NO LOGOS, wordless image, text-free illustration, no page numbers, no shading, no gray areas, thick black outlines, perfect for coloring, ultra high contrast, clean coloring book page"
    
    old_tokens = len(old_prompt.split()) * 1.33
    print(f"\nOLD APPROACH:")
    print(f"Length: {len(old_prompt)} characters")
    print(f"Tokens: ~{int(old_tokens)} (CLIP limit: 77)")
    print(f"First 77 tokens get: {' '.join(old_prompt.split()[:57])}")
    print(f"\nIGNORED: Everything after 'perfect composition'")
    print("Result: No text prevention, no coloring specs, no anatomy fixes!")
    
    # New optimized approach
    generator = OptimizedFluxGenerator()
    new_prompt = generator.build_optimized_prompt(character, scene, 'coloring_page')
    new_tokens = generator.count_tokens(new_prompt)
    
    print(f"\nNEW OPTIMIZED APPROACH:")
    print(f"Length: {len(new_prompt)} characters")
    print(f"Tokens: ~{new_tokens} (within CLIP limit!)")
    print(f"Full prompt: {new_prompt}")
    print("\nResult: ALL critical elements are read by CLIP!")
    
    print("\n" + "=" * 70)
    print("KEY IMPROVEMENTS:")
    print("1. 'no text no words' - ACTUALLY GETS READ NOW")
    print("2. 'black white line art' - IN THE FIRST 30 TOKENS")
    print("3. 'coloring book page' - CLEARLY SPECIFIED EARLY")
    print("4. Character still described but concisely")
    print("5. Negative prompt also optimized for clarity")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_optimization()
    
    print("\n\nTo use this in your pipeline:")
    print("1. Replace clean_line_flux_generator.py with this optimized version")
    print("2. Update automated_monitor_pipeline.py to use OptimizedFluxGenerator")
    print("3. Run with much better quality results!")