#!/usr/bin/env python3
"""
Test Fixed Processing - Verify the faint image fix works
"""

from PIL import Image, ImageDraw
from clean_line_flux_generator import CleanLineFluxGenerator
import numpy as np

def test_fixed_processing():
    """Test that the fixed processing preserves faint content"""
    
    print("🧪 Testing Fixed Line Processing")
    print("=" * 40)
    
    # Create a faint test image (simulating FLUX output)
    test_image = Image.new('RGB', (400, 400), 'white')
    draw = ImageDraw.Draw(test_image)
    
    # Add very faint content (like FLUX might produce)
    light_gray = (220, 220, 220)
    medium_gray = (180, 180, 180)
    
    # Character
    draw.ellipse([150, 50, 250, 150], outline=light_gray, width=2)    # Head
    draw.ellipse([175, 150, 225, 200], outline=light_gray, width=2)   # Body
    draw.line([(200, 200), (180, 250)], fill=medium_gray, width=2)    # Left leg
    draw.line([(200, 200), (220, 250)], fill=medium_gray, width=2)    # Right leg
    
    # Scene
    draw.rectangle([50, 300, 350, 350], outline=medium_gray, width=2)  # Ground
    draw.ellipse([300, 80, 350, 130], outline=light_gray, width=1)     # Sun
    
    test_image.save("test_faint_input.png")
    print("✅ Created faint test image")
    
    # Analyze original
    img_array = np.array(test_image.convert('L'))
    original_dark_pixels = np.sum(img_array < 200) / img_array.size
    print(f"📊 Original image: {original_dark_pixels:.3f} dark pixel ratio")
    
    # Test with fixed processing
    generator = CleanLineFluxGenerator()
    
    try:
        result = generator.apply_ultra_clean_line_processing(test_image, "Manga")
        
        if result:
            result.save("test_fixed_output.png")
            print("✅ Processing completed successfully")
            
            # Analyze result
            result_array = np.array(result.convert('L'))
            final_dark_pixels = np.sum(result_array < 128) / result_array.size
            print(f"📊 Final image: {final_dark_pixels:.3f} dark pixel ratio")
            
            if final_dark_pixels > 0.01:  # At least 1% content
                print("✅ SUCCESS: Fixed processing preserved content!")
                return True
            else:
                print("❌ FAILED: Still losing too much content")
                return False
        else:
            print("❌ FAILED: Processing returned None")
            return False
            
    except Exception as e:
        print(f"❌ FAILED: Processing threw exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_fixed_processing()
    
    if success:
        print(f"\n🎉 FIXED! The line processing now handles faint images correctly.")
        print(f"Files created:")
        print(f"  • test_faint_input.png - Simulated faint FLUX output")
        print(f"  • test_fixed_output.png - Processed result with content preserved")
        print(f"\nYou can now run: python find_sweet_spot.py")
    else:
        print(f"\n❌ Fix didn't work. Need further debugging.")
        print(f"Check the generated files to see what happened.")