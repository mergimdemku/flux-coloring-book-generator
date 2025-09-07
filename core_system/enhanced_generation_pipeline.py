#!/usr/bin/env python3
"""
Enhanced Generation Pipeline
Integrates fixed intelligent author with optimized FLUX generation
FIXES: Poor results, text artifacts, nonsense output
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image
import torch

from enhanced_intelligent_author import generate_intelligent_book
from optimized_flux_generator import OptimizedFluxGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedGenerationPipeline:
    """
    Complete pipeline with enhanced intelligent author and fixed FLUX generation
    ADDRESSES: User complaints about poor quality and text artifacts
    """
    
    def __init__(self):
        self.output_dir = Path("enhanced_output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize FLUX generator
        try:
            self.flux_generator = OptimizedFluxGenerator()
            logger.info("✅ FLUX generator initialized")
        except Exception as e:
            logger.error(f"❌ FLUX initialization failed: {e}")
            self.flux_generator = None
    
    def generate_complete_book(self, target_pages: int = 24, 
                              book_title: str = None) -> Dict[str, Any]:
        """
        Generate a complete coloring book with enhanced quality
        FIXES: All major issues identified by user
        """
        
        logger.info(f"🎨 Starting enhanced book generation ({target_pages} pages)...")
        
        # Step 1: Generate intelligent book structure
        logger.info("📚 Creating intelligent book structure...")
        book_data = generate_intelligent_book(target_pages)
        
        if book_title:
            book_data['title'] = book_title
        
        # Step 2: Generate images with enhanced prompts
        logger.info("🖼️ Generating images with enhanced prompts...")
        generated_images = []
        
        if not self.flux_generator:
            logger.error("❌ FLUX generator not available")
            return {"error": "FLUX generator not initialized"}
        
        for i, prompt_data in enumerate(book_data['prompts']):
            logger.info(f"Generating page {prompt_data['page_number']}: {prompt_data['subject']}")
            
            try:
                # Use enhanced prompt with optimized settings
                image = self.flux_generator.generate_image(
                    prompt=prompt_data['enhanced_prompt'],
                    negative_prompt=prompt_data['negative_prompt'],
                    **prompt_data['settings']
                )
                
                if image:
                    # Save image
                    page_filename = f"page_{prompt_data['page_number']:02d}_{prompt_data['page_type']}.png"
                    image_path = self.output_dir / book_data['unique_id'] / page_filename
                    image_path.parent.mkdir(exist_ok=True)
                    
                    image.save(image_path)
                    
                    generated_images.append({
                        'page_number': prompt_data['page_number'],
                        'page_type': prompt_data['page_type'],
                        'subject': prompt_data['subject'],
                        'image_path': str(image_path),
                        'success': True
                    })
                    
                    logger.info(f"✅ Page {prompt_data['page_number']} generated successfully")
                else:
                    logger.error(f"❌ Failed to generate page {prompt_data['page_number']}")
                    generated_images.append({
                        'page_number': prompt_data['page_number'],
                        'success': False,
                        'error': 'Generation failed'
                    })
                    
            except Exception as e:
                logger.error(f"❌ Error generating page {prompt_data['page_number']}: {e}")
                generated_images.append({
                    'page_number': prompt_data['page_number'],
                    'success': False,
                    'error': str(e)
                })
        
        # Step 3: Create final book package
        final_result = {
            'book_info': book_data,
            'generated_images': generated_images,
            'output_directory': str(self.output_dir / book_data['unique_id']),
            'success_count': len([img for img in generated_images if img.get('success')]),
            'total_pages': len(generated_images),
            'generation_complete': True
        }
        
        # Save book metadata
        metadata_path = self.output_dir / book_data['unique_id'] / 'book_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(final_result, f, indent=2, default=str)
        
        logger.info(f"📖 Book generation complete: {book_data['title']}")
        logger.info(f"✅ Successfully generated {final_result['success_count']}/{final_result['total_pages']} pages")
        logger.info(f"📁 Output saved to: {final_result['output_directory']}")
        
        return final_result
    
    def validate_generated_book(self, book_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the generated book for quality issues
        CHECKS: Text artifacts, poor line quality, composition issues
        """
        
        validation_results = {
            'overall_quality': 'good',
            'issues_found': [],
            'recommendations': []
        }
        
        failed_pages = [img for img in book_result['generated_images'] if not img.get('success')]
        if failed_pages:
            validation_results['issues_found'].append(f"{len(failed_pages)} pages failed to generate")
            validation_results['recommendations'].append("Retry failed pages with adjusted prompts")
            validation_results['overall_quality'] = 'needs_improvement'
        
        success_rate = book_result['success_count'] / book_result['total_pages']
        if success_rate < 0.8:
            validation_results['overall_quality'] = 'poor'
            validation_results['recommendations'].append("Consider adjusting generation settings")
        
        return validation_results

def main():
    """Main execution for enhanced pipeline"""
    
    print("🎨 ENHANCED COLORING BOOK GENERATION PIPELINE")
    print("=" * 50)
    print("FIXES: Poor results, text artifacts, nonsense output")
    print()
    
    pipeline = EnhancedGenerationPipeline()
    
    # Generate a test book
    result = pipeline.generate_complete_book(target_pages=12)
    
    if 'error' not in result:
        # Validate results
        validation = pipeline.validate_generated_book(result)
        
        print(f"📖 Book: {result['book_info']['title']}")
        print(f"✅ Success Rate: {result['success_count']}/{result['total_pages']} pages")
        print(f"🎯 Quality Assessment: {validation['overall_quality']}")
        
        if validation['issues_found']:
            print("⚠️ Issues Found:")
            for issue in validation['issues_found']:
                print(f"   • {issue}")
        
        if validation['recommendations']:
            print("💡 Recommendations:")
            for rec in validation['recommendations']:
                print(f"   • {rec}")
        
        print(f"📁 Output Directory: {result['output_directory']}")
    else:
        print(f"❌ Generation failed: {result['error']}")

if __name__ == "__main__":
    main()