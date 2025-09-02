#!/usr/bin/env python3
"""
Demo the Book-Author Agent - Generate 5 different story types
"""

from book_author_agent import BookAuthorAgent
import time

def demo_variety():
    """Generate 5 stories to show the variety"""
    
    print("🎨 BOOK-AUTHOR AGENT DEMO")
    print("=" * 50)
    print("Generating 5 different story types to show variety:\n")
    
    author = BookAuthorAgent()
    
    stories_generated = []
    
    for i in range(5):
        print(f"📚 Generating story {i+1}/5...")
        
        # Generate story
        story = author.generate_creative_story()
        
        # Save it
        filepath = author.save_story(story)
        stories_generated.append(story)
        
        # Show what was created
        book = story['book']
        metadata = book['metadata']
        
        print(f"   ✅ Title: {book['title']}")
        print(f"   🎭 Type: {metadata['story_type']} - {metadata['theme']}")
        print(f"   👤 Character: {metadata['character_type']}")
        print(f"   🏞️  Setting: {metadata['setting_type']}")
        print(f"   📄 Pages: {len(book['pages'])}")
        print(f"   💾 File: {filepath.split('/')[-1]}")
        print()
    
    print("🎉 DEMO COMPLETE!")
    print(f"Generated {len(stories_generated)} different stories showing variety:")
    print()
    
    # Show summary of variety
    story_types = set()
    themes = set() 
    character_types = set()
    
    for story in stories_generated:
        meta = story['book']['metadata']
        story_types.add(meta['story_type'])
        themes.add(meta['theme'])
        character_types.add(meta['character_type'])
    
    print(f"📊 VARIETY ACHIEVED:")
    print(f"   Story Types: {len(story_types)} different ({', '.join(story_types)})")
    print(f"   Themes: {len(themes)} different ({', '.join(themes)})")
    print(f"   Character Types: {len(character_types)} different ({', '.join(character_types)})")
    print()
    print("🤖 This shows the AI creativity of the Book-Author Agent!")
    print("💡 Run 'python book_author_agent.py' for continuous generation")

if __name__ == "__main__":
    demo_variety()