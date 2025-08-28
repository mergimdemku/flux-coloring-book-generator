#!/usr/bin/env python3
"""
Clean Line FLUX Generator - Focused on Ultra Clean Lines and Proper Covers
"""

import torch
import gc
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from pathlib import Path
import logging
from enhanced_flux_generator import EnhancedFluxGenerator
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CleanLineFluxGenerator(EnhancedFluxGenerator):
    """Enhanced FLUX generator focused on ultra-clean lines and proper covers"""
    
    def __init__(self):
        super().__init__()
        
        # Enhanced style settings for ULTRA CLEAN lines with strong anatomy controls
        self.clean_line_enhancers = {
            'Manga': {
                'prompt_prefix': 'professional manga illustration',
                'style_elements': 'manga art style, ultra clean sharp black lines, high contrast lineart, perfect anatomically correct characters, professional manga quality, clean outlines, single continuous lines',
                'negative_prompt': 'blurry lines, sketchy, rough lines, dirty lines, messy artwork, low quality lines, broken lines, disconnected lines',
                'line_processing': 'manga_clean'
            },
            'Anime': {
                'prompt_prefix': 'professional anime illustration', 
                'style_elements': 'anime art style, crisp clean black outlines, perfect line art, cel-animation quality, ultra clean continuous lines, anatomically correct proportions',
                'negative_prompt': 'rough lines, sketchy, blurry outlines, messy lines, low quality, broken outlines, jagged edges',
                'line_processing': 'anime_clean'
            },
            'Disney': {
                'prompt_prefix': 'professional Disney animation style',
                'style_elements': 'Disney character design, smooth clean black lines, perfect continuous outlines, professional animation quality, pristine line work, correct anatomy',
                'negative_prompt': 'rough sketch, messy lines, amateur artwork, dirty lines, broken lines, disconnected outlines',
                'line_processing': 'disney_smooth'
            },
            'Pixar': {
                'prompt_prefix': 'professional Pixar 3D style',
                'style_elements': 'Pixar character design, clean smooth black outlines, 3D animation style, perfect line definition, correct proportions',
                'negative_prompt': 'rough edges, jagged lines, low quality 3D, messy outlines, broken lines, poor anatomy',
                'line_processing': 'pixar_smooth'
            },
            'Cartoon': {
                'prompt_prefix': 'professional cartoon illustration',
                'style_elements': 'cartoon style, bold clean black lines, perfect thick outlines, child-friendly design, ultra clean artwork, simple correct anatomy',
                'negative_prompt': 'messy lines, rough sketch, amateur cartoon, dirty artwork, thin lines, broken outlines',
                'line_processing': 'cartoon_bold'
            },
            'Ghibli': {
                'prompt_prefix': 'professional Studio Ghibli style',
                'style_elements': 'Studio Ghibli art style, delicate clean black lines, hand-drawn quality, pristine continuous line work, magical clean artwork',
                'negative_prompt': 'rough sketch, messy lines, digital artifacts, low quality, broken lines, poor line quality',
                'line_processing': 'ghibli_delicate'
            },
            'Simple': {
                'prompt_prefix': 'professional simple illustration',
                'style_elements': 'simple clean design, ultra thick clean black lines, perfect for toddlers, pristine simple artwork, bold continuous outlines',
                'negative_prompt': 'complex details, messy lines, thin lines, rough artwork, broken lines, poor quality outlines',
                'line_processing': 'simple_thick'
            },
            'Pixel': {
                'prompt_prefix': 'professional pixel art',
                'style_elements': 'pixel art style, clean pixel edges, sharp boundaries, retro game quality, perfect pixel alignment, clear pixel outlines',
                'negative_prompt': 'blurry pixels, anti-aliasing, smooth edges, messy pixels, broken pixel art, poor pixel quality',
                'line_processing': 'pixel_sharp'
            },
            'Modern_KPop': {
                'prompt_prefix': 'professional modern illustration',
                'style_elements': 'modern style, clean trendy black lines, fashion illustration quality, crisp contemporary artwork, stylish clean design',
                'negative_prompt': 'old-fashioned, messy lines, rough artwork, amateur design, broken lines, poor line quality',
                'line_processing': 'modern_crisp'
            }
        }
        
        # Ultra-clean line processing settings
        self.line_quality_settings = {
            'high_contrast_threshold': 200,
            'line_smoothing': True,
            'edge_enhancement': True,
            'noise_reduction': True,
            'line_thickness_optimization': True
        }
    
    def build_ultra_clean_prompt(self, base_prompt: str, style_name: str, 
                                character_consistency: Dict[str, str] = None,
                                prompt_type: str = 'coloring_page') -> str:
        """Build prompt optimized for ultra-clean lines"""
        
        # Get clean line enhancer
        style_info = self.clean_line_enhancers.get(style_name, self.clean_line_enhancers['Cartoon'])
        
        # Start with professional style prefix
        enhanced_prompt = f"{style_info['prompt_prefix']}, "
        
        # Add character consistency if provided
        if character_consistency:
            for char_name, description in character_consistency.items():
                enhanced_prompt += f"{description}, "
        
        # Add the base scene/content
        enhanced_prompt += f"{base_prompt}, "
        
        # Add ultra-clean style elements
        enhanced_prompt += f"{style_info['style_elements']}, "
        
        # Add ultra-clean quality boosters with anatomical correctness
        ultra_clean_boosters = [
            'masterpiece quality', 'ultra clean continuous lines', 'perfect line art', 
            'professional illustration', 'high quality artwork', 'pristine unbroken lines',
            'sharp clean edges', 'perfect continuous outlines', 'crisp line work',
            'anatomically correct', 'proper proportions', 'correct anatomy',
            'perfect body structure', 'normal human anatomy', 'realistic proportions'
        ]
        enhanced_prompt += ", ".join(ultra_clean_boosters) + ", "
        
        # Add coloring book or cover specific elements
        if prompt_type == 'coloring_page':
            coloring_elements = [
                'black and white line art only', 'pure white background', 
                'NO TEXT AT ALL', 'NO WORDS', 'NO LETTERS', 'NO NUMBERS', 'NO LOGOS',
                'wordless image', 'text-free illustration', 'no page numbers',
                'no shading', 'no gray areas', 'thick black outlines', 
                'perfect for coloring', 'ultra high contrast', 'clean coloring book page'
            ]
            enhanced_prompt += ", ".join(coloring_elements) + ", "
        elif prompt_type == 'cover':
            cover_elements = [
                'vibrant full colors', 'professional book cover design', 
                'full page illustration', 'edge to edge artwork', 'full bleed cover',
                'NO TEXT AT ALL', 'NO WORDS', 'NO LETTERS', 'NO TITLE', 'NO LOGOS',
                'wordless cover', 'text-free illustration'
            ]
            enhanced_prompt += ", ".join(cover_elements) + ", "
        
        # Add kid-friendly elements
        kid_elements = [
            'child-friendly', 'wholesome', 'innocent', 'happy', 'positive',
            'safe for children', 'family-friendly', 'age-appropriate'
        ]
        enhanced_prompt += ", ".join(kid_elements)
        
        # Clean up the prompt
        enhanced_prompt = enhanced_prompt.replace(", ,", ",").strip().rstrip(",")
        
        logger.info(f"Ultra-clean prompt (first 150 chars): {enhanced_prompt[:150]}...")
        return enhanced_prompt
    
    def build_ultra_clean_negative_prompt(self, style_name: str, prompt_type: str = 'coloring_page') -> str:
        """Build comprehensive negative prompt with anatomical controls"""
        
        style_info = self.clean_line_enhancers.get(style_name, self.clean_line_enhancers['Cartoon'])
        
        # ANATOMICAL ISSUES - Most Critical - EXPANDED
        anatomical_issues = [
            'two heads', 'multiple heads', 'extra heads', 'double head', 'second head',
            'three arms', 'four arms', 'extra arms', 'multiple arms', 'wrong number of arms', 'third arm',
            'three hands', 'four hands', 'extra hands', 'multiple hands', 'missing hands', 
            'six fingers', 'seven fingers', 'extra fingers', 'too many fingers', 'wrong number of fingers',
            'three legs', 'four legs', 'five legs', 'six legs', 'extra legs', 'multiple legs', 'third leg',
            'three feet', 'four feet', 'five feet', 'six feet', 'extra feet', 'multiple feet',
            'extra limbs', 'missing limbs', 'malformed limbs', 'wrong anatomy', 'deformed',
            'extra eyes', 'missing eyes', 'wrong eye placement', 'asymmetric eyes', 'third eye',
            'extra ears', 'missing ears', 'malformed ears', 'wrong ear placement',
            'multiple tails', 'extra tails', 'wrong tail placement', 'extra tail',
            'deformed body', 'twisted anatomy', 'broken proportions', 'incorrect anatomy',
            'extra body parts', 'duplicate body parts', 'floating limbs', 'disconnected body parts',
            'mutated', 'mutation', 'disfigured', 'malformed', 'body horror', 'anatomical errors'
        ]
        
        # LINE QUALITY ISSUES
        line_quality_issues = [
            style_info['negative_prompt'],
            'blurry lines', 'sketchy lines', 'rough artwork', 'messy lines', 'dirty lines',
            'smudged lines', 'broken lines', 'disconnected lines', 'jagged edges', 'poor line quality',
            'low quality lines', 'amateur artwork', 'unfinished lines', 'incomplete lines',
            'pixelated lines', 'aliased edges', 'compression artifacts', 'artifact lines',
            'double lines', 'ghost lines', 'fuzzy outlines', 'unclear boundaries'
        ]
        
        # GENERAL QUALITY ISSUES
        quality_issues = [
            'low resolution', 'poor quality', 'amateur', 'unprofessional', 'ugly',
            'distorted', 'warped', 'stretched', 'compressed', 'out of focus',
            'noise', 'grain', 'artifacts', 'glitches', 'errors', 'mistakes'
        ]
        
        # INAPPROPRIATE CONTENT
        inappropriate_content = [
            'nsfw', 'inappropriate', 'scary', 'violent', 'dark themes',
            'adult content', 'weapons', 'horror', 'blood', 'gore', 'frightening'
        ]
        
        # Combine all negative elements
        negative_elements = anatomical_issues + line_quality_issues + quality_issues + inappropriate_content
        
        # NO TEXT AT ALL - CRITICAL FOR BOTH COVERS AND COLORING PAGES
        text_issues = [
            'text', 'words', 'letters', 'numbers', 'writing', 'fonts', 'typography',
            'page numbers', 'title text', 'captions', 'speech bubbles', 'dialogue',
            'labels', 'signs', 'banners', 'messages', 'quotes', 'sayings', 'logos',
            'watermarks', 'signatures', 'credits', 'copyright', 'branding',
            'alphabet', 'characters', 'symbols', 'inscriptions', 'annotations'
        ]
        negative_elements.extend(text_issues)
        
        if prompt_type == 'coloring_page':
            coloring_specific = [
                # NO COLORS OR SHADING
                'colors', 'colored', 'color fill', 'shading', 'shadows', 'gray areas',
                'gradients', 'tones', 'highlights', 'dark areas', 'light areas',
                
                # NO FILLED AREAS
                'solid colors', 'filled shapes', 'colored backgrounds', 'painted areas'
            ]
            negative_elements.extend(coloring_specific)
        
        return ", ".join(negative_elements)
    
    def apply_ultra_clean_line_processing(self, image: Image.Image, style_name: str) -> Image.Image:
        """Apply simple, effective line processing - no more overcomplicated BS"""
        
        logger.info(f"Applying SIMPLE line processing for {style_name}")
        
        # Convert to grayscale
        if image.mode != 'L':
            gray_img = image.convert('L')
        else:
            gray_img = image
        
        # Convert to numpy
        gray_array = np.array(gray_img)
        
        # Check brightness and enhance if needed
        mean_brightness = np.mean(gray_array)
        logger.info(f"Image brightness: {mean_brightness:.1f}")
        
        if mean_brightness > 240:
            logger.info("Very faint image - boosting contrast heavily")
            enhancer = ImageEnhance.Contrast(gray_img)
            gray_img = enhancer.enhance(8.0)
            gray_array = np.array(gray_img)
        elif mean_brightness > 200:
            logger.info("Faint image - boosting contrast moderately") 
            enhancer = ImageEnhance.Contrast(gray_img)
            gray_img = enhancer.enhance(4.0)
            gray_array = np.array(gray_img)
        
        # SIMPLE APPROACH: Just threshold to black and white, no BS
        
        # Use Otsu's method for automatic threshold selection
        _, binary = cv2.threshold(gray_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Invert if needed (we want black lines on white background)
        black_pixels = np.sum(binary == 0)
        white_pixels = np.sum(binary == 255)
        
        if black_pixels > white_pixels:
            binary = cv2.bitwise_not(binary)
            logger.info("Inverted image - now black lines on white background")
        
        # Light cleanup to connect nearby lines
        kernel = np.ones((2,2), np.uint8)
        edges = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Remove tiny noise
        kernel_small = np.ones((1,1), np.uint8)  
        edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel_small)
        
        # That's it! Simple and effective.
        
        # Convert back to PIL Image and done
        result = Image.fromarray(edges, mode='L')
        logger.info("Simple coloring page processing complete")
        
        return result
    
    def generate_perfect_cover(self, prompt_data: Dict[str, str], 
                              story_data: Dict[str, Any],
                              width: int = 592, height: int = 840) -> Optional[Image.Image]:
        """Generate perfect cover with title integration and full page layout"""
        
        logger.info("Generating perfect cover with integrated title")
        
        style_name = story_data['art_style']['name']
        story_id = story_data['id']
        title = story_data['title']
        
        # Build ultra-clean cover prompt WITHOUT text
        enhanced_prompt = self.build_ultra_clean_prompt(
            base_prompt=prompt_data['prompt'],
            style_name=style_name,
            prompt_type='cover'
        )
        
        negative_prompt = self.build_ultra_clean_negative_prompt(
            style_name=style_name,
            prompt_type='cover'
        )
        
        # Generate cover with higher quality settings
        seed = self.character_seeds.get(f"{story_id}_{story_data.get('main_character', '')}", torch.randint(0, 1000000, (1,)).item())
        
        logger.info(f"Generating cover with enhanced settings:")
        logger.info(f"Style: {style_name}")
        logger.info(f"Seed: {seed}")
        
        try:
            # Generate with enhanced settings for cover quality
            image = self.base_generator.generate(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height, 
                seed=seed,
                num_inference_steps=8,  # More steps for cover quality
                guidance_scale=0.0,
            )
            
            if image:
                # Apply cover-specific enhancements
                image = self.enhance_cover_quality(image, style_name, title, width, height)
            
            return image
            
        except Exception as e:
            logger.error(f"Cover generation failed: {e}")
            return None
    
    def enhance_cover_quality(self, image: Image.Image, style_name: str, title: str, width: int, height: int) -> Image.Image:
        """Enhance cover quality and ensure full page layout"""
        
        logger.info(f"Enhancing cover quality for {style_name} style")
        
        # Resize to full page if needed
        if image.size != (width, height):
            # Calculate scaling to fill page while maintaining aspect ratio
            img_ratio = image.width / image.height
            page_ratio = width / height
            
            if img_ratio > page_ratio:
                # Image is wider - fit to height and crop width
                new_height = height
                new_width = int(height * img_ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                # Crop to center
                left = (new_width - width) // 2
                image = image.crop((left, 0, left + width, height))
            else:
                # Image is taller - fit to width and crop height  
                new_width = width
                new_height = int(width / img_ratio)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                # Crop to center
                top = (new_height - height) // 2
                image = image.crop((0, top, width, top + height))
        
        # If image is smaller than page, center it on white background
        if image.size[0] < width or image.size[1] < height:
            background = Image.new('RGB', (width, height), 'white')
            x = (width - image.width) // 2
            y = (height - image.height) // 2
            background.paste(image, (x, y))
            image = background
        
        # Enhance colors and sharpness for cover
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.3)
        
        return image
    
    def generate_ultra_clean_coloring_page(self, prompt_data: Dict[str, str], 
                                          story_data: Dict[str, Any],
                                          width: int = 592, height: int = 840) -> Optional[Image.Image]:
        """Generate ultra-clean coloring page with no text"""
        
        # Use the enhanced prompt building
        enhanced_prompt = self.build_ultra_clean_prompt(
            base_prompt=prompt_data['prompt'],
            style_name=story_data['art_style']['name'],
            prompt_type='coloring_page'
        )
        
        negative_prompt = self.build_ultra_clean_negative_prompt(
            style_name=story_data['art_style']['name'],
            prompt_type='coloring_page'
        )
        
        # Generate base image using the enhanced prompts
        story_id = story_data['id']
        seed = self.character_seeds.get(f"{story_id}_{story_data.get('main_character', '')}", torch.randint(0, 1000000, (1,)).item())
        
        logger.info(f"Generating coloring page with enhanced prompts")
        logger.info(f"Style: {story_data['art_style']['name']}")
        logger.info(f"Seed: {seed}")
        
        try:
            # Generate using enhanced prompts with negative prompts
            image = self.base_generator.generate(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                seed=seed,
                num_inference_steps=4,
                guidance_scale=0.0,
            )
            
            if image:
                # Apply ultra-clean line processing
                image = self.apply_ultra_clean_line_processing(image, story_data['art_style']['name'])
            
            return image
            
        except Exception as e:
            logger.error(f"Coloring page generation failed: {e}")
            return None

def test_clean_line_generator():
    """Test the clean line generator"""
    
    print("🧪 Testing Clean Line FLUX Generator...")
    
    generator = CleanLineFluxGenerator()
    
    if not generator.load_model():
        print("❌ Failed to load FLUX model")
        return
    
    print("✅ FLUX model loaded")
    
    # Test with improved story
    from improved_story_generator import ImprovedStoryGenerator
    
    story_gen = ImprovedStoryGenerator()
    batch = story_gen.get_next_story_batch()
    
    story_data = batch['story_data']
    prompts = batch['prompts']
    
    print(f"\n📖 Testing with story: {story_data['title']}")
    print(f"🎨 Style: {story_data['art_style']['name']}")
    
    # Test cover generation
    print("\n🖼️  Testing cover generation...")
    cover_image = generator.generate_perfect_cover(
        prompt_data=prompts[0],  # Cover prompt
        story_data=story_data,
        width=400,
        height=600
    )
    
    if cover_image:
        cover_image.save("test_clean_cover.png")
        print("✅ Clean cover generated: test_clean_cover.png")
    
    # Test coloring page generation
    print("\n🎨 Testing ultra-clean coloring page...")
    coloring_image = generator.generate_ultra_clean_coloring_page(
        prompt_data=prompts[1],  # First coloring page
        story_data=story_data,
        width=400,
        height=600
    )
    
    if coloring_image:
        coloring_image.save("test_clean_coloring.png")
        print("✅ Ultra-clean coloring page generated: test_clean_coloring.png")
    
    generator.cleanup_memory()
    print("\n🎉 Clean line generator test completed!")

if __name__ == "__main__":
    test_clean_line_generator()