#!/usr/bin/env python3
"""
Test Pipeline Without AI Generation
Creates a sample coloring book using placeholder content to test the pipeline
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from improved_story_generator import ImprovedStoryGenerator
from no_text_pdf_generator import NoTextPDFGenerator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_cover(story_data, width=592, height=840):
    """Create a test cover with actual story content"""
    
    # Create a colorful cover
    cover = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(cover)
    
    # Add border
    border_width = 20
    draw.rectangle([border_width, border_width, width-border_width, height-border_width], 
                   outline='darkblue', width=8)
    
    # Add title area (simulating story integration)
    title_area_height = 150
    draw.rectangle([50, 50, width-50, title_area_height], 
                   fill='white', outline='darkblue', width=4)
    
    # Try to add title text
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        title = story_data['title'][:30] + ("..." if len(story_data['title']) > 30 else "")
        
        # Calculate text position
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = 80
        
        draw.text((x, y), title, fill='darkblue', font=font)
        
    except Exception as e:
        logger.warning(f"Could not load font: {e}")
        draw.text((60, 80), story_data['title'][:25], fill='darkblue')
    
    # Add main scene illustration area (representing where FLUX image would be)
    scene_y = title_area_height + 80
    scene_height = height - scene_y - 100
    draw.rectangle([80, scene_y, width-80, scene_y + scene_height], 
                   fill='lightgray', outline='darkblue', width=3)
    
    # Add sample illustration content based on story theme
    theme = story_data.get('theme', 'adventure')
    main_char = story_data.get('main_character', 'Character')
    
    # Center illustration area
    center_x = width // 2
    center_y = scene_y + scene_height // 2
    
    if 'dragon' in theme or 'dragon' in main_char.lower():
        # Draw a simple dragon-like shape
        draw.ellipse([center_x-60, center_y-30, center_x+60, center_y+30], 
                     fill='lightgreen', outline='darkgreen', width=3)
        draw.ellipse([center_x-20, center_y-10, center_x+20, center_y+10], 
                     fill='yellow', outline='orange', width=2)
        
    else:
        # Generic character representation
        draw.ellipse([center_x-50, center_y-40, center_x+50, center_y+40], 
                     fill='lightyellow', outline='orange', width=3)
    
    return cover

def create_test_coloring_page(scene_description, story_data, width=592, height=840):
    """Create a test coloring page with scene-appropriate content"""
    
    # Create white background
    coloring = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(coloring)
    
    # Add border
    border_width = 30
    draw.rectangle([border_width, border_width, width-border_width, height-border_width], 
                   outline='black', width=4)
    
    # Create scene elements based on description
    scene = scene_description.lower()
    
    # Main character area (center)
    char_x = width // 2
    char_y = height // 2
    
    # Character shape (simple representation)
    if 'dragon' in scene:
        # Dragon body
        draw.ellipse([char_x-80, char_y-40, char_x+80, char_y+40], 
                     outline='black', width=3)
        # Dragon head
        draw.ellipse([char_x+60, char_y-20, char_x+120, char_y+20], 
                     outline='black', width=3)
        # Wings
        draw.ellipse([char_x-60, char_y-80, char_x+20, char_y-20], 
                     outline='black', width=3)
        draw.ellipse([char_x+20, char_y-80, char_x+100, char_y-20], 
                     outline='black', width=3)
        
    elif 'cat' in scene or 'dog' in scene:
        # Pet body
        draw.ellipse([char_x-60, char_y-20, char_x+60, char_y+20], 
                     outline='black', width=3)
        # Head
        draw.ellipse([char_x-30, char_y-60, char_x+30, char_y-20], 
                     outline='black', width=3)
        # Ears
        draw.polygon([(char_x-25, char_y-60), (char_x-35, char_y-80), (char_x-15, char_y-75)], 
                     outline='black', width=2)
        draw.polygon([(char_x+15, char_y-75), (char_x+35, char_y-80), (char_x+25, char_y-60)], 
                     outline='black', width=2)
        
    else:
        # Generic character
        draw.ellipse([char_x-50, char_y-30, char_x+50, char_y+30], 
                     outline='black', width=3)
    
    # Add scene elements
    if 'forest' in scene or 'tree' in scene:
        # Trees
        draw.rectangle([100, height-200, 120, height-100], outline='black', width=2)  # Trunk
        draw.ellipse([80, height-250, 140, height-200], outline='black', width=2)     # Leaves
        
        draw.rectangle([width-120, height-180, width-100, height-100], outline='black', width=2)
        draw.ellipse([width-140, height-230, width-80, height-180], outline='black', width=2)
    
    if 'flower' in scene or 'garden' in scene:
        # Flowers
        for i in range(3):
            x = 150 + i * 100
            y = height - 150
            draw.ellipse([x-15, y-15, x+15, y+15], outline='black', width=2)
            draw.line([(x, y+15), (x, y+40)], fill='black', width=2)
    
    if 'mountain' in scene or 'cave' in scene:
        # Mountains
        draw.polygon([(50, height-100), (150, height-300), (250, height-100)], 
                     outline='black', width=3)
        draw.polygon([(width-250, height-100), (width-150, height-280), (width-50, height-100)], 
                     outline='black', width=3)
    
    if 'lake' in scene or 'water' in scene:
        # Water
        draw.ellipse([100, height-150, 300, height-120], outline='black', width=2)
    
    # Add some decorative elements
    if 'star' in scene or 'magic' in scene:
        # Stars
        star_points = [
            (100, 100), (105, 110), (115, 110), (107, 118),
            (110, 130), (100, 122), (90, 130), (93, 118),
            (85, 110), (95, 110)
        ]
        draw.polygon(star_points, outline='black', width=2)
    
    return coloring

def test_pipeline_no_ai():
    """Test the complete pipeline without AI generation"""
    
    print("🧪 TESTING PIPELINE WITHOUT AI")
    print("=" * 50)
    print("This creates a coloring book using test content instead of AI generation")
    print()
    
    # Step 1: Generate story data
    print("📖 Step 1: Generating story...")
    story_gen = ImprovedStoryGenerator()
    batch = story_gen.get_next_story_batch()
    
    story_data = batch['story_data']
    prompts = batch['prompts']
    
    print(f"✅ Story: {story_data['title']}")
    print(f"✅ Style: {story_data['art_style']['name']}")
    print(f"✅ Theme: {story_data.get('theme', 'N/A')}")
    print(f"✅ Main Character: {story_data.get('main_character', 'N/A')}")
    
    # Step 2: Create test images
    print("\n🎨 Step 2: Creating test images...")
    
    # Create cover
    print("   Creating test cover...")
    cover_image = create_test_cover(story_data)
    cover_path = "TEST_COVER.png"
    cover_image.save(cover_path)
    print(f"   ✅ Test cover saved: {cover_path}")
    
    # Create coloring pages (first 3 scenes)
    coloring_images = []
    for i, prompt in enumerate(prompts[1:4]):  # Skip cover, take first 3 coloring pages
        scene = prompt['scene_description']
        print(f"   Creating coloring page {i+1}: {scene[:50]}...")
        
        coloring_image = create_test_coloring_page(scene, story_data)
        coloring_path = f"TEST_COLORING_{i+1}.png"
        coloring_image.save(coloring_path)
        coloring_images.append(coloring_image)
        print(f"   ✅ Test coloring page {i+1} saved: {coloring_path}")
    
    # Step 3: Create PDF
    print("\n📄 Step 3: Creating PDF...")
    pdf_gen = NoTextPDFGenerator("test_no_ai_output")
    
    pdf_path = pdf_gen.generate_clean_pdf(
        story_title=f"TEST_{story_data['title']}",
        cover_image=cover_image,
        coloring_images=coloring_images
    )
    
    print(f"✅ Test PDF created: {pdf_path}")
    
    # Step 4: Results
    print(f"\n🎉 PIPELINE TEST COMPLETED!")
    print(f"=" * 50)
    print(f"📁 Files created:")
    print(f"   🖼️  Cover: {cover_path} (COLORED test cover)")
    print(f"   🎨 Coloring: TEST_COLORING_*.png (B&W test pages)")
    print(f"   📄 PDF: {pdf_path} (Complete test book)")
    print()
    print("🔍 This demonstrates the pipeline works!")
    print("   The issue is only with FLUX authentication")
    print("   Run setup_huggingface_auth.py to fix AI generation")
    
    return True

if __name__ == "__main__":
    success = test_pipeline_no_ai()
    
    if success:
        print("\n✅ Pipeline test successful!")
        print("Next step: Set up FLUX authentication")
    else:
        print("\n❌ Pipeline test failed!")
        print("Check the error messages above")