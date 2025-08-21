"""
Quality validation system for coloring book content
"""

import numpy as np
from PIL import Image, ImageStat
import cv2
from typing import Dict, List, Any, Tuple
import logging
from pathlib import Path

class QualityValidator:
    """Validates coloring book images for quality and suitability"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Quality thresholds
        self.thresholds = {
            'min_line_thickness': 2,     # pixels at 300 DPI
            'max_line_thickness': 8,     # pixels at 300 DPI
            'min_white_ratio': 0.65,     # minimum white background
            'max_black_ratio': 0.25,     # maximum line coverage
            'max_gray_ratio': 0.08,      # maximum gray areas
            'min_contrast': 150,         # minimum contrast between lines and background
            'min_quality_score': 70      # overall quality threshold
        }
    
    def validate_coloring_page(self, image: Image.Image, age_range: str = "3-6 years") -> Dict[str, Any]:
        """Comprehensive validation of a coloring page"""
        
        # Adjust thresholds based on age range
        adjusted_thresholds = self._adjust_thresholds_for_age(age_range)
        
        # Run all validation checks
        results = {
            'overall_score': 0,
            'suitable_for_coloring': False,
            'issues': [],
            'warnings': [],
            'metrics': {},
            'age_appropriate': False
        }
        
        # Convert to numpy for analysis
        np_image = np.array(image.convert('RGB'))
        gray_image = np.array(image.convert('L'))
        
        # 1. Color distribution analysis
        color_results = self._analyze_color_distribution(np_image, gray_image, adjusted_thresholds)
        results['metrics'].update(color_results['metrics'])
        results['issues'].extend(color_results['issues'])
        results['warnings'].extend(color_results['warnings'])
        
        # 2. Line quality analysis  
        line_results = self._analyze_line_quality(gray_image, adjusted_thresholds)
        results['metrics'].update(line_results['metrics'])
        results['issues'].extend(line_results['issues'])
        results['warnings'].extend(line_results['warnings'])
        
        # 3. Contrast analysis
        contrast_results = self._analyze_contrast(gray_image, adjusted_thresholds)
        results['metrics'].update(contrast_results['metrics'])
        results['issues'].extend(contrast_results['issues'])
        results['warnings'].extend(contrast_results['warnings'])
        
        # 4. Complexity analysis for age appropriateness
        complexity_results = self._analyze_complexity(gray_image, age_range)
        results['metrics'].update(complexity_results['metrics'])
        results['issues'].extend(complexity_results['issues'])
        results['warnings'].extend(complexity_results['warnings'])
        results['age_appropriate'] = complexity_results['age_appropriate']
        
        # 5. Print readiness check
        print_results = self._check_print_readiness(image)
        results['metrics'].update(print_results['metrics'])
        results['issues'].extend(print_results['issues'])
        results['warnings'].extend(print_results['warnings'])
        
        # Calculate overall quality score
        results['overall_score'] = self._calculate_quality_score(results['metrics'], adjusted_thresholds)
        results['suitable_for_coloring'] = (
            results['overall_score'] >= adjusted_thresholds['min_quality_score'] and
            len([issue for issue in results['issues'] if issue['severity'] == 'critical']) == 0
        )
        
        return results
    
    def _adjust_thresholds_for_age(self, age_range: str) -> Dict[str, float]:
        """Adjust quality thresholds based on target age range"""
        
        thresholds = self.thresholds.copy()
        
        if '2-4' in age_range:
            # Younger children need thicker lines, simpler content
            thresholds['min_line_thickness'] = 4
            thresholds['max_line_thickness'] = 10
            thresholds['min_white_ratio'] = 0.75
            thresholds['max_black_ratio'] = 0.15
        elif '3-6' in age_range:
            # Standard settings
            pass
        elif '5-8' in age_range or '6-10' in age_range:
            # Older children can handle more detail
            thresholds['min_line_thickness'] = 1
            thresholds['max_line_thickness'] = 6
            thresholds['min_white_ratio'] = 0.60
            thresholds['max_black_ratio'] = 0.30
        
        return thresholds
    
    def _analyze_color_distribution(self, np_image: np.ndarray, gray_image: np.ndarray, 
                                   thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Analyze color distribution in the image"""
        
        results = {
            'metrics': {},
            'issues': [],
            'warnings': []
        }
        
        total_pixels = gray_image.size
        
        # Calculate color ratios
        white_pixels = np.sum(gray_image > 240)  # Very white pixels
        black_pixels = np.sum(gray_image < 15)   # Very black pixels
        gray_pixels = np.sum((gray_image >= 15) & (gray_image <= 240))  # Gray pixels
        
        white_ratio = white_pixels / total_pixels
        black_ratio = black_pixels / total_pixels
        gray_ratio = gray_pixels / total_pixels
        
        results['metrics'].update({
            'white_ratio': white_ratio,
            'black_ratio': black_ratio,
            'gray_ratio': gray_ratio
        })
        
        # Check white background ratio
        if white_ratio < thresholds['min_white_ratio']:
            results['issues'].append({
                'type': 'insufficient_white_background',
                'severity': 'critical',
                'message': f"Background too dark ({white_ratio:.1%}). Should be at least {thresholds['min_white_ratio']:.1%} white.",
                'suggestion': "Increase threshold values or improve background cleanup."
            })
        
        # Check line density
        if black_ratio > thresholds['max_black_ratio']:
            results['issues'].append({
                'type': 'too_dense',
                'severity': 'major',
                'message': f"Image too dense for coloring ({black_ratio:.1%} black). Maximum recommended: {thresholds['max_black_ratio']:.1%}.",
                'suggestion': "Reduce detail complexity or increase line spacing."
            })
        elif black_ratio < 0.03:
            results['warnings'].append({
                'type': 'too_sparse',
                'severity': 'minor',
                'message': f"Very few lines detected ({black_ratio:.1%}). May be too simple.",
                'suggestion': "Consider adding more detail if appropriate for age group."
            })
        
        # Check gray areas (indicates poor contrast/cleanup)
        if gray_ratio > thresholds['max_gray_ratio']:
            results['issues'].append({
                'type': 'excessive_gray',
                'severity': 'major',
                'message': f"Too much gray area ({gray_ratio:.1%}). Lines should be pure black/white.",
                'suggestion': "Improve thresholding and contrast enhancement."
            })
        
        # Check for color contamination
        if len(np_image.shape) == 3:
            # Check if image has color
            r_channel = np_image[:, :, 0]
            g_channel = np_image[:, :, 1] 
            b_channel = np_image[:, :, 2]
            
            color_variance = np.var([r_channel.mean(), g_channel.mean(), b_channel.mean()])
            
            if color_variance > 10:  # Threshold for color detection
                results['warnings'].append({
                    'type': 'color_detected',
                    'severity': 'minor',
                    'message': "Color detected in image. Coloring pages should be black and white only.",
                    'suggestion': "Convert to grayscale and apply proper thresholding."
                })
        
        return results
    
    def _analyze_line_quality(self, gray_image: np.ndarray, thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Analyze line thickness and quality"""
        
        results = {
            'metrics': {},
            'issues': [],
            'warnings': []
        }
        
        # Edge detection to find lines
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Distance transform to analyze line thickness
        binary = (gray_image < 128).astype(np.uint8) * 255
        dist_transform = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        
        # Find line thickness distribution
        line_pixels = binary > 0
        if np.any(line_pixels):
            thickness_values = dist_transform[line_pixels]
            avg_thickness = np.mean(thickness_values) * 2  # Distance is to center, so double for thickness
            min_thickness = np.min(thickness_values) * 2
            max_thickness = np.max(thickness_values) * 2
        else:
            avg_thickness = min_thickness = max_thickness = 0
        
        results['metrics'].update({
            'avg_line_thickness': avg_thickness,
            'min_line_thickness': min_thickness,
            'max_line_thickness': max_thickness,
            'edge_density': np.sum(edges > 0) / edges.size
        })
        
        # Check minimum line thickness
        if avg_thickness < thresholds['min_line_thickness']:
            results['issues'].append({
                'type': 'lines_too_thin',
                'severity': 'major',
                'message': f"Lines too thin ({avg_thickness:.1f}px). Minimum: {thresholds['min_line_thickness']}px.",
                'suggestion': "Apply morphological dilation to thicken lines."
            })
        
        # Check maximum line thickness
        if avg_thickness > thresholds['max_line_thickness']:
            results['warnings'].append({
                'type': 'lines_very_thick',
                'severity': 'minor',
                'message': f"Lines quite thick ({avg_thickness:.1f}px). May reduce coloring space.",
                'suggestion': "Consider reducing line thickness if appropriate."
            })
        
        # Check for broken lines
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        small_contours = [c for c in contours if cv2.contourArea(c) < 50]
        
        if len(small_contours) > len(contours) * 0.3:  # More than 30% small fragments
            results['warnings'].append({
                'type': 'fragmented_lines',
                'severity': 'minor',
                'message': f"Many small line fragments detected ({len(small_contours)} fragments).",
                'suggestion': "Apply morphological closing to connect broken lines."
            })
        
        return results
    
    def _analyze_contrast(self, gray_image: np.ndarray, thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Analyze contrast between lines and background"""
        
        results = {
            'metrics': {},
            'issues': [],
            'warnings': []
        }
        
        # Calculate histogram
        hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        
        # Find peaks (should have peaks at black and white ends)
        hist_smooth = cv2.GaussianBlur(hist.reshape(256, 1), (5, 1), 0).flatten()
        
        # Find background and line intensities
        background_peak = np.argmax(hist_smooth[200:]) + 200  # Look for white peak
        line_peak = np.argmax(hist_smooth[:100])              # Look for black peak
        
        contrast = background_peak - line_peak
        
        # RMS contrast calculation
        rms_contrast = np.sqrt(np.mean((gray_image - gray_image.mean()) ** 2))
        
        results['metrics'].update({
            'contrast': contrast,
            'rms_contrast': rms_contrast,
            'background_intensity': background_peak,
            'line_intensity': line_peak
        })
        
        # Check contrast levels
        if contrast < thresholds['min_contrast']:
            results['issues'].append({
                'type': 'low_contrast',
                'severity': 'critical',
                'message': f"Insufficient contrast ({contrast}). Minimum: {thresholds['min_contrast']}.",
                'suggestion': "Apply contrast enhancement or better thresholding."
            })
        
        # Check for proper bimodal distribution
        hist_peaks = []
        for i in range(1, 255):
            if hist_smooth[i] > hist_smooth[i-1] and hist_smooth[i] > hist_smooth[i+1]:
                if hist_smooth[i] > hist_smooth.max() * 0.1:  # Significant peak
                    hist_peaks.append(i)
        
        if len(hist_peaks) < 2:
            results['warnings'].append({
                'type': 'non_bimodal',
                'severity': 'minor',
                'message': "Image doesn't show clear separation between lines and background.",
                'suggestion': "Improve thresholding to create cleaner black/white separation."
            })
        
        return results
    
    def _analyze_complexity(self, gray_image: np.ndarray, age_range: str) -> Dict[str, Any]:
        """Analyze image complexity for age appropriateness"""
        
        results = {
            'metrics': {},
            'issues': [],
            'warnings': [],
            'age_appropriate': False
        }
        
        # Edge detection for complexity analysis
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Find contours for shape analysis
        binary = (gray_image < 128).astype(np.uint8) * 255
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Calculate complexity metrics
        edge_density = np.sum(edges > 0) / edges.size
        num_shapes = len(contours)
        
        # Shape size analysis
        if contours:
            areas = [cv2.contourArea(c) for c in contours]
            avg_shape_size = np.mean(areas)
            min_shape_size = np.min(areas)
            shape_size_variance = np.var(areas)
        else:
            avg_shape_size = min_shape_size = shape_size_variance = 0
        
        # Detail density (high frequency content)
        f_transform = np.fft.fft2(gray_image)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        
        # High frequency energy (indicates fine details)
        h, w = gray_image.shape
        center_h, center_w = h // 2, w // 2
        high_freq_mask = np.ones((h, w))
        cv2.circle(high_freq_mask, (center_w, center_h), min(center_h, center_w) // 3, 0, -1)
        high_freq_energy = np.sum(magnitude_spectrum * high_freq_mask) / np.sum(magnitude_spectrum)
        
        results['metrics'].update({
            'edge_density': edge_density,
            'num_shapes': num_shapes,
            'avg_shape_size': avg_shape_size,
            'min_shape_size': min_shape_size,
            'shape_complexity': shape_size_variance,
            'detail_density': high_freq_energy
        })
        
        # Age-specific complexity checks
        if '2-4' in age_range:
            # Very simple for toddlers
            complexity_limits = {
                'max_edge_density': 0.05,
                'max_shapes': 5,
                'min_shape_size': 1000
            }
        elif '3-6' in age_range:
            # Simple to moderate
            complexity_limits = {
                'max_edge_density': 0.08,
                'max_shapes': 10,
                'min_shape_size': 500
            }
        elif '5-8' in age_range:
            # Moderate complexity
            complexity_limits = {
                'max_edge_density': 0.12,
                'max_shapes': 15,
                'min_shape_size': 200
            }
        else:  # 6-10 years
            # More complex allowed
            complexity_limits = {
                'max_edge_density': 0.15,
                'max_shapes': 20,
                'min_shape_size': 100
            }
        
        # Check complexity appropriateness
        age_appropriate = True
        
        if edge_density > complexity_limits['max_edge_density']:
            results['issues'].append({
                'type': 'too_complex',
                'severity': 'major',
                'message': f"Too complex for {age_range} ({edge_density:.3f} edge density).",
                'suggestion': "Simplify design or adjust target age range."
            })
            age_appropriate = False
        
        if num_shapes > complexity_limits['max_shapes']:
            results['warnings'].append({
                'type': 'many_shapes',
                'severity': 'minor',
                'message': f"Many shapes detected ({num_shapes}). May be overwhelming for {age_range}.",
                'suggestion': "Consider consolidating shapes or simplifying design."
            })
        
        if min_shape_size < complexity_limits['min_shape_size'] and min_shape_size > 0:
            results['warnings'].append({
                'type': 'tiny_shapes',
                'severity': 'minor',
                'message': f"Very small shapes detected (min: {min_shape_size:.0f}px²). May be hard to color.",
                'suggestion': "Remove tiny details or increase minimum shape size."
            })
        
        results['age_appropriate'] = age_appropriate
        
        return results
    
    def _check_print_readiness(self, image: Image.Image) -> Dict[str, Any]:
        """Check if image is ready for printing"""
        
        results = {
            'metrics': {},
            'issues': [],
            'warnings': []
        }
        
        width, height = image.size
        
        # Check resolution and size
        dpi = image.info.get('dpi', (72, 72))
        if isinstance(dpi, tuple):
            dpi_x, dpi_y = dpi
        else:
            dpi_x = dpi_y = dpi
        
        # Calculate physical size in inches
        width_inches = width / dpi_x if dpi_x > 0 else 0
        height_inches = height / dpi_y if dpi_y > 0 else 0
        
        results['metrics'].update({
            'width_pixels': width,
            'height_pixels': height,
            'dpi_x': dpi_x,
            'dpi_y': dpi_y,
            'width_inches': width_inches,
            'height_inches': height_inches,
            'aspect_ratio': width / height if height > 0 else 0
        })
        
        # Check DPI for print quality
        if dpi_x < 300 or dpi_y < 300:
            results['issues'].append({
                'type': 'low_dpi',
                'severity': 'major',
                'message': f"Low resolution ({dpi_x}x{dpi_y} DPI). Recommended: 300 DPI for print.",
                'suggestion': "Increase image resolution or regenerate at higher DPI."
            })
        
        # Check A4 proportions (8.27 x 11.69 inches)
        a4_ratio = 11.69 / 8.27
        current_ratio = height / width if width > 0 else 0
        
        ratio_difference = abs(current_ratio - a4_ratio) / a4_ratio
        
        if ratio_difference > 0.05:  # 5% tolerance
            results['warnings'].append({
                'type': 'aspect_ratio',
                'severity': 'minor', 
                'message': f"Aspect ratio ({current_ratio:.2f}) doesn't match A4 ({a4_ratio:.2f}).",
                'suggestion': "Adjust image dimensions for optimal A4 printing."
            })
        
        # Check file format
        if image.format and image.format.upper() not in ['PNG', 'JPEG', 'TIFF']:
            results['warnings'].append({
                'type': 'format',
                'severity': 'minor',
                'message': f"Image format ({image.format}) may not be optimal for print.",
                'suggestion': "Use PNG or TIFF format for best print quality."
            })
        
        return results
    
    def _calculate_quality_score(self, metrics: Dict[str, float], thresholds: Dict[str, float]) -> int:
        """Calculate overall quality score (0-100)"""
        
        score = 100
        
        # Deduct points for various quality issues
        
        # White background ratio
        white_ratio = metrics.get('white_ratio', 0)
        if white_ratio < thresholds['min_white_ratio']:
            score -= (thresholds['min_white_ratio'] - white_ratio) * 100
        
        # Black ratio (line density)
        black_ratio = metrics.get('black_ratio', 0)
        if black_ratio > thresholds['max_black_ratio']:
            score -= (black_ratio - thresholds['max_black_ratio']) * 200
        
        # Gray ratio (poor contrast)
        gray_ratio = metrics.get('gray_ratio', 0)
        if gray_ratio > thresholds['max_gray_ratio']:
            score -= (gray_ratio - thresholds['max_gray_ratio']) * 300
        
        # Line thickness
        avg_thickness = metrics.get('avg_line_thickness', 0)
        if avg_thickness < thresholds['min_line_thickness']:
            score -= (thresholds['min_line_thickness'] - avg_thickness) * 10
        
        # Contrast
        contrast = metrics.get('contrast', 255)
        if contrast < thresholds['min_contrast']:
            score -= (thresholds['min_contrast'] - contrast) / 5
        
        # DPI penalty
        dpi_x = metrics.get('dpi_x', 300)
        if dpi_x < 300:
            score -= (300 - dpi_x) / 10
        
        return max(0, min(100, int(score)))
    
    def validate_batch(self, images: List[Image.Image], age_range: str = "3-6 years", 
                      progress_callback=None) -> List[Dict[str, Any]]:
        """Validate multiple images"""
        
        results = []
        total = len(images)
        
        for i, image in enumerate(images):
            if progress_callback:
                progress_callback(i, total, f"Validating image {i+1}/{total}")
            
            try:
                result = self.validate_coloring_page(image, age_range)
                result['image_index'] = i
                results.append(result)
            except Exception as e:
                self.logger.error(f"Validation failed for image {i+1}: {e}")
                results.append({
                    'image_index': i,
                    'overall_score': 0,
                    'suitable_for_coloring': False,
                    'issues': [{'type': 'validation_error', 'severity': 'critical', 'message': str(e)}],
                    'warnings': [],
                    'metrics': {},
                    'age_appropriate': False
                })
        
        if progress_callback:
            progress_callback(total, total, "Validation complete")
        
        return results
    
    def generate_quality_report(self, validation_results: List[Dict[str, Any]], 
                               project_title: str = "Coloring Book") -> str:
        """Generate a human-readable quality report"""
        
        report_lines = [
            f"Quality Validation Report: {project_title}",
            "=" * (len(project_title) + 26),
            ""
        ]
        
        # Overall statistics
        total_images = len(validation_results)
        suitable_count = sum(1 for r in validation_results if r['suitable_for_coloring'])
        avg_score = np.mean([r['overall_score'] for r in validation_results])
        
        report_lines.extend([
            f"Total Images: {total_images}",
            f"Suitable for Coloring: {suitable_count}/{total_images} ({suitable_count/total_images:.1%})",
            f"Average Quality Score: {avg_score:.1f}/100",
            ""
        ])
        
        # Issues summary
        all_issues = []
        all_warnings = []
        
        for result in validation_results:
            all_issues.extend(result['issues'])
            all_warnings.extend(result['warnings'])
        
        if all_issues:
            report_lines.extend([
                f"Issues Found ({len(all_issues)} total):",
                "-" * 20
            ])
            
            # Group issues by type
            issue_types = {}
            for issue in all_issues:
                issue_type = issue['type']
                if issue_type not in issue_types:
                    issue_types[issue_type] = []
                issue_types[issue_type].append(issue)
            
            for issue_type, issues in issue_types.items():
                report_lines.append(f"• {issue_type}: {len(issues)} occurrences")
                if issues:
                    report_lines.append(f"  └─ {issues[0]['message']}")
            
            report_lines.append("")
        
        # Per-image details
        report_lines.extend([
            "Individual Image Results:",
            "-" * 25
        ])
        
        for i, result in enumerate(validation_results):
            status = "✓ PASS" if result['suitable_for_coloring'] else "✗ FAIL"
            score = result['overall_score']
            
            report_lines.append(f"Image {i+1:2d}: {status} (Score: {score:3.0f}/100)")
            
            # Show critical issues
            critical_issues = [issue for issue in result['issues'] if issue['severity'] == 'critical']
            if critical_issues:
                for issue in critical_issues:
                    report_lines.append(f"         └─ CRITICAL: {issue['message']}")
        
        return "\n".join(report_lines)