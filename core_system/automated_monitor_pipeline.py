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

import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'archived_old_versions'))

from optimized_flux_generator import OptimizedFluxGenerator
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
        self.flux_generator = OptimizedFluxGenerator()
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
        
        # Cover prompt - convert to colorful cover style
        cover_character = book['cover_prompt'].split(';')[0]  # Get main character part
        prompts.append({
            'type': 'cover',
            'character': cover_character,  # Pass character separately
            'scene': book['cover_prompt'],  # Pass full scene
            'negative': book['negative'],
            'scene_description': "Cover"
        })
        
        # Page prompts - preserve character names from story text
        for page in book['pages']:
            # Extract character name from story text with improved logic
            story_text = page['text']
            
            # Handle different story text formats
            if "found a" in story_text:
                # Format: "Look! Whale Wally found a Lion!" -> extract "Whale Wally"
                # Split and find character name before "found"
                words = story_text.split()
                found_idx = None
                for i, word in enumerate(words):
                    if word in ["found", "sees", "meets"]:
                        found_idx = i
                        break
                
                if found_idx and found_idx >= 2:
                    # Take the 2 words before "found" as character name
                    character_name = ' '.join(words[found_idx-2:found_idx])
                else:
                    # Fallback to first 2 meaningful words (skip "Look!")
                    meaningful_words = [w for w in words if w.lower() not in ["look!", "look", "wow!", "see!"]]
                    character_name = ' '.join(meaningful_words[:2])
            else:
                # Standard format: "Dolphin Dany leaps" -> "Dolphin Dany"
                character_name = ' '.join(story_text.split()[:2])
            
            # Extract scene objects for emphasis (animals, objects mentioned)
            scene_objects = []
            scene_lower = page['scene'].lower()
            common_objects = [
                'lion', 'elephant', 'giraffe', 'monkey', 'zebra', 'penguin', 'tiger', 
                'hippo', 'kangaroo', 'panda', 'flamingo', 'seal', 'parrot', 'snake',
                'turtle', 'bear', 'wolf', 'owl', 'tree', 'rock', 'ball', 'banana',
                'bamboo', 'branch', 'water', 'ice', 'stream'
            ]
            
            for obj in common_objects:
                if obj in scene_lower:
                    scene_objects.append(obj)
            
            prompts.append({
                'type': 'coloring_page',
                'page_number': page['id'],
                'character': character_name,  # Pass character name
                'scene': page['scene'],  # Pass scene description  
                'scene_objects': scene_objects,  # NEW: Pass extracted objects for emphasis
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
                
                if prompt_data['type'] == 'cover':
                    # Pass character and scene directly to cover generator
                    image = self.flux_generator.generate_perfect_cover(
                        character_desc=prompt_data['character'],
                        scene_desc=prompt_data['scene'],
                        width=592,
                        height=832
                    )
                    
                    generated_images['cover'] = image
                    
                else:
                    # Pass character, scene, and objects to coloring page generator
                    processed = self.flux_generator.generate_ultra_clean_coloring_page(
                        character_desc=prompt_data['character'],
                        scene_desc=prompt_data['scene'],
                        scene_objects=prompt_data.get('scene_objects', []),  # NEW: Pass scene objects
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