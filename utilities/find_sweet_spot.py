#!/usr/bin/env python3
"""
FIND THE SWEET SPOT: Generate 1 cover + 1 coloring page with perfect settings
"""

import logging
from pathlib import Path
from improved_story_generator import ImprovedStoryGenerator
from clean_line_flux_generator import CleanLineFluxGenerator
from no_text_pdf_generator import NoTextPDFGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_sweet_spot():
    """Generate 1 cover + 1 coloring page to find optimal settings"""
    
    print("🎯 FINDING THE SWEET SPOT")
    print("=" * 50)
    print("Generating 1 cover + 1 coloring page with optimal settings")
    
    # Step 1: Get a story
    print("\n📖 Step 1: Getting story...")
    story_gen = ImprovedStoryGenerator()
    batch = story_gen.get_next_story_batch()
    
    story_data = batch['story_data']
    prompts = batch['prompts']
    
    print(f"✅ Story: {story_data['title']}")
    print(f"✅ Style: {story_data['art_style']['name']}")
    
    cover_prompt = prompts[0]
    coloring_prompt = prompts[1]
    
    # Step 2: Load FLUX generator
    print("\n⚡ Step 2: Loading FLUX generator...")
    generator = CleanLineFluxGenerator()
    
    if not generator.load_model():
        print("❌ FLUX model failed to load!")
        print("\n🔐 Authentication required!")
        print("To fix this:")
        print("1. Run: python setup_huggingface_auth.py")
        print("2. Follow the authentication steps")
        print("3. Try again")
        return False
    
    print("✅ FLUX model loaded successfully")
    
    # Step 3: Generate cover (COLORED)
    print(f"\n🖼️  Step 3: Generating COLORED COVER...")
    print(f"Scene: {cover_prompt['scene_description']}")
    
    cover_image = generator.generate_perfect_cover(
        prompt_data=cover_prompt,
        story_data=story_data,
        width=592,  # A4 compatible
        height=840
    )
    
    if not cover_image:
        print("❌ Cover generation FAILED!")
        return False
    
    # Save cover for inspection
    cover_path = "COVER_TEST.png"
    cover_image.save(cover_path)
    print(f"✅ Cover generated: {cover_path}")
    print(f"   Should be: COLORED with title integrated in image")
    
    # Step 4: Generate coloring page (B&W)
    print(f"\n🎨 Step 4: Generating B&W COLORING PAGE...")
    print(f"Scene: {coloring_prompt['scene_description']}")
    
    coloring_image = generator.generate_ultra_clean_coloring_page(
        prompt_data=coloring_prompt,
        story_data=story_data,
        width=592,  # A4 compatible
        height=840
    )
    
    if not coloring_image:
        print("❌ Coloring page generation FAILED!")
        return False
    
    # Save coloring page for inspection
    coloring_path = "COLORING_TEST.png"
    coloring_image.save(coloring_path)
    print(f"✅ Coloring page generated: {coloring_path}")
    print(f"   Should be: BLACK & WHITE lines only, no text")
    
    # Step 5: Create clean PDF
    print(f"\n📄 Step 5: Creating CLEAN PDF...")
    pdf_gen = NoTextPDFGenerator("sweet_spot_output")
    
    pdf_path = pdf_gen.generate_clean_pdf(
        story_title=story_data['title'],
        cover_image=cover_image,
        coloring_images=[coloring_image]
    )
    
    print(f"✅ Clean PDF created: {pdf_path}")
    
    # Step 6: Results summary
    print(f"\n🎉 SWEET SPOT TEST COMPLETED!")
    print(f"=" * 50)
    print(f"📁 Files created:")
    print(f"   🖼️  Cover: {cover_path} (should be COLORED)")
    print(f"   🎨 Coloring: {coloring_path} (should be B&W)")
    print(f"   📄 PDF: {pdf_path} (should have NO TEXT)")
    print(f"")
    print(f"🔍 CHECK THESE FILES:")
    print(f"   1. Cover should be colorful with title IN the image")
    print(f"   2. Coloring page should be black lines on white background")
    print(f"   3. PDF should have ZERO text added by the PDF generator")
    print(f"")
    print(f"🎯 If these look good, we found the sweet spot!")
    
    # Cleanup
    generator.cleanup_memory()
    return True

if __name__ == "__main__":
    success = find_sweet_spot()
    
    if success:
        print("\n✅ Sweet spot test completed!")
        print("Check the generated files to see if quality is good")
    else:
        print("\n❌ Sweet spot test failed!")
        print("Need to debug the image generation")