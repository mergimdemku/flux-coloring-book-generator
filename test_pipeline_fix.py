#!/usr/bin/env python3
"""
Test script to verify the pipeline fix works
"""

import logging
import sys
from pathlib import Path
from automated_monitor_pipeline import AutomatedMonitorPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pipeline_initialization():
    """Test that the pipeline can initialize properly with FLUX model"""
    
    print("🧪 Testing Pipeline Initialization Fix...")
    
    try:
        # This should now work without the 'pipe' attribute error
        pipeline = AutomatedMonitorPipeline()
        
        print("✅ Pipeline initialized successfully!")
        print(f"✅ FLUX generator loaded: {pipeline.flux_generator is not None}")
        print(f"✅ PDF generator loaded: {pipeline.pdf_generator is not None}")
        
        # Check if there are stories to process
        new_stories_dir = Path("new_stories")
        json_files = list(new_stories_dir.glob("*.json"))
        
        if json_files:
            print(f"📚 Found {len(json_files)} stories ready for processing:")
            for file in json_files[:3]:  # Show first 3
                print(f"  - {file.name}")
            if len(json_files) > 3:
                print(f"  ... and {len(json_files) - 3} more")
        else:
            print("📭 No stories found in new_stories directory")
        
        print("\n🎉 Pipeline initialization test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline initialization test FAILED: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_single_story_processing():
    """Test processing a single story"""
    
    print("\n🧪 Testing Single Story Processing...")
    
    try:
        pipeline = AutomatedMonitorPipeline()
        
        # Find a story to test
        story_file = pipeline.check_new_stories()
        
        if not story_file:
            print("📭 No stories found to test")
            return True
        
        print(f"📖 Testing with: {story_file.name}")
        
        # Load the story data (don't process fully to avoid long generation)
        story_data = pipeline.load_story_file(story_file)
        
        if story_data:
            print("✅ Story loaded successfully")
            story_info = story_data.get('story', {})
            prompts = story_data.get('prompts', [])
            print(f"✅ Found {len(prompts)} prompts to generate")
            print(f"✅ Story title: {story_info.get('title', 'Unknown')}")
        else:
            print("❌ Failed to load story")
            return False
        
        print("✅ Single story processing test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Single story processing test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing Pipeline Fixes")
    print("=" * 50)
    
    # Test 1: Pipeline initialization
    test1_passed = test_pipeline_initialization()
    
    if test1_passed:
        # Test 2: Story processing (if initialization worked)
        test2_passed = test_single_story_processing()
    else:
        test2_passed = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"  Pipeline Initialization: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"  Story Processing: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The fix is working correctly.")
        print("\nYou can now run:")
        print("  python automated_monitor_pipeline.py")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        sys.exit(1)