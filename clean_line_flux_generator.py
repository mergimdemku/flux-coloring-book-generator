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
        
        # Enhanced style settings for ULTRA CLEAN lines
        self.clean_line_enhancers = {
            'Manga': {
                'prompt_prefix': 'professional manga illustration',
                'style_elements': 'manga art style, ultra clean sharp lines, high contrast black lines, perfect line work, professional manga quality',
                'negative_prompt': 'blurry lines, sketchy, rough lines, dirty lines, messy artwork, low quality lines',
                'line_processing': 'manga_clean'
            },
            'Anime': {
                'prompt_prefix': 'professional anime illustration', 
                'style_elements': 'anime art style, crisp clean outlines, perfect line art, cel-animation quality, ultra clean lines',
                'negative_prompt': 'rough lines, sketchy, blurry outlines, messy lines, low quality',
                'line_processing': 'anime_clean'
            },
            'Disney': {
                'prompt_prefix': 'professional Disney animation style',
                'style_elements': 'Disney character design, smooth clean lines, perfect outlines, professional animation quality, pristine line work',
                'negative_prompt': 'rough sketch, messy lines, amateur artwork, dirty lines',
                'line_processing': 'disney_smooth'
            },
            'Pixar': {
                'prompt_prefix': 'professional Pixar 3D style',
                'style_elements': 'Pixar character design, clean smooth outlines, 3D animation style, perfect line definition',
                'negative_prompt': 'rough edges, jagged lines, low quality 3D, messy outlines',
                'line_processing': 'pixar_smooth'
            },
            'Cartoon': {
                'prompt_prefix': 'professional cartoon illustration',
                'style_elements': 'cartoon style, bold clean lines, perfect outlines, child-friendly design, ultra clean artwork',
                'negative_prompt': 'messy lines, rough sketch, amateur cartoon, dirty artwork',
                'line_processing': 'cartoon_bold'
            },
            'Ghibli': {
                'prompt_prefix': 'professional Studio Ghibli style',
                'style_elements': 'Studio Ghibli art style, delicate clean lines, hand-drawn quality, pristine line work, magical clean artwork',
                'negative_prompt': 'rough sketch, messy lines, digital artifacts, low quality',
                'line_processing': 'ghibli_delicate'
            },
            'Simple': {
                'prompt_prefix': 'professional simple illustration',
                'style_elements': 'simple clean design, ultra thick clean lines, perfect for toddlers, pristine simple artwork, bold clean outlines',
                'negative_prompt': 'complex details, messy lines, thin lines, rough artwork',
                'line_processing': 'simple_thick'
            },
            'Pixel': {
                'prompt_prefix': 'professional pixel art',
                'style_elements': 'pixel art style, clean pixel edges, sharp boundaries, retro game quality, perfect pixel alignment',
                'negative_prompt': 'blurry pixels, anti-aliasing, smooth edges, messy pixels',
                'line_processing': 'pixel_sharp'
            },
            'Modern_KPop': {
                'prompt_prefix': 'professional modern illustration',
                'style_elements': 'modern style, clean trendy lines, fashion illustration quality, crisp contemporary artwork, stylish clean design',
                'negative_prompt': 'old-fashioned, messy lines, rough artwork, amateur design',
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
        
        # Add ultra-clean quality boosters
        ultra_clean_boosters = [
            'masterpiece quality', 'ultra clean lines', 'perfect line art', 
            'professional illustration', 'high quality artwork', 'pristine lines',
            'sharp clean edges', 'perfect outlines', 'crisp line work'
        ]
        enhanced_prompt += ", ".join(ultra_clean_boosters) + ", "
        
        # Add coloring book or cover specific elements
        if prompt_type == 'coloring_page':
            coloring_elements = [
                'black and white line art only', 'pure white background', 
                'no text', 'no words', 'no letters', 'no page numbers',
                'no shading', 'no gray areas', 'thick black outlines', 
                'perfect for coloring', 'ultra high contrast', 'clean coloring book page'
            ]
            enhanced_prompt += ", ".join(coloring_elements) + ", "
        elif prompt_type == 'cover':
            cover_elements = [
                'vibrant full colors', 'professional book cover design', 
                'title integrated in image', 'full page cover layout', 
                'beautiful typography', 'cover art quality'
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
        """Build negative prompt to ensure ultra-clean results"""
        
        style_info = self.clean_line_enhancers.get(style_name, self.clean_line_enhancers['Cartoon'])
        
        negative_elements = [
            style_info['negative_prompt'],
            'blurry lines', 'sketchy lines', 'rough artwork', 'messy lines',
            'dirty lines', 'smudged lines', 'broken lines', 'jagged edges',
            'low quality lines', 'amateur artwork', 'unfinished lines',
            'pixelated lines', 'aliased edges', 'compression artifacts',
            'nsfw', 'inappropriate', 'scary', 'violent', 'dark themes',
            'adult content', 'weapons', 'horror', 'blood'
        ]
        
        if prompt_type == 'coloring_page':
            negative_elements.extend([
                'colors', 'colored', 'shading', 'shadows', 'gray areas',
                'gradients', 'text', 'words', 'letters', 'numbers',
                'page numbers', 'title text', 'captions', 'speech bubbles'
            ])
        
        return ", ".join(negative_elements)
    
    def apply_ultra_clean_line_processing(self, image: Image.Image, style_name: str) -> Image.Image:
        """Apply ultra-clean line processing based on style"""
        
        logger.info(f"Applying ultra-clean line processing for {style_name}")
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale for processing
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Get processing type
        style_info = self.clean_line_enhancers.get(style_name, self.clean_line_enhancers['Cartoon'])
        processing_type = style_info['line_processing']
        
        # Apply style-specific ultra-clean processing
        if processing_type == 'manga_clean':
            # Manga: Sharp, high-contrast clean lines
            gray = cv2.bilateralFilter(gray, 9, 80, 80)  # Smooth while preserving edges
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 5)
            # Enhance line thickness and sharpness
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
        elif processing_type == 'anime_clean':
            # Anime: Crisp, clean cel-animation lines
            gray = cv2.medianBlur(gray, 3)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 7, 7)
            
        elif processing_type == 'disney_smooth' or processing_type == 'pixar_smooth':
            # Disney/Pixar: Smooth, flowing clean lines
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
            # Smooth the lines
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
        elif processing_type == 'cartoon_bold':
            # Cartoon: Bold, thick clean lines
            gray = cv2.medianBlur(gray, 5)
            _, edges = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)
            # Make lines thicker and bolder
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
            
        elif processing_type == 'simple_thick':
            # Simple: Very thick, ultra-clean lines for toddlers
            gray = cv2.medianBlur(gray, 7)
            _, edges = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
            # Make lines extra thick
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
            edges = cv2.dilate(edges, kernel, iterations=1)
            
        elif processing_type == 'pixel_sharp':
            # Pixel: Sharp pixel boundaries
            # Resize down and back up for pixel effect
            h, w = gray.shape
            small = cv2.resize(gray, (w//6, h//6), interpolation=cv2.INTER_NEAREST)
            gray = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
            _, edges = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
            
        elif processing_type == 'ghibli_delicate':
            # Ghibli: Delicate, hand-drawn clean lines
            gray = cv2.bilateralFilter(gray, 5, 50, 50)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 11)
            
        else:  # modern_crisp and default
            # Modern/Default: Crisp, contemporary clean lines  
            gray = cv2.bilateralFilter(gray, 7, 60, 60)
            edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)
        
        # Final ultra-clean processing
        # Remove noise
        edges = cv2.medianBlur(edges, 3)
        
        # Clean up isolated pixels
        kernel = np.ones((2, 2), np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # Convert back to PIL Image
        result = Image.fromarray(edges)
        result = result.convert('RGB')
        
        # Final enhancement for ultra-clean look
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(2.0)  # High contrast for clean lines
        
        # Final sharpening
        result = result.filter(ImageFilter.UnsharpMask(radius=1, percent=200, threshold=3))
        
        return result
    
    def generate_perfect_cover(self, prompt_data: Dict[str, str], 
                              story_data: Dict[str, Any],
                              width: int = 592, height: int = 840) -> Optional[Image.Image]:
        """Generate perfect cover with title integration and full page layout"""
        
        logger.info("Generating perfect cover with integrated title")
        
        style_name = story_data['art_style']['name']
        story_id = story_data['id']
        title = story_data['title']
        
        # Build ultra-clean cover prompt with title integration
        enhanced_prompt = self.build_ultra_clean_prompt(
            base_prompt=f"{prompt_data['prompt']}, title '{title}' beautifully integrated in the image design",
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
        
        # Generate base image
        image = self.generate_with_enhanced_prompts(prompt_data, story_data, width, height)
        
        if image:
            # Apply ultra-clean line processing
            image = self.apply_ultra_clean_line_processing(image, story_data['art_style']['name'])
        
        return image

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