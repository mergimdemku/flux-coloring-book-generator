#!/usr/bin/env python3
"""
Debug Line Processing - Find where content is being lost
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_line_processing(input_image_path, output_dir="debug_processing"):
    """Debug line processing step by step to find where content is lost"""
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"🔍 DEBUG LINE PROCESSING")
    print(f"Input: {input_image_path}")
    print(f"Output dir: {output_dir}")
    print("=" * 50)
    
    # Load image
    try:
        if isinstance(input_image_path, str):
            image = Image.open(input_image_path)
        else:
            image = input_image_path
            
        # Save original
        image.save(output_dir / "0_original.png")
        print("✅ Step 0: Saved original")
        
    except Exception as e:
        print(f"❌ Could not load input image: {e}")
        return None
    
    # Convert to numpy array
    img_array = np.array(image)
    
    # Convert to grayscale
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # Save grayscale
    gray_pil = Image.fromarray(gray)
    gray_pil.save(output_dir / "1_grayscale.png")
    print("✅ Step 1: Converted to grayscale")
    
    # PRE-PROCESSING: Denoising
    gray_denoised = cv2.bilateralFilter(gray, 15, 100, 100)
    denoised_pil = Image.fromarray(gray_denoised)
    denoised_pil.save(output_dir / "2_denoised.png")
    print("✅ Step 2: Applied denoising")
    
    # MANGA PROCESSING (as used in the log)
    edges = cv2.adaptiveThreshold(gray_denoised, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 3)
    edges_pil = Image.fromarray(edges)
    edges_pil.save(output_dir / "3_adaptive_threshold.png")
    print("✅ Step 3: Applied adaptive threshold")
    
    # Check if we lost content here
    white_pixels = np.sum(edges == 255)
    black_pixels = np.sum(edges == 0)
    total_pixels = edges.shape[0] * edges.shape[1]
    content_ratio = black_pixels / total_pixels
    print(f"   📊 Content ratio after threshold: {content_ratio:.3f} ({black_pixels} black pixels)")
    
    if content_ratio < 0.01:  # Less than 1% content
        print("⚠️  WARNING: Very little content after adaptive threshold!")
        print("   This might indicate the original image was too light/faint")
        
        # Try different threshold values
        for thresh_val in [5, 7, 9, 11]:
            test_edges = cv2.adaptiveThreshold(gray_denoised, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, thresh_val, thresh_val)
            test_content = np.sum(test_edges == 0) / total_pixels
            test_pil = Image.fromarray(test_edges)
            test_pil.save(output_dir / f"3b_threshold_{thresh_val}.png")
            print(f"   📊 Threshold {thresh_val}: content ratio {test_content:.3f}")
            
            if test_content > 0.05:  # More than 5% content
                print(f"   ✅ Better threshold found: {thresh_val}")
                edges = test_edges
                break
    
    # Stage 1: Connect broken lines
    kernel_connect = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_connect, iterations=2)
    edges_pil = Image.fromarray(edges)
    edges_pil.save(output_dir / "4_line_connect.png")
    print("✅ Step 4: Connected broken lines")
    
    # Stage 2: Thicken lines
    kernel_thick = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    edges = cv2.dilate(edges, kernel_thick, iterations=1)
    edges_pil = Image.fromarray(edges)
    edges_pil.save(output_dir / "5_thicken_lines.png")
    print("✅ Step 5: Thickened lines")
    
    # AGGRESSIVE PROCESSING (this is where content might be lost)
    
    # Stage 1: Median blur
    edges = cv2.medianBlur(edges, 3)
    edges_pil = Image.fromarray(edges)
    edges_pil.save(output_dir / "6_median_blur.png")
    print("✅ Step 6: Applied median blur")
    
    # Stage 2: Connect nearby segments
    kernel_connect_final = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_connect_final, iterations=3)
    edges_pil = Image.fromarray(edges)
    edges_pil.save(output_dir / "7_connect_segments.png")
    print("✅ Step 7: Connected nearby segments")
    
    # Stage 3: Remove tiny artifacts (THIS IS THE DANGEROUS STEP)
    kernel_clean = np.ones((3, 3), np.uint8)
    edges_before_clean = edges.copy()
    edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, kernel_clean, iterations=1)
    edges_pil = Image.fromarray(edges)
    edges_pil.save(output_dir / "8_remove_artifacts.png")
    
    # Check content loss
    content_before = np.sum(edges_before_clean == 0) / total_pixels
    content_after = np.sum(edges == 0) / total_pixels
    content_loss = (content_before - content_after) / content_before if content_before > 0 else 0
    
    print(f"✅ Step 8: Removed tiny artifacts")
    print(f"   📊 Content before: {content_before:.3f}, after: {content_after:.3f}")
    print(f"   📊 Content loss: {content_loss:.1%}")
    
    if content_loss > 0.8:  # Lost more than 80% of content
        print("⚠️  WARNING: Major content loss in artifact removal!")
        print("   This step is too aggressive - using previous version")
        edges = edges_before_clean
    
    # Stage 4: Final line connection
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_clean, iterations=2)
    edges_pil = Image.fromarray(edges)
    edges_pil.save(output_dir / "9_final_connect.png")
    print("✅ Step 9: Final line connection")
    
    # Stage 5: Binary threshold
    _, edges = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)
    edges_pil = Image.fromarray(edges)
    edges_pil.save(output_dir / "10_binary_threshold.png")
    print("✅ Step 10: Binary threshold")
    
    # Convert back to PIL and RGB
    result = Image.fromarray(edges)
    result = result.convert('RGB')
    result.save(output_dir / "11_rgb_conversion.png")
    print("✅ Step 11: RGB conversion")
    
    # Stage 6: Contrast enhancement
    enhancer = ImageEnhance.Contrast(result)
    result = enhancer.enhance(3.0)
    result.save(output_dir / "12_contrast_enhance.png")
    print("✅ Step 12: Contrast enhancement")
    
    # Stage 7: Unsharp mask
    result = result.filter(ImageFilter.UnsharpMask(radius=2, percent=300, threshold=1))
    result.save(output_dir / "13_unsharp_mask.png")
    print("✅ Step 13: Unsharp mask")
    
    # Stage 8: Final median filter
    result = result.filter(ImageFilter.MedianFilter(size=3))
    result.save(output_dir / "14_final_result.png")
    print("✅ Step 14: Final median filter")
    
    # Final analysis
    final_array = np.array(result.convert('L'))
    final_content = np.sum(final_array < 128) / total_pixels  # Count dark pixels
    print(f"\n📊 FINAL ANALYSIS:")
    print(f"   Original content ratio: {content_ratio:.3f}")
    print(f"   Final content ratio: {final_content:.3f}")
    print(f"   Overall content loss: {(content_ratio - final_content) / content_ratio * 100:.1f}%" if content_ratio > 0 else "N/A")
    
    if final_content < 0.01:
        print("❌ RESULT: Final image is essentially blank!")
        print("   Recommendation: Reduce processing aggressiveness")
    elif final_content > 0.05:
        print("✅ RESULT: Final image has reasonable content")
    else:
        print("⚠️  RESULT: Final image has minimal content")
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python debug_line_processing.py <image_path>")
        print("Example: python debug_line_processing.py COLORING_TEST.png")
        sys.exit(1)
    
    input_path = sys.argv[1]
    if not Path(input_path).exists():
        print(f"❌ File not found: {input_path}")
        sys.exit(1)
    
    result = debug_line_processing(input_path)
    if result:
        print(f"\n✅ Debug processing complete!")
        print(f"Check the debug_processing/ directory for step-by-step images")
    else:
        print(f"\n❌ Debug processing failed!")