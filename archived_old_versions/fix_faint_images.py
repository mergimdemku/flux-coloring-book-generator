#!/usr/bin/env python3
"""
Fix Faint Images - Handle very light FLUX output
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging

def enhance_faint_image(image):
    """Enhance very faint/light images before processing"""
    
    # Convert to numpy array
    img_array = np.array(image)
    
    # Convert to grayscale
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    print(f"🔍 Analyzing image brightness...")
    
    # Analyze the image
    mean_brightness = np.mean(gray)
    std_brightness = np.std(gray)
    dark_pixels = np.sum(gray < 128) / gray.size
    very_dark_pixels = np.sum(gray < 64) / gray.size
    
    print(f"   Mean brightness: {mean_brightness:.1f}/255")
    print(f"   Brightness std: {std_brightness:.1f}")
    print(f"   Dark pixels: {dark_pixels:.1%}")
    print(f"   Very dark pixels: {very_dark_pixels:.1%}")
    
    if mean_brightness > 240 and dark_pixels < 0.05:
        print("⚠️  Image appears very faint/light!")
        print("   Applying faint image enhancement...")
        
        # Enhance contrast dramatically
        pil_gray = Image.fromarray(gray)
        enhancer = ImageEnhance.Contrast(pil_gray)
        enhanced = enhancer.enhance(5.0)  # Very high contrast
        
        # Convert back to array
        enhanced_array = np.array(enhanced)
        
        # Apply histogram equalization
        enhanced_array = cv2.equalizeHist(enhanced_array)
        
        # Save enhanced version for inspection
        enhanced_pil = Image.fromarray(enhanced_array)
        enhanced_pil.save("enhanced_input.png")
        print("   ✅ Saved enhanced input as 'enhanced_input.png'")
        
        return enhanced_array
    
    elif mean_brightness > 200 and dark_pixels < 0.1:
        print("⚠️  Image appears light - applying moderate enhancement...")
        
        # Moderate enhancement
        pil_gray = Image.fromarray(gray)
        enhancer = ImageEnhance.Contrast(pil_gray)
        enhanced = enhancer.enhance(2.5)
        enhanced_array = np.array(enhanced)
        
        enhanced_pil = Image.fromarray(enhanced_array)
        enhanced_pil.save("enhanced_input.png")
        print("   ✅ Saved enhanced input as 'enhanced_input.png'")
        
        return enhanced_array
    
    else:
        print("   ✅ Image has reasonable contrast")
        return gray

def process_coloring_page_smart(image, style_name='Manga'):
    """Smart coloring page processing that adapts to image brightness"""
    
    print(f"🎨 SMART coloring page processing for {style_name}")
    
    # Step 1: Enhance faint images
    gray = enhance_faint_image(image)
    
    # Step 2: Determine best threshold method based on content
    mean_val = np.mean(gray)
    
    if mean_val > 200:  # Very bright image
        print("   Using aggressive thresholding for bright image...")
        # Use Otsu's method for automatic threshold
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif mean_val > 150:  # Moderately bright
        print("   Using standard adaptive thresholding...")
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 15)
    else:  # Already dark enough
        print("   Using gentle thresholding...")
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 7)
    
    # Save intermediate result
    binary_pil = Image.fromarray(binary)
    binary_pil.save("binary_result.png")
    print("   ✅ Saved binary result as 'binary_result.png'")
    
    # Step 3: Check if we have content
    content_ratio = np.sum(binary == 0) / binary.size
    print(f"   📊 Content ratio after thresholding: {content_ratio:.3f}")
    
    if content_ratio < 0.01:
        print("   ⚠️  Very little content - trying alternative methods...")
        
        # Try different approaches
        for method_name, method in [
            ("Global Otsu", lambda: cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
            ("Fixed threshold 200", lambda: cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)[1]),
            ("Fixed threshold 150", lambda: cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]),
            ("Adaptive Gaussian", lambda: cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 20)),
        ]:
            try:
                test_binary = method()
                test_content = np.sum(test_binary == 0) / test_binary.size
                print(f"      {method_name}: {test_content:.3f} content ratio")
                
                if test_content > content_ratio and test_content > 0.02:
                    print(f"      ✅ Better method found: {method_name}")
                    binary = test_binary
                    content_ratio = test_content
                    break
            except Exception as e:
                print(f"      ❌ {method_name} failed: {e}")
    
    if content_ratio < 0.01:
        print("   ❌ Could not extract meaningful content from image!")
        return None
    
    # Step 4: Minimal cleanup (only if we have enough content)
    if content_ratio > 0.05:  # Only clean up if we have substantial content
        print("   Applying minimal cleanup...")
        
        # Light denoising
        binary = cv2.medianBlur(binary, 3)
        
        # Connect very close line breaks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
    else:
        print("   Skipping cleanup to preserve content...")
    
    # Convert to RGB
    result = Image.fromarray(binary)
    result = result.convert('RGB')
    
    # Light contrast enhancement
    enhancer = ImageEnhance.Contrast(result)
    result = enhancer.enhance(1.2)
    
    print("   ✅ Smart processing complete")
    return result

def test_with_faint_image():
    """Test with a very faint image like FLUX might produce"""
    
    print("🧪 Testing with faint image (simulating FLUX output)")
    
    # Create a faint test image (like FLUX might produce)
    test_image = Image.new('RGB', (400, 400), 'white')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(test_image)
    
    # Add very faint details (simulating FLUX coloring page output)
    light_gray = (220, 220, 220)  # Very light gray
    medium_gray = (180, 180, 180)  # Medium light gray
    
    # Character outline (very faint)
    draw.ellipse([100, 50, 200, 150], outline=light_gray, width=2)  # Head
    draw.ellipse([125, 150, 175, 200], outline=light_gray, width=2)  # Body
    draw.line([(150, 200), (130, 250)], fill=medium_gray, width=2)   # Left leg
    draw.line([(150, 200), (170, 250)], fill=medium_gray, width=2)   # Right leg
    draw.line([(125, 170), (100, 190)], fill=light_gray, width=2)    # Left arm
    draw.line([(175, 170), (200, 190)], fill=light_gray, width=2)    # Right arm
    
    # Scene elements (even fainter)
    draw.ellipse([250, 300, 350, 350], outline=light_gray, width=1)   # Sun
    draw.line([(50, 350), (350, 350)], fill=medium_gray, width=2)     # Ground
    
    test_image.save("faint_test_input.png")
    print("✅ Created faint test image")
    
    # Process it
    result = process_coloring_page_smart(test_image)
    
    if result:
        result.save("faint_test_output.png")
        print("✅ Processed faint image successfully")
        
        # Check final content
        result_array = np.array(result.convert('L'))
        final_content = np.sum(result_array < 128) / result_array.size
        print(f"📊 Final content ratio: {final_content:.3f}")
        
        return final_content > 0.02  # At least 2% content
    else:
        print("❌ Failed to process faint image")
        return False

if __name__ == "__main__":
    success = test_with_faint_image()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Faint image processing test")
    
    if success:
        print("\nFiles created:")
        print("  • faint_test_input.png - Simulated faint FLUX output")
        print("  • enhanced_input.png - After enhancement")
        print("  • binary_result.png - After thresholding") 
        print("  • faint_test_output.png - Final result")
        print("\nThis approach should work with faint FLUX output!")