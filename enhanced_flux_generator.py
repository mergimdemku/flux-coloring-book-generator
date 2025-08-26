#!/usr/bin/env python3
"""
Enhanced FLUX Generator with Consistent Characters and Proper Prompt Following
Addresses prompt following issues and maintains character consistency across stories
"""

import torch
import gc
import os
import cv2
import numpy as np
from pathlib import Path
import logging
import json
import time
from PIL import Image, ImageEnhance, ImageFilter
from typing import Dict, List, Any, Optional
from local_flux_rtx3070 import FluxRTX3070

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedFluxGenerator:
    """Enhanced FLUX generator with character consistency and better prompt following"""
    
    def __init__(self):
        # Initialize base FLUX generator
        self.base_generator = FluxRTX3070()
        
        # Character consistency settings
        self.character_seeds = {}  # Store seeds for consistent characters
        self.character_descriptions = {}  # Store character visual descriptions
        
        # Enhanced prompt building
        self.style_enhancers = {
            'Manga': {
                'prompt_prefix': 'manga style illustration',
                'style_elements': 'Japanese manga art, expressive eyes, dynamic poses, screen tone effects',
                'negative_prompt': 'realistic, photographic, western cartoon'
            },
            'Anime': {
                'prompt_prefix': 'anime style illustration', 
                'style_elements': 'anime art style, large eyes, colorful hair, cel-shading',
                'negative_prompt': 'realistic, 3d render, manga hatching'
            },
            'Disney': {
                'prompt_prefix': 'Disney animation style illustration',
                'style_elements': 'Disney character design, magical atmosphere, classic animation style',
                'negative_prompt': 'anime, manga, realistic, dark themes'
            },
            'Pixar': {
                'prompt_prefix': 'Pixar 3D animation style illustration',
                'style_elements': 'Pixar character design, 3D rendered look, warm lighting, friendly characters',
                'negative_prompt': '2d animation, flat colors, anime, manga'
            },
            'Cartoon': {
                'prompt_prefix': 'cartoon style illustration',
                'style_elements': 'simple cartoon art, bold colors, exaggerated features, child-friendly',
                'negative_prompt': 'realistic, complex details, dark themes'
            },
            'Ghibli': {
                'prompt_prefix': 'Studio Ghibli style illustration',
                'style_elements': 'Ghibli art style, nature themes, magical realism, hand-drawn animation',
                'negative_prompt': 'modern animation, CGI, simple cartoon'
            },
            'Simple': {
                'prompt_prefix': 'simple illustration style',
                'style_elements': 'minimalist design, basic shapes, clear lines, preschool appropriate',
                'negative_prompt': 'complex details, realistic, mature themes'
            },
            'Pixel': {
                'prompt_prefix': 'pixel art style illustration',
                'style_elements': '8-bit pixel art, retro game style, blocky characters',
                'negative_prompt': 'smooth lines, high resolution, realistic'
            },
            'Modern_KPop': {
                'prompt_prefix': 'modern K-pop style illustration',
                'style_elements': 'trendy fashion, vibrant colors, stylish characters, contemporary design',
                'negative_prompt': 'traditional style, old-fashioned, muted colors'
            }
        }
        
        # Prompt enhancement settings
        self.enhancement_settings = {
            'quality_boosters': [
                'high quality', 'professional illustration', 'detailed artwork',
                'masterpiece', 'best quality', 'clean lines'
            ],
            'coloring_book_elements': [
                'black and white line art', 'thick black outlines', 'pure white background',
                'no shading', 'no gray areas', 'perfect for coloring', 'high contrast'
            ],
            'kid_friendly_elements': [
                'child-friendly', 'wholesome', 'innocent', 'happy', 'positive',
                'educational', 'safe for children', 'family-friendly'
            ]
        }
    
    def load_model(self) -> bool:
        """Load FLUX model with enhanced settings"""
        logger.info("Loading enhanced FLUX model...")
        return self.base_generator.load_model()
    
    def create_character_consistency_seed(self, character_name: str, story_id: str) -> int:
        """Create or retrieve consistent seed for character across story"""
        
        character_key = f"{story_id}_{character_name}"
        
        if character_key not in self.character_seeds:
            # Generate deterministic seed based on character name and story
            seed = hash(character_key) % 1000000
            self.character_seeds[character_key] = seed
            logger.info(f"Created consistent seed {seed} for {character_name} in {story_id}")
        
        return self.character_seeds[character_key]
    
    def build_enhanced_prompt(self, base_prompt: str, style_name: str, 
                            character_consistency: Dict[str, str] = None,
                            prompt_type: str = 'coloring_page') -> str:
        """Build enhanced prompt with better style adherence and character consistency"""
        
        # Get style enhancer
        style_info = self.style_enhancers.get(style_name, self.style_enhancers['Cartoon'])
        
        # Start with style prefix
        enhanced_prompt = f"{style_info['prompt_prefix']}, "
        
        # Add character consistency if provided
        if character_consistency:
            for char_name, description in character_consistency.items():
                enhanced_prompt += f"{description}, "
        
        # Add the base scene/content
        enhanced_prompt += f"{base_prompt}, "
        
        # Add style elements
        enhanced_prompt += f"{style_info['style_elements']}, "
        
        # Add quality boosters
        enhanced_prompt += ", ".join(self.enhancement_settings['quality_boosters']) + ", "
        
        # Add coloring book or cover specific elements
        if prompt_type == 'coloring_page':
            enhanced_prompt += ", ".join(self.enhancement_settings['coloring_book_elements']) + ", "
        elif prompt_type == 'cover':
            enhanced_prompt += "vibrant colors, book cover design, title space, "
        
        # Add kid-friendly elements
        enhanced_prompt += ", ".join(self.enhancement_settings['kid_friendly_elements'])
        
        # Clean up the prompt
        enhanced_prompt = enhanced_prompt.replace(", ,", ",").strip().rstrip(",")
        
        logger.info(f"Enhanced prompt (first 150 chars): {enhanced_prompt[:150]}...")
        return enhanced_prompt
    
    def build_negative_prompt(self, style_name: str, prompt_type: str = 'coloring_page') -> str:
        """Build negative prompt to avoid unwanted elements"""
        
        style_info = self.style_enhancers.get(style_name, self.style_enhancers['Cartoon'])
        
        negative_elements = [
            style_info['negative_prompt'],
            'nsfw', 'inappropriate', 'scary', 'violent', 'dark themes',
            'adult content', 'weapons', 'horror', 'blood'
        ]
        
        if prompt_type == 'coloring_page':
            negative_elements.extend([
                'colors', 'colored', 'shading', 'shadows', 'gray areas',
                'gradients', 'photorealistic', 'blurry', 'low quality'
            ])
        
        return ", ".join(negative_elements)
    
    def generate_with_enhanced_prompts(self, prompt_data: Dict[str, str], 
                                     story_data: Dict[str, Any],
                                     width: int = 840, height: int = 592) -> Optional[Image.Image]:
        """Generate image with enhanced prompt following and character consistency"""
        
        style_name = story_data['art_style']['name']
        story_id = story_data['id']
        
        # Build character consistency descriptions
        character_consistency = {}
        main_char = story_data.get('main_character', '')
        companion = story_data.get('companion', '')
        
        if main_char:
            # Create consistent character description
            char_seed = self.create_character_consistency_seed(main_char, story_id)
            character_consistency[main_char] = f"consistent character {main_char}, same appearance throughout story"
        
        if companion:
            char_seed = self.create_character_consistency_seed(companion, story_id) 
            character_consistency[companion] = f"consistent character {companion}, same appearance throughout story"
        
        # Build enhanced prompt
        enhanced_prompt = self.build_enhanced_prompt(
            base_prompt=prompt_data['prompt'],
            style_name=style_name,
            character_consistency=character_consistency,
            prompt_type=prompt_data.get('type', 'coloring_page')
        )
        
        # Build negative prompt
        negative_prompt = self.build_negative_prompt(
            style_name=style_name,
            prompt_type=prompt_data.get('type', 'coloring_page')
        )
        
        # Use character-consistent seed if available
        seed = self.character_seeds.get(f"{story_id}_{main_char}", torch.randint(0, 1000000, (1,)).item())
        
        logger.info(f"Generating with enhanced settings:")
        logger.info(f"Style: {style_name}")
        logger.info(f"Seed: {seed}")
        logger.info(f"Type: {prompt_data.get('type', 'coloring_page')}")
        
        try:
            # Generate with enhanced settings
            image = self.base_generator.generate(
                prompt=enhanced_prompt,
                width=width,
                height=height,
                seed=seed,
                num_inference_steps=6,  # Slightly more steps for better quality
                guidance_scale=0.0,     # FLUX-schnell doesn't use guidance
            )
            
            if image and prompt_data.get('type') == 'coloring_page':
                # Apply enhanced coloring book optimization
                image = self.enhance_for_coloring_book(image, style_name)
            
            return image
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None
    
    def enhance_for_coloring_book(self, image: Image.Image, style_name: str) -> Image.Image:
        """Enhanced coloring book optimization based on style"""
        
        logger.info(f"Applying enhanced coloring book optimization for {style_name}")
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Style-specific processing
        if style_name == 'Manga':
            # Manga-style processing with screen tones
            gray = cv2.bilateralFilter(gray, 9, 75, 75)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 7)
            
        elif style_name == 'Anime':
            # Anime-style with clean lines
            gray = cv2.medianBlur(gray, 5)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 9, 9)
            
        elif style_name == 'Disney' or style_name == 'Pixar':
            # Smooth Disney/Pixar style lines
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 11)
            
        elif style_name == 'Simple':
            # Very simple lines for young children
            gray = cv2.medianBlur(gray, 7)
            _, edges = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
            
        elif style_name == 'Pixel':
            # Pixel art style - maintain blocky appearance
            # Resize down and back up to create pixel effect
            small = cv2.resize(gray, (gray.shape[1]//8, gray.shape[0]//8), interpolation=cv2.INTER_NEAREST)
            gray = cv2.resize(small, (gray.shape[1], gray.shape[0]), interpolation=cv2.INTER_NEAREST)
            _, edges = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
            
        else:
            # Default processing for other styles
            gray = cv2.bilateralFilter(gray, 7, 50, 50)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        
        # Clean up the edges
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)
        
        # Convert back to PIL Image
        result = Image.fromarray(edges)
        result = result.convert('RGB')
        
        # Ensure pure white background and black lines
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(1.5)  # Increase contrast
        
        return result
    
    def generate_colored_cover(self, prompt_data: Dict[str, str], 
                             story_data: Dict[str, Any],
                             width: int = 840, height: int = 592) -> Optional[Image.Image]:
        """Generate colored cover image (not for coloring)"""
        
        logger.info("Generating colored cover image")
        
        # Force cover type
        cover_prompt_data = prompt_data.copy()
        cover_prompt_data['type'] = 'cover'
        
        # Generate colored cover
        image = self.generate_with_enhanced_prompts(
            prompt_data=cover_prompt_data,
            story_data=story_data,
            width=width,
            height=height
        )
        
        # Apply cover-specific enhancements
        if image:
            image = self.enhance_cover_image(image, story_data['art_style']['name'])
        
        return image
    
    def enhance_cover_image(self, image: Image.Image, style_name: str) -> Image.Image:
        """Enhance cover image with vibrant colors and professional look"""
        
        logger.info(f"Enhancing cover image for {style_name} style")
        
        # Increase saturation for more vibrant colors
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.3)
        
        # Slight contrast boost
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        # Slight sharpening
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        
        return image
    
    def cleanup_memory(self):
        """Clean up GPU memory"""
        gc.collect()
        torch.cuda.empty_cache()
        logger.info("Memory cleaned up")

def test_enhanced_generator():
    """Test the enhanced FLUX generator"""
    
    print("🧪 Testing Enhanced FLUX Generator...")
    
    generator = EnhancedFluxGenerator()
    
    # Load model
    if not generator.load_model():
        print("❌ Failed to load FLUX model")
        return
    
    print("✅ FLUX model loaded")
    
    # Test story data
    test_story = {
        'id': 'test_story_001',
        'title': 'Test Adventure',
        'main_character': 'Alex',
        'companion': 'Buddy the Dog',
        'art_style': {
            'name': 'Disney',
            'coloring_style': 'Disney style black and white line art',
            'cover_style': 'Disney animation style with magical colors'
        }
    }
    
    # Test coloring page prompt
    test_prompt = {
        'type': 'coloring_page',
        'prompt': 'Alex and Buddy the Dog playing in a magical garden with flowers and butterflies',
        'scene_description': 'Playing in garden'
    }
    
    print("\n🎨 Testing coloring page generation...")
    start_time = time.time()
    
    image = generator.generate_with_enhanced_prompts(
        prompt_data=test_prompt,
        story_data=test_story,
        width=592,
        height=840
    )
    
    if image:
        # Save test image
        image.save("test_coloring_page.png")
        elapsed = time.time() - start_time
        print(f"✅ Coloring page generated in {elapsed:.1f}s")
        print(f"📁 Saved: test_coloring_page.png")
    else:
        print("❌ Coloring page generation failed")
        return
    
    # Test cover generation
    cover_prompt = {
        'type': 'cover',
        'prompt': 'Alex and Buddy the Dog magical adventure book cover',
        'scene_description': 'Cover image'
    }
    
    print("\n🎨 Testing cover generation...")
    start_time = time.time()
    
    cover_image = generator.generate_colored_cover(
        prompt_data=cover_prompt,
        story_data=test_story,
        width=592,
        height=840
    )
    
    if cover_image:
        cover_image.save("test_cover.png")
        elapsed = time.time() - start_time
        print(f"✅ Cover generated in {elapsed:.1f}s")
        print(f"📁 Saved: test_cover.png")
    else:
        print("❌ Cover generation failed")
    
    generator.cleanup_memory()
    print("\n🎉 Enhanced generator test completed!")

if __name__ == "__main__":
    test_enhanced_generator()