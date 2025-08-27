#!/usr/bin/env python3
"""
SIMPLE TEST: Generate 1 cover + 1 coloring page to debug issues
"""

import logging
from pathlib import Path
from improved_story_generator import ImprovedStoryGenerator
from clean_line_flux_generator import CleanLineFluxGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_single_generation():
    """Test generating just 1 cover + 1 coloring page"""
    
    print("🧪 SIMPLE TEST: 1 Cover + 1 Coloring Page")
    print("=" * 50)
    
    # Step 1: Generate story
    print("\n📖 Step 1: Generating story...")
    story_gen = ImprovedStoryGenerator()
    batch = story_gen.get_next_story_batch()
    
    story_data = batch['story_data']
    prompts = batch['prompts']
    
    print(f"✅ Story: {story_data['title']}")
    print(f"✅ Style: {story_data['art_style']['name']}")
    print(f"✅ Total prompts: {len(prompts)}")
    
    # Take only cover + first coloring page
    cover_prompt = prompts[0]  # Cover
    coloring_prompt = prompts[1]  # First coloring page
    
    print(f"\n🎨 Cover prompt (first 100 chars):")
    print(f"   {cover_prompt['prompt'][:100]}...")
    
    print(f"\n🖍️  Coloring prompt (first 100 chars):")
    print(f"   {coloring_prompt['prompt'][:100]}...")
    
    # Step 2: Initialize FLUX generator
    print(f"\n⚡ Step 2: Loading FLUX generator...")
    generator = CleanLineFluxGenerator()
    
    if not generator.load_model():
        print("❌ FLUX model loading failed!")
        return False
    
    print("✅ FLUX model loaded")
    
    # Step 3: Generate cover
    print(f"\n🖼️  Step 3: Generating COVER...")
    print(f"Prompt type: {cover_prompt['type']}")
    
    cover_image = generator.generate_perfect_cover(
        prompt_data=cover_prompt,
        story_data=story_data,
        width=400,  # Smaller for testing
        height=600
    )
    
    if cover_image:
        cover_path = "test_cover.png"
        cover_image.save(cover_path)
        print(f"✅ Cover saved: {cover_path}")
    else:
        print("❌ Cover generation failed!")
        return False
    
    # Step 4: Generate coloring page
    print(f"\n🎨 Step 4: Generating COLORING PAGE...")
    print(f"Prompt type: {coloring_prompt['type']}")
    
    coloring_image = generator.generate_ultra_clean_coloring_page(
        prompt_data=coloring_prompt,
        story_data=story_data,
        width=400,  # Smaller for testing
        height=600
    )
    
    if coloring_image:
        coloring_path = "test_coloring.png"
        coloring_image.save(coloring_path)
        print(f"✅ Coloring page saved: {coloring_path}")
    else:
        print("❌ Coloring page generation failed!")
        return False
    
    # Step 5: Check the results
    print(f"\n🔍 Step 5: RESULTS CHECK")
    print(f"✅ Cover image: {cover_path} (should be COLORED)")
    print(f"✅ Coloring page: {coloring_path} (should be BLACK & WHITE)")
    
    print(f"\n📊 GENERATION SUCCESS!")
    print(f"Now check the images manually to see quality")
    
    # Cleanup
    generator.cleanup_memory()
    return True

def debug_prompts():
    """Debug the actual prompts being generated"""
    
    print("\n🔍 DEBUGGING PROMPTS")
    print("=" * 30)
    
    story_gen = ImprovedStoryGenerator()
    batch = story_gen.get_next_story_batch()
    
    story_data = batch['story_data']
    prompts = batch['prompts']
    
    cover_prompt = prompts[0]
    coloring_prompt = prompts[1]
    
    print(f"\n📋 COVER PROMPT:")
    print(f"Type: {cover_prompt['type']}")
    print(f"Full prompt: {cover_prompt['prompt']}")
    
    print(f"\n📋 COLORING PROMPT:")
    print(f"Type: {coloring_prompt['type']}")
    print(f"Full prompt: {coloring_prompt['prompt']}")
    
    # Test the clean line generator prompt building
    generator = CleanLineFluxGenerator()
    
    print(f"\n🔧 FLUX GENERATOR PROCESSED PROMPTS:")
    
    enhanced_cover = generator.build_ultra_clean_prompt(
        base_prompt=cover_prompt['prompt'],
        style_name=story_data['art_style']['name'],
        prompt_type='cover'
    )
    
    enhanced_coloring = generator.build_ultra_clean_prompt(
        base_prompt=coloring_prompt['prompt'],
        style_name=story_data['art_style']['name'],
        prompt_type='coloring_page'
    )
    
    negative_cover = generator.build_ultra_clean_negative_prompt(
        style_name=story_data['art_style']['name'],
        prompt_type='cover'
    )
    
    negative_coloring = generator.build_ultra_clean_negative_prompt(
        style_name=story_data['art_style']['name'],
        prompt_type='coloring_page'
    )
    
    print(f"\n✨ ENHANCED COVER PROMPT:")
    print(enhanced_cover)
    
    print(f"\n✨ ENHANCED COLORING PROMPT:")
    print(enhanced_coloring)
    
    print(f"\n❌ COVER NEGATIVE PROMPT:")
    print(negative_cover[:200] + "...")
    
    print(f"\n❌ COLORING NEGATIVE PROMPT:")
    print(negative_coloring[:200] + "...")

if __name__ == "__main__":
    print("🚀 SIMPLE FLUX TEST - DEBUG MODE")
    print("=" * 50)
    
    # First debug prompts
    debug_prompts()
    
    print("\n" + "=" * 50)
    print("Run actual generation? (this will be slow)")
    print("If you want to test generation, run: python simple_test_generation.py --generate")
    
    import sys
    if "--generate" in sys.argv:
        success = test_single_generation()
        if success:
            print("✅ Test completed successfully!")
        else:
            print("❌ Test failed")