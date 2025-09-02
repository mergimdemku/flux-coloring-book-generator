#!/usr/bin/env python3
"""
Fix Line Processing - Apply gentler processing to preserve content
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging

def apply_gentle_line_processing(image, style_name='Manga'):
    """Apply gentler line processing that preserves content"""
    
    # Convert to numpy array
    img_array = np.array(image)
    
    # Convert to grayscale
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    print(f"🎨 Applying GENTLE line processing for {style_name}")
    
    # Step 1: Light denoising (less aggressive)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)  # Reduced from 15, 100, 100
    
    # Step 2: Adaptive threshold (more permissive)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 7)  # Increased from 3, 3
    
    # Step 3: Only connect obvious broken lines (reduced iterations)
    kernel_connect = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))  # Smaller kernel
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_connect, iterations=1)  # Reduced iterations
    
    # Step 4: Very light line thickening
    kernel_thick = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))  # Minimal thickening
    edges = cv2.dilate(edges, kernel_thick, iterations=1)
    
    # Step 5: Skip aggressive cleanup steps that remove content
    # NO median blur
    # NO morphological opening (this removes small content)
    # Just ensure binary
    _, edges = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)
    
    # Convert back to PIL Image
    result = Image.fromarray(edges)
    result = result.convert('RGB')
    
    # Step 6: Light contrast enhancement only
    enhancer = ImageEnhance.Contrast(result)
    result = enhancer.enhance(1.5)  # Reduced from 3.0
    
    # Skip aggressive sharpening and filtering
    
    print("✅ Gentle processing complete")
    return result

def test_gentle_processing():
    """Create a test that shows the difference"""
    
    print("🧪 Testing gentle vs aggressive processing")
    
    # Create a test image with fine details
    test_image = Image.new('RGB', (400, 400), 'white')
    from PIL import ImageDraw
    draw = ImageDraw.Draw(test_image)
    
    # Add some fine lines and details
    draw.ellipse([50, 50, 150, 150], outline='gray', width=1)  # Light circle
    draw.line([(200, 50), (350, 150)], fill='lightgray', width=2)  # Light line
    draw.rectangle([100, 200, 300, 300], outline='darkgray', width=1)  # Light rectangle
    draw.text((150, 350), "Test", fill='gray')  # Light text
    
    test_image.save("test_input.png")
    print("✅ Created test input image")
    
    # Apply gentle processing
    result = apply_gentle_line_processing(test_image)
    result.save("test_gentle_output.png")
    print("✅ Applied gentle processing")
    
    # Check content
    result_array = np.array(result.convert('L'))
    content_ratio = np.sum(result_array < 128) / (result_array.shape[0] * result_array.shape[1])
    print(f"📊 Final content ratio: {content_ratio:.3f}")
    
    if content_ratio > 0.01:
        print("✅ Gentle processing preserved content!")
        return True
    else:
        print("❌ Even gentle processing lost too much content")
        return False

if __name__ == "__main__":
    success = test_gentle_processing()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: Gentle processing test")