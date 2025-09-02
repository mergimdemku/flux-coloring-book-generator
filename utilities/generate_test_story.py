#!/usr/bin/env python3
"""
Generate a single test story to verify JSON structure and quality
"""

from book_author_agent import BookAuthorAgent
import json
from pathlib import Path

# Create the agent
agent = BookAuthorAgent()

# Generate one story
print("📚 Generating test story...")
story = agent.generate_creative_story()

# Save to a test file for inspection
test_file = Path("test_story_inspection.json")
with open(test_file, 'w', encoding='utf-8') as f:
    json.dump(story, f, indent=2, ensure_ascii=False)

print(f"✅ Story saved to: {test_file}")

# Also save to new_stories for processing
story_file = Path("new_stories") / f"test_story_{story['book']['title'].replace(' ', '_')}.json"
with open(story_file, 'w', encoding='utf-8') as f:
    json.dump(story, f, indent=2, ensure_ascii=False)

print(f"✅ Also saved to: {story_file}")

# Display key information
book = story['book']
print("\n" + "="*50)
print("📖 STORY DETAILS:")
print(f"Title: {book['title']}")
print(f"Age Range: {book['age_range']}")
print(f"Pages: {len(book['pages'])} coloring pages")
print(f"\n🎨 Style prompt:")
print(f"{book['style'][:150]}...")
print(f"\n❌ Negative prompt:")
print(f"{book['negative'][:150]}...")
print(f"\n🖼️ Cover prompt:")
print(f"{book['cover_prompt'][:150]}...")
print(f"\n📄 First page scene:")
print(f"{book['pages'][0]['scene'][:150]}...")

print("\n" + "="*50)
print("✅ Story generated successfully!")
print("Check test_story_inspection.json for full details")