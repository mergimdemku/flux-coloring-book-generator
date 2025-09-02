#!/usr/bin/env python3
"""
Generate a JSON-style story and save to new_stories folder
"""

import sys
import json
import time
import random
from pathlib import Path
from json_style_story_generator import JsonStyleStoryGenerator

def generate_story_to_queue():
    """Generate a story and add to new_stories queue"""
    
    generator = JsonStyleStoryGenerator()
    
    # Generate story
    story = generator.generate_story()
    
    # Save to new_stories folder
    timestamp = int(time.time())
    filename = f"story_{story['book']['title'].replace(' ', '_')}_{timestamp}.json"
    filepath = Path("new_stories") / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(story, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated: {story['book']['title']}")
    print(f"📁 Saved to: {filepath}")
    print(f"📖 Pages: {len(story['book']['pages'])}")
    print(f"\n🎨 Cover prompt preview:")
    print(f"   {story['book']['cover_prompt'][:100]}...")
    print(f"\n🖍️  First scene:")
    print(f"   {story['book']['pages'][0]['scene'][:100]}...")
    
    return filepath

def generate_batch(count: int = 5):
    """Generate multiple stories at once"""
    print(f"🎨 Generating {count} JSON-style stories...\n")
    
    generated = []
    for i in range(count):
        print(f"Story {i+1}/{count}:")
        filepath = generate_story_to_queue()
        generated.append(filepath)
        print("-" * 60)
    
    print(f"\n✅ Generated {len(generated)} stories in new_stories folder")
    print("📌 The automated pipeline will process them automatically!")
    
    return generated

if __name__ == "__main__":
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
        generate_batch(count)
    else:
        # Generate single story
        generate_story_to_queue()
        print("\n💡 Tip: Use 'python generate_json_story.py 5' to generate 5 stories at once")