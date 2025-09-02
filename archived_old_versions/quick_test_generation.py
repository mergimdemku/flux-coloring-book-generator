#!/usr/bin/env python3
"""
Quick test to generate a cover and one coloring page
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from clean_line_flux_generator import CleanLineFluxGenerator
from enhanced_pdf_generator import EnhancedPDFGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_story():
    """Create a simple test story with cover and one page"""
    return {
        "book": {
            "title": "Test Bunny's Quick Adventure",
            "age_range": "4-7",
            "paper": {
                "size": "8.5x11in",
                "dpi": 300,
                "orientation": "portrait"
            },
            "style": "black-and-white coloring page, kid-friendly, thick clean outlines, minimal detail, high contrast, no grayscale, no text",
            "negative": "color, grey, shading, gradients, tiny patterns, cluttered backgrounds, logos, watermarks, photorealism, text, numbers, letters, words",
            "cover_prompt": "cute bunny with floppy ears with tiny blue bow standing in magical garden; big flowers around; butterfly flying above; simple composition, large shapes, kid-friendly",
            "back_blurb": "Join Test Bunny on a quick adventure!",
            "pages": [
                {
                    "id": 1,
                    "text": "Bunny finds a magical flower in the garden!",
                    "scene": "cute bunny with floppy ears with tiny blue bow looking at giant magical flower; sparkles around flower; garden background with trees"
                }
            ]
        }
    }

def main():
    print("🧪 Quick Test Generation - Cover + 1 Coloring Page")
    print("=" * 50)
    
    # Initialize generators
    print("\n📦 Initializing generators...")
    flux_gen = CleanLineFluxGenerator()
    pdf_gen = EnhancedPDFGenerator("test_output")
    
    # Create output directory
    Path("test_output").mkdir(exist_ok=True)
    
    # Load FLUX model
    print("🔮 Loading FLUX model...")
    if not flux_gen.load_model():
        print("❌ Failed to load FLUX model")
        print("Make sure you have HuggingFace authentication set up:")
        print("  huggingface-cli login")
        return
    
    print("✅ FLUX model loaded successfully")
    
    # Create test story
    story_data = create_test_story()
    book = story_data['book']
    
    print(f"\n📖 Test Story: {book['title']}")
    print(f"📝 Pages: Cover + {len(book['pages'])} coloring page(s)")
    
    # Prepare story info for generators
    story_info = {
        'id': f"test_{int(datetime.now().timestamp())}",
        'title': book['title'],
        'age_range': book['age_range'],
        'style': book['style'],
        'art_style': {'name': 'Simple'},  # For compatibility
        'negative': book['negative']
    }
    
    # Generate Cover
    print("\n🎨 Generating cover image...")
    cover_prompt = {
        'prompt': f"{book['cover_prompt']}, {book['style']}",
        'negative': book['negative']
    }
    
    cover_image = flux_gen.generate_perfect_cover(
        prompt_data=cover_prompt,
        story_data=story_info,
        width=592,
        height=832  # Divisible by 16
    )
    
    if cover_image:
        cover_path = Path("test_output/test_cover.png")
        cover_image.save(cover_path)
        print(f"✅ Cover saved: {cover_path}")
    else:
        print("❌ Failed to generate cover")
        return
    
    # Generate Coloring Page
    print("\n🖍️ Generating coloring page...")
    page = book['pages'][0]
    page_prompt = {
        'prompt': f"{page['scene']}, {book['style']}",
        'negative': book['negative']
    }
    
    coloring_image = flux_gen.generate_ultra_clean_coloring_page(
        prompt_data=page_prompt,
        story_data=story_info,
        width=592,
        height=832  # Divisible by 16
    )
    
    if coloring_image:
        coloring_path = Path("test_output/test_coloring_page_1.png")
        coloring_image.save(coloring_path)
        print(f"✅ Coloring page saved: {coloring_path}")
    else:
        print("❌ Failed to generate coloring page")
        return
    
    # Create PDF
    print("\n📚 Creating PDF...")
    prompts_data = [
        {'scene_description': 'Cover'},
        {'scene_description': page['text']}
    ]
    
    pdf_filename = pdf_gen.generate_complete_book_pdf(
        story_data=story_info,
        cover_image=cover_image,
        coloring_images=[coloring_image],
        prompts_data=prompts_data
    )
    
    if pdf_filename:
        print(f"✅ PDF created: {pdf_filename}")
    else:
        print("❌ Failed to create PDF")
    
    # Clean up memory
    flux_gen.cleanup_memory()
    
    print("\n" + "=" * 50)
    print("🎉 Test generation complete!")
    print(f"📁 Check 'test_output' folder for results:")
    print("  - test_cover.png (colored cover)")
    print("  - test_coloring_page_1.png (black & white for coloring)")
    print(f"  - {Path(pdf_filename).name if pdf_filename else 'PDF'} (complete book)")

if __name__ == "__main__":
    main()