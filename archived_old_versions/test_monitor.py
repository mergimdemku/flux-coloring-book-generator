#!/usr/bin/env python3
"""
Test the monitoring system without actual image generation
"""

import json
from pathlib import Path
from automated_monitor_pipeline import AutomatedMonitorPipeline

# Create a test pipeline
pipeline = AutomatedMonitorPipeline()

# Check for stories
story_file = pipeline.check_new_stories()

if story_file:
    print(f"✅ Found story: {story_file}")
    
    # Load and validate
    story_data = pipeline.load_story_file(story_file)
    
    if story_data:
        print(f"✅ Loaded successfully")
        print(f"   Title: {story_data['story'].get('title', 'Unknown')}")
        print(f"   Prompts: {len(story_data['prompts'])} total")
        print(f"   Style: JSON-style" if story_data.get('json_style') else "Old style")
        
        # Show first prompt
        if story_data['prompts']:
            first = story_data['prompts'][0]
            print(f"\n📖 Cover prompt:")
            print(f"   {first['prompt'][:150]}...")
            print(f"\n❌ Negative prompt:")
            print(f"   {first.get('negative', 'None')[:100]}...")
    else:
        print("❌ Failed to load story")
else:
    print("❌ No stories found in new_stories folder")