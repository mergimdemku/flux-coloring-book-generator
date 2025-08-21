"""
Image post-processing utilities for coloring book optimization
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
from typing import Tuple, Dict, Any
import logging

class ColoringBookProcessor:
    """Post-processing pipeline for coloring book images"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_for_coloring(self, image: Image.Image, 
                           processing_params: Dict[str, Any]) -> Image.Image:
        """Complete processing pipeline for coloring book optimization"""
        
        # Convert PIL to OpenCV format
        cv_image = self._pil_to_cv(image)
        
        # Apply processing steps
        cv_image = self._enhance_contrast(cv_image)
        cv_image = self._adaptive_threshold(cv_image, processing_params)
        cv_image = self._thicken_lines(cv_image, processing_params)
        cv_image = self._remove_noise(cv_image)
        cv_image = self._ensure_white_background(cv_image)
        
        # Convert back to PIL
        result = self._cv_to_pil(cv_image)
        
        # Final PIL enhancements
        result = self._final_enhancement(result)
        
        return result
    
    def _pil_to_cv(self, pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to OpenCV format"""
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # PIL to numpy array
        np_image = np.array(pil_image)
        
        # RGB to BGR for OpenCV
        cv_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
        
        return cv_image
    
    def _cv_to_pil(self, cv_image: np.ndarray) -> Image.Image:
        """Convert OpenCV format to PIL Image"""
        # Handle grayscale
        if len(cv_image.shape) == 2:
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_GRAY2BGR)
        
        # BGR to RGB
        rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL
        return Image.fromarray(rgb_image)
    
    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance contrast to make lines more defined"""
        
        # Convert to grayscale for processing
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Convert back to BGR if original was color
        if len(image.shape) == 3:
            return cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        else:
            return enhanced
    
    def _adaptive_threshold(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Apply adaptive thresholding to create clean black/white image"""
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Apply adaptive threshold
        threshold = cv2.adaptiveThreshold(
            gray,
            255,  # Max value
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # Adaptive method
            cv2.THRESH_BINARY,  # Threshold type
            11,  # Block size
            2   # C parameter
        )
        
        return threshold
    
    def _thicken_lines(self, image: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Thicken lines to make them suitable for coloring"""
        
        kernel_size = params.get('morphology_kernel', 2)
        
        # Create morphological kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        
        # Invert image (lines become white, background becomes black)
        inverted = cv2.bitwise_not(image)
        
        # Dilate to thicken lines
        dilated = cv2.dilate(inverted, kernel, iterations=1)
        
        # Invert back
        result = cv2.bitwise_not(dilated)
        
        return result
    
    def _remove_noise(self, image: np.ndarray) -> np.ndarray:
        """Remove small noise artifacts"""
        
        # Use morphological opening to remove small noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        
        # Invert for processing
        inverted = cv2.bitwise_not(image)
        
        # Opening (erosion followed by dilation)
        opened = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, kernel)
        
        # Invert back
        result = cv2.bitwise_not(opened)
        
        # Additional noise removal using connected components
        result = self._remove_small_components(result)
        
        return result
    
    def _remove_small_components(self, image: np.ndarray, min_area: int = 50) -> np.ndarray:
        """Remove small connected components (noise)"""
        
        # Find connected components
        inverted = cv2.bitwise_not(image)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(inverted, connectivity=8)
        
        # Create mask for components to keep
        mask = np.zeros_like(inverted)
        
        for i in range(1, num_labels):  # Skip background (label 0)
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_area:
                mask[labels == i] = 255
        
        # Apply mask and invert back
        result = cv2.bitwise_not(mask)
        
        return result
    
    def _ensure_white_background(self, image: np.ndarray) -> np.ndarray:
        """Ensure background is pure white"""
        
        # Make sure white areas are pure white (255) and black areas are pure black (0)
        result = np.where(image > 127, 255, 0).astype(np.uint8)
        
        return result
    
    def _final_enhancement(self, image: Image.Image) -> Image.Image:
        """Final PIL-based enhancements"""
        
        # Ensure it's in RGB mode
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Enhance sharpness slightly
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.1)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        return image
    
    def validate_coloring_quality(self, image: Image.Image) -> Dict[str, Any]:
        """Validate that image is suitable for coloring"""
        
        # Convert to numpy for analysis
        np_image = np.array(image.convert('L'))  # Grayscale
        
        # Calculate metrics
        total_pixels = np_image.size
        black_pixels = np.sum(np_image < 50)  # Very dark pixels
        white_pixels = np.sum(np_image > 200)  # Very light pixels
        gray_pixels = total_pixels - black_pixels - white_pixels
        
        black_ratio = black_pixels / total_pixels
        white_ratio = white_pixels / total_pixels
        gray_ratio = gray_pixels / total_pixels
        
        # Check line thickness
        edges = cv2.Canny(np_image, 50, 150)
        line_density = np.sum(edges > 0) / total_pixels
        
        # Quality assessment
        quality_score = 100
        issues = []
        
        # Too much gray (not enough contrast)
        if gray_ratio > 0.1:
            quality_score -= 20
            issues.append("Too much gray - needs better contrast")
        
        # Too few lines
        if black_ratio < 0.05:
            quality_score -= 15
            issues.append("Lines too thin or sparse")
        
        # Too many lines (too dense)
        if black_ratio > 0.3:
            quality_score -= 15
            issues.append("Image too dense for coloring")
        
        # Background not white enough
        if white_ratio < 0.6:
            quality_score -= 10
            issues.append("Background not white enough")
        
        return {
            'quality_score': max(0, quality_score),
            'black_ratio': black_ratio,
            'white_ratio': white_ratio, 
            'gray_ratio': gray_ratio,
            'line_density': line_density,
            'issues': issues,
            'suitable_for_coloring': quality_score >= 60
        }
    
    def create_printable_version(self, image: Image.Image, dpi: int = 300) -> Image.Image:
        """Create print-optimized version"""
        
        # Ensure correct size for A4 at specified DPI
        a4_width_inches = 8.27
        a4_height_inches = 11.69
        
        target_width = int(a4_width_inches * dpi)
        target_height = int(a4_height_inches * dpi)
        
        # Resize if necessary (maintaining aspect ratio)
        current_width, current_height = image.size
        
        # Calculate scaling to fit within A4 while maintaining aspect ratio
        width_scale = target_width / current_width
        height_scale = target_height / current_height
        scale = min(width_scale, height_scale)
        
        new_width = int(current_width * scale)
        new_height = int(current_height * scale)
        
        # Resize image
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create A4 canvas and center image
        canvas = Image.new('RGB', (target_width, target_height), 'white')
        
        # Calculate position to center image
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        # Paste image onto canvas
        canvas.paste(resized, (x_offset, y_offset))
        
        return canvas
    
    def batch_process(self, images: list, processing_params: Dict[str, Any],
                     progress_callback=None) -> list:
        """Process multiple images"""
        
        results = []
        total = len(images)
        
        for i, image in enumerate(images):
            if progress_callback:
                progress_callback(i, total, f"Processing image {i+1}/{total}")
            
            try:
                processed = self.process_for_coloring(image, processing_params)
                results.append(processed)
            except Exception as e:
                self.logger.error(f"Failed to process image {i+1}: {e}")
                results.append(image)  # Return original on error
        
        if progress_callback:
            progress_callback(total, total, "Processing complete")
        
        return results