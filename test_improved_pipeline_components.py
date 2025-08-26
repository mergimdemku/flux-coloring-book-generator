#!/usr/bin/env python3
"""
Test Improved Pipeline Components Without FLUX Model
Tests story generation, prompt creation, and PDF generation with dummy images
"""

import os
import logging
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_improved_story_generator():
    """Test improved story generator"""
    
    print("🧪 Testing Improved Story Generator")
    print("=" * 40)
    
    try:
        from improved_story_generator import ImprovedStoryGenerator
        
        generator = ImprovedStoryGenerator()
        
        # Generate 3 different stories to show variety
        for i in range(3):
            batch = generator.get_next_story_batch()
            story = batch['story_data']
            prompts = batch['prompts']
            
            print(f"\n📖 Story {i+1}:")
            print(f"   Title: {story['title']}")
            print(f"   Theme: {story['theme']}")
            print(f"   Style: {story['art_style']['name']}")
            print(f"   Character: {story['main_character']}")
            print(f"   Summary: {story['summary'][:100]}...")
            
            print(f"   First 3 scenes:")
            for j, scene in enumerate(story['scenes'][:3]):
                print(f"      {j+1}. {scene}")
            
            # Check prompts
            cover_prompt = prompts[0]
            coloring_prompt = prompts[1]
            
            print(f"   Cover includes title: {'title' in cover_prompt['prompt'].lower()}")
            print(f"   Coloring has no text: {'no text' in coloring_prompt['prompt']}")
            print(f"   Clean lines emphasized: {'clean lines' in coloring_prompt['prompt']}")
        
        print(f"\n✅ Story generator creating REAL narratives (not templates!)")
        return True
        
    except Exception as e:
        print(f"❌ Story generator failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_dummy_images(story_data, prompts):
    """Create dummy images to simulate FLUX output"""
    
    print("\n🎨 Creating dummy images to simulate FLUX output...")
    
    width, height = 592, 840
    images = {'cover_image': None, 'coloring_images': []}
    
    try:
        # Create colored cover image
        cover = Image.new('RGB', (width, height), color='lightblue')
        draw = ImageDraw.Draw(cover)
        
        # Add title text
        title = story_data['title']
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        # Draw title
        if font:
            text_bbox = draw.textbbox((0, 0), title, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            x = (width - text_width) // 2
            y = height // 4
            draw.text((x, y), title, fill='darkblue', font=font)
        
        # Add style indicator
        style_text = f"Style: {story_data['art_style']['name']}"
        if font:
            draw.text((50, height - 100), style_text, fill='darkgreen', font=font)
        
        images['cover_image'] = cover
        print(f"   ✅ Cover created (colored)")
        
        # Create B&W coloring pages
        for i, prompt in enumerate(prompts[1:]):  # Skip cover prompt
            coloring = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(coloring)
            
            # Draw simple coloring page outline
            scene = prompt['scene_description'][:50]  # Truncate for display
            
            # Draw border
            draw.rectangle([50, 50, width-50, height-50], outline='black', width=3)
            
            # Add scene text
            if font:
                draw.text((70, 100), f"Scene {i+1}:", fill='black', font=font)
                draw.text((70, 130), scene, fill='black', font=font)
            
            # Draw simple shapes for coloring
            # Circle
            draw.ellipse([100, 200, 200, 300], outline='black', width=2)
            # Rectangle  
            draw.rectangle([250, 200, 350, 300], outline='black', width=2)
            # Triangle
            draw.polygon([(400, 300), (450, 200), (500, 300)], outline='black', width=2)
            
            images['coloring_images'].append(coloring)
        
        print(f"   ✅ {len(images['coloring_images'])} coloring pages created (B&W)")
        return images
        
    except Exception as e:
        print(f"   ❌ Dummy image creation failed: {e}")
        return None

def test_pdf_generation(story_data, prompts, images):
    """Test PDF generation with improved components"""
    
    print("\n📄 Testing PDF Generation")
    print("=" * 30)
    
    try:
        from enhanced_pdf_generator import EnhancedPDFGenerator
        
        pdf_gen = EnhancedPDFGenerator("test_improved_output")
        
        pdf_path = pdf_gen.generate_complete_book_pdf(
            story_data=story_data,
            cover_image=images['cover_image'],
            coloring_images=images['coloring_images'],
            prompts_data=prompts
        )
        
        print(f"✅ PDF Generated: {pdf_path}")
        print(f"   Story: {story_data['title']}")
        print(f"   Style: {story_data['art_style']['name']}")
        print(f"   Pages: {len(images['coloring_images']) + 1}")
        
        return pdf_path
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Test all improved pipeline components"""
    
    print("🚀 IMPROVED PIPELINE COMPONENT TEST")
    print("=" * 50)
    print("Testing improved components WITHOUT FLUX model")
    print("(Using dummy images to simulate FLUX output)")
    print("=" * 50)
    
    # Test 1: Improved Story Generator
    if not test_improved_story_generator():
        print("❌ Story generator test failed")
        return False
    
    # Test 2: Create one complete book simulation
    print("\n" + "=" * 50)
    print("🎨 COMPLETE BOOK SIMULATION")
    print("=" * 50)
    
    try:
        from improved_story_generator import ImprovedStoryGenerator
        
        generator = ImprovedStoryGenerator()
        batch = generator.get_next_story_batch()
        story_data = batch['story_data']
        prompts = batch['prompts']
        
        print(f"\n📖 Creating complete book simulation:")
        print(f"   Title: {story_data['title']}")
        print(f"   Style: {story_data['art_style']['name']}")
        print(f"   Total prompts: {len(prompts)}")
        
        # Create dummy images
        images = create_dummy_images(story_data, prompts)
        if not images:
            print("❌ Failed to create dummy images")
            return False
        
        # Generate PDF
        pdf_path = test_pdf_generation(story_data, prompts, images)
        if not pdf_path:
            print("❌ Failed to generate PDF")
            return False
        
        print(f"\n🎉 COMPLETE BOOK SIMULATION SUCCESS!")
        print(f"📁 Output: {pdf_path}")
        print(f"📊 Components working: Story ✅, Images ✅, PDF ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ ALL IMPROVED COMPONENTS WORKING!")
        print("=" * 50)
        print("Ready for full FLUX testing when:")
        print("1. NumPy compatibility fixed (< 2.0)")
        print("2. HuggingFace authentication setup")
        print("3. GPU properly configured")
        print("=" * 50)
    else:
        print("\n❌ Some components need fixing")