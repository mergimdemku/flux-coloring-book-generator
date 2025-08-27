#!/usr/bin/env python3
"""
Test the new simple processor on existing images
"""

from PIL import Image
import logging
from clean_line_flux_generator import CleanLineFluxGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_new_processor():
    """Test the simplified processing on test images"""
    
    generator = CleanLineFluxGenerator()
    
    test_files = [
        "/mnt/d/CLAUDE/Kids_App_Painting_Books/test_input.png",
        "/mnt/d/CLAUDE/Kids_App_Painting_Books/test_gentle_output.png", 
        "/mnt/d/CLAUDE/Kids_App_Painting_Books/test_fixed_output.png"
    ]
    
    for test_file in test_files:
        try:
            logger.info(f"Testing new processor on {test_file}")
            img = Image.open(test_file)
            result = generator.apply_ultra_clean_line_processing(img, "Manga")
            output_path = test_file.replace(".png", "_new_processed.png")
            result.save(output_path)
            logger.info(f"Saved to {output_path}")
        except Exception as e:
            logger.error(f"Error processing {test_file}: {e}")

if __name__ == "__main__":
    test_new_processor()