#!/usr/bin/env python3
"""
Automated Monitoring Pipeline - Watches new_stories folder and processes automatically
"""

import os
import time
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import torch
import gc

from clean_line_flux_generator import CleanLineFluxGenerator
from enhanced_pdf_generator import EnhancedPDFGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutomatedMonitorPipeline:
    """Monitors new_stories folder and automatically processes stories"""
    
    def __init__(self):
        self.new_stories_dir = Path("new_stories")
        self.old_stories_dir = Path("old_stories")
        self.output_dir = Path("automated_books")
        
        # Create directories if they don't exist
        self.new_stories_dir.mkdir(exist_ok=True)
        self.old_stories_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize generators
        logger.info("Initializing generators...")
        self.flux_generator = CleanLineFluxGenerator()
        self.pdf_generator = EnhancedPDFGenerator(str(self.output_dir))
        
        # Load FLUX model
        logger.info("Loading FLUX model...")
        if not self.flux_generator.load_model():
            logger.error("Failed to load FLUX model - exiting")
            raise RuntimeError("FLUX model failed to load")
        logger.info("✅ FLUX model loaded successfully")
        
        self.check_interval = 300  # 5 minutes in seconds
        self.running = True
        
        # Statistics
        self.stats = {
            'stories_processed': 0,
            'images_generated': 0,
            'pdfs_created': 0,
            'errors': 0,
            'start_time': datetime.now().isoformat()
        }
    
    def check_new_stories(self) -> Optional[Path]:
        """Check if there are any new story files to process"""
        json_files = list(self.new_stories_dir.glob("*.json"))
        
        if json_files:
            # Return the oldest file (first in, first out)
            return min(json_files, key=lambda f: f.stat().st_mtime)
        return None
    
    def load_story_file(self, filepath: Path) -> Dict[str, Any]:
        """Load and validate story JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            if 'book' in data:
                # New JSON style (like magic_garden.json)
                return self.convert_json_style_story(data)
            elif 'story' in data:
                # Old style with story/prompts
                return data
            else:
                logger.error(f"Invalid story format in {filepath}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return None
    
    def convert_json_style_story(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert JSON style story to our pipeline format"""
        book = data['book']
        
        # Extract character from cover prompt
        cover_parts = book['cover_prompt'].split(';')
        character_desc = cover_parts[0] if cover_parts else "character"
        
        # Create story data
        story_data = {
            'id': f"story_{int(time.time())}",
            'title': book['title'],
            'age_range': book['age_range'],
            'style': book['style'],
            'art_style': {'name': book['style']},  # Add for compatibility
            'negative': book['negative'],
            'cover_prompt': book['cover_prompt'],
            'character_description': character_desc,
            'generated_at': datetime.now().isoformat()
        }
        
        # Create prompts from pages
        prompts = []
        
        # Cover prompt
        prompts.append({
            'type': 'cover',
            'prompt': f"{book['cover_prompt']}, {book['style']}",
            'negative': book['negative'],
            'scene_description': "Cover"
        })
        
        # Page prompts
        for page in book['pages']:
            prompts.append({
                'type': 'coloring_page',
                'page_number': page['id'],
                'prompt': f"{page['scene']}, {book['style']}",
                'negative': book['negative'],
                'scene_description': page['text'],
                'scene_visual': page['scene']
            })
        
        return {
            'story': story_data,
            'prompts': prompts,
            'json_style': True
        }
    
    def generate_images(self, story_data: Dict[str, Any], prompts: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate all images for the story"""
        generated_images = {
            'cover': None,
            'coloring_pages': []
        }
        
        logger.info(f"Generating images for: {story_data.get('title', 'Unknown')}")
        
        for i, prompt_data in enumerate(prompts):
            try:
                logger.info(f"Generating {prompt_data['type']} {i+1}/{len(prompts)}")
                
                # Add negative prompt if specified
                full_prompt = prompt_data['prompt']
                negative_prompt = prompt_data.get('negative', '')
                
                if prompt_data['type'] == 'cover':
                    # Use the proper enhanced cover generation method
                    cover_prompt_data = {
                        'prompt': full_prompt,
                        'negative': negative_prompt,
                        'type': 'cover'
                    }
                    
                    # Generate high-quality cover with all enhancements
                    image = self.flux_generator.generate_perfect_cover(
                        prompt_data=cover_prompt_data,
                        story_data=story_data,
                        width=592,
                        height=832
                    )
                    
                    generated_images['cover'] = image
                    
                else:
                    # Use the proper enhanced coloring page generation method
                    page_prompt_data = {
                        'prompt': full_prompt,
                        'negative': negative_prompt,
                        'type': 'coloring_page',
                        'page_number': prompt_data.get('page_number', i)
                    }
                    
                    # Generate ultra-clean coloring page with all processing
                    processed = self.flux_generator.generate_ultra_clean_coloring_page(
                        prompt_data=page_prompt_data,
                        story_data=story_data,
                        width=592,
                        height=832
                    )
                    
                    if not processed:
                        logger.warning(f"Failed to generate page {i+1}")
                    
                    generated_images['coloring_pages'].append({
                        'page_number': prompt_data['page_number'],
                        'image': processed,
                        'description': prompt_data.get('scene_description', '')
                    })
                
                self.stats['images_generated'] += 1
                
                # Memory cleanup
                if i % 5 == 0:
                    gc.collect()
                    torch.cuda.empty_cache() if torch.cuda.is_available() else None
                    
            except Exception as e:
                logger.error(f"Error generating image {i+1}: {e}")
                self.stats['errors'] += 1
        
        return generated_images
    
    def create_pdf(self, story_data: Dict[str, Any], images: Dict[str, Any], prompts: List[Dict[str, str]]) -> Optional[str]:
        """Create PDF from generated images"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            title_clean = story_data['title'].replace(' ', '_').replace("'", "")
            pdf_filename = f"{title_clean}_{timestamp}.pdf"
            pdf_path = self.output_dir / pdf_filename
            
            # Create PDF using enhanced generator
            coloring_images = [page['image'] for page in images['coloring_pages'] if page['image']]
            
            pdf_path = self.pdf_generator.generate_complete_book_pdf(
                story_data=story_data,
                cover_image=images['cover'],
                coloring_images=coloring_images,
                prompts_data=prompts  # Pass actual prompts instead of empty list
            )
            
            self.stats['pdfs_created'] += 1
            logger.info(f"✅ PDF created: {pdf_path}")
            return str(pdf_path)
            
        except Exception as e:
            logger.error(f"Error creating PDF: {e}")
            self.stats['errors'] += 1
            return None
    
    def process_story(self, story_file: Path) -> bool:
        """Process a single story file"""
        logger.info(f"📖 Processing story: {story_file.name}")
        
        try:
            # Load story
            story_data = self.load_story_file(story_file)
            if not story_data:
                logger.error(f"Failed to load {story_file}")
                return False
            
            # Extract components
            story_info = story_data.get('story', {})
            prompts = story_data.get('prompts', [])
            
            if not prompts:
                logger.error(f"No prompts found in {story_file}")
                return False
            
            # Generate images
            images = self.generate_images(story_info, prompts)
            
            if not images['cover'] or not images['coloring_pages']:
                logger.error("Failed to generate images")
                return False
            
            # Create PDF
            pdf_path = self.create_pdf(story_info, images, prompts)
            
            if pdf_path:
                # Move story file to old_stories
                old_path = self.old_stories_dir / story_file.name
                shutil.move(str(story_file), str(old_path))
                logger.info(f"✅ Story moved to old_stories: {old_path}")
                
                self.stats['stories_processed'] += 1
                
                # Save metadata
                self.save_metadata(story_info, pdf_path)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing story: {e}")
            self.stats['errors'] += 1
            return False
    
    def save_metadata(self, story_data: Dict[str, Any], pdf_path: str):
        """Save processing metadata"""
        metadata = {
            'story': story_data,
            'pdf_path': pdf_path,
            'processed_at': datetime.now().isoformat(),
            'stats': self.stats.copy()
        }
        
        pdf_name = Path(pdf_path).stem
        metadata_path = self.output_dir / f"{pdf_name}_metadata.json"
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def run(self):
        """Main monitoring loop"""
        logger.info("🚀 Starting Automated Monitor Pipeline")
        logger.info(f"📁 Watching: {self.new_stories_dir}")
        logger.info(f"📚 Output: {self.output_dir}")
        logger.info(f"⏰ Check interval: {self.check_interval} seconds")
        
        while self.running:
            try:
                # Check for new stories
                story_file = self.check_new_stories()
                
                if story_file:
                    logger.info(f"📌 Found new story: {story_file.name}")
                    
                    # Process the story
                    success = self.process_story(story_file)
                    
                    if success:
                        logger.info(f"✅ Successfully processed: {story_file.name}")
                        logger.info(f"📊 Stats: {self.stats['stories_processed']} stories, {self.stats['images_generated']} images, {self.stats['pdfs_created']} PDFs")
                    else:
                        logger.error(f"❌ Failed to process: {story_file.name}")
                        # Move failed file to old_stories with error prefix
                        error_name = f"ERROR_{story_file.name}"
                        error_path = self.old_stories_dir / error_name
                        shutil.move(str(story_file), str(error_path))
                    
                    # Check again immediately for more files
                    continue
                    
                else:
                    # No files found, wait
                    logger.info(f"💤 No new stories. Checking again in {self.check_interval} seconds...")
                    time.sleep(self.check_interval)
                    
            except KeyboardInterrupt:
                logger.info("⏹️  Stopping pipeline (user interrupt)")
                self.running = False
                break
                
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(30)  # Wait 30 seconds on error
        
        # Final stats
        logger.info("📊 Final Statistics:")
        logger.info(f"  Stories processed: {self.stats['stories_processed']}")
        logger.info(f"  Images generated: {self.stats['images_generated']}")
        logger.info(f"  PDFs created: {self.stats['pdfs_created']}")
        logger.info(f"  Errors: {self.stats['errors']}")


if __name__ == "__main__":
    pipeline = AutomatedMonitorPipeline()
    pipeline.run()