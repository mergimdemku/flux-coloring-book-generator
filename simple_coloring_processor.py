#!/usr/bin/env python3
"""
Simple Coloring Page Processor - No bullshit, just clean black and white lines
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def make_simple_coloring_page(input_image: Image.Image) -> Image.Image:
    """
    Convert any image to a clean black and white coloring page
    Simple approach: enhance contrast, threshold, clean up
    """
    logger.info("Converting to simple coloring page...")
    
    # Convert to grayscale
    if input_image.mode != 'L':
        gray_img = input_image.convert('L')
    else:
        gray_img = input_image
    
    # Convert to numpy
    gray_array = np.array(gray_img)
    
    # Check if image is very faint (FLUX often generates faint images)
    mean_brightness = np.mean(gray_array)
    logger.info(f"Image brightness: {mean_brightness:.1f}")
    
    if mean_brightness > 240:
        logger.info("Very faint image - boosting contrast heavily")
        # Boost contrast dramatically
        enhancer = ImageEnhance.Contrast(gray_img)
        gray_img = enhancer.enhance(8.0)  # Very aggressive
        gray_array = np.array(gray_img)
    elif mean_brightness > 200:
        logger.info("Faint image - boosting contrast moderately") 
        enhancer = ImageEnhance.Contrast(gray_img)
        gray_img = enhancer.enhance(4.0)
        gray_array = np.array(gray_img)
    
    # Simple threshold to black and white
    # Use Otsu's method for automatic threshold selection
    _, binary = cv2.threshold(gray_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # Invert if needed (we want black lines on white background)
    black_pixels = np.sum(binary == 0)
    white_pixels = np.sum(binary == 255)
    
    if black_pixels > white_pixels:
        binary = cv2.bitwise_not(binary)
        logger.info("Inverted image - now black lines on white background")
    
    # Light cleanup to connect nearby lines
    kernel = np.ones((2,2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
    # Remove tiny noise
    kernel_small = np.ones((1,1), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_small)
    
    # Convert back to PIL
    result = Image.fromarray(binary, mode='L')
    
    logger.info("Simple coloring page conversion complete")
    return result

if __name__ == "__main__":
    # Test with the existing images
    test_files = [
        "/mnt/d/CLAUDE/Kids_App_Painting_Books/test_input.png",
        "/mnt/d/CLAUDE/Kids_App_Painting_Books/test_gentle_output.png", 
        "/mnt/d/CLAUDE/Kids_App_Painting_Books/test_fixed_output.png"
    ]
    
    for test_file in test_files:
        try:
            logger.info(f"Testing {test_file}")
            img = Image.open(test_file)
            result = make_simple_coloring_page(img)
            output_path = test_file.replace(".png", "_simple_processed.png")
            result.save(output_path)
            logger.info(f"Saved to {output_path}")
        except Exception as e:
            logger.error(f"Error processing {test_file}: {e}")