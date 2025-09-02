#!/usr/bin/env python3
"""
Test the complete automated pipeline
"""

import time
import logging
from pathlib import Path

from kids_story_generator import KidsStoryGenerator
from enhanced_flux_generator import EnhancedFluxGenerator  
from enhanced_pdf_generator import EnhancedPDFGenerator
from automated_coloring_book_pipeline import AutomatedColoringBookPipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_individual_components():
    """Test each component individually"""
    
    print("🧪 Testing Individual Components")
    print("=" * 40)
    
    # Test 1: Story Generator
    print("\n1️⃣ Testing Story Generator...")
    try:
        story_gen = KidsStoryGenerator()
        batch = story_gen.get_next_story_batch()
        
        print(f"✅ Story: {batch['story_data']['title']}")
        print(f"✅ Style: {batch['story_data']['art_style']['name']}")
        print(f"✅ Prompts: {len(batch['prompts'])}")
        
    except Exception as e:
        print(f"❌ Story Generator failed: {e}")
        return False
    
    # Test 2: Enhanced FLUX Generator
    print("\n2️⃣ Testing Enhanced FLUX Generator...")
    try:
        flux_gen = EnhancedFluxGenerator()
        
        if not flux_gen.load_model():
            print("❌ FLUX model loading failed")
            return False
        
        print("✅ FLUX model loaded")
        
        # Test single image generation
        test_prompt = {
            'type': 'coloring_page',
            'prompt': 'cute dragon playing in a garden'
        }
        
        test_story = {
            'id': 'test_001',
            'main_character': 'Alex',
            'companion': 'Dragon',
            'art_style': {'name': 'Cartoon'}
        }
        
        image = flux_gen.generate_with_enhanced_prompts(
            prompt_data=test_prompt,
            story_data=test_story,
            width=400,
            height=400
        )
        
        if image:
            image.save("test_flux_output.png")
            print("✅ FLUX generation successful")
            print("📁 Saved: test_flux_output.png")
        else:
            print("❌ FLUX generation failed")
            return False
        
    except Exception as e:
        print(f"❌ FLUX Generator failed: {e}")
        return False
    
    # Test 3: PDF Generator
    print("\n3️⃣ Testing PDF Generator...")
    try:
        pdf_gen = EnhancedPDFGenerator("test_output")
        
        # Use the generated story and create test images
        from PIL import Image
        
        test_cover = Image.new('RGB', (400, 600), color='lightblue')
        test_pages = [Image.new('RGB', (400, 600), color='white') for _ in range(3)]
        
        test_prompts = [
            {'type': 'cover', 'scene_description': 'Test cover'},
            {'type': 'coloring_page', 'scene_description': 'Test page 1'},
            {'type': 'coloring_page', 'scene_description': 'Test page 2'},
            {'type': 'coloring_page', 'scene_description': 'Test page 3'}
        ]
        
        pdf_path = pdf_gen.generate_complete_book_pdf(
            story_data=batch['story_data'],
            cover_image=test_cover,
            coloring_images=test_pages,
            prompts_data=test_prompts
        )
        
        print(f"✅ PDF generation successful")
        print(f"📁 Saved: {pdf_path}")
        
    except Exception as e:
        print(f"❌ PDF Generator failed: {e}")
        return False
    
    print("\n🎉 All individual components working!")
    return True

def test_integrated_pipeline():
    """Test the complete integrated pipeline"""
    
    print("\n🔧 Testing Integrated Pipeline")
    print("=" * 40)
    
    try:
        # Initialize pipeline
        pipeline = AutomatedColoringBookPipeline("test_pipeline_output")
        
        # Initialize components
        if not pipeline.initialize_components():
            print("❌ Pipeline initialization failed")
            return False
        
        print("✅ Pipeline initialized")
        
        # Test single book generation
        print("\n📖 Testing single book generation...")
        
        success = pipeline.process_single_book()
        
        if success:
            print("✅ Complete book generation successful!")
            
            # Show stats
            status = pipeline.get_status()
            print(f"📊 Stories: {status['stats']['stories_generated']}")
            print(f"🎨 Images: {status['stats']['images_generated']}")
            print(f"📄 PDFs: {status['stats']['pdfs_created']}")
            print(f"⚠️  Errors: {status['stats']['errors']}")
            
        else:
            print("❌ Complete book generation failed")
            return False
        
        # Cleanup
        pipeline.stop_pipeline()
        
    except Exception as e:
        print(f"❌ Integrated pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 Integrated pipeline test successful!")
    return True

def main():
    """Run complete pipeline test"""
    
    print("🎨 COMPLETE PIPELINE TEST")
    print("=" * 50)
    print()
    
    start_time = time.time()
    
    # Test individual components first
    if not test_individual_components():
        print("\n❌ Individual component tests failed")
        return
    
    # Test integrated pipeline
    if not test_integrated_pipeline():
        print("\n❌ Integrated pipeline test failed")
        return
    
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 50)
    print(f"⏱️  Total test time: {elapsed:.1f} seconds")
    print()
    print("🚀 Ready for production!")
    print("   Run: start_automated_pipeline.bat")
    print()
    print("📁 Test outputs:")
    print("   - test_flux_output.png")
    print("   - test_output/ (PDF files)")
    print("   - test_pipeline_output/ (Complete books)")

if __name__ == "__main__":
    main()