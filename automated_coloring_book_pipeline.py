#!/usr/bin/env python3
"""
Automated 24/7 Coloring Book Generation Pipeline
Integrates story generation, image generation, and PDF creation into a complete pipeline
"""

import os
import time
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
from queue import Queue
import traceback

from improved_story_generator import ImprovedStoryGenerator
from clean_line_flux_generator import CleanLineFluxGenerator
from enhanced_pdf_generator import EnhancedPDFGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomatedColoringBookPipeline:
    """Complete automated pipeline for 24/7 coloring book generation"""
    
    def __init__(self, output_dir: str = "automated_books"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize improved components
        logger.info("Initializing improved pipeline components...")
        self.story_generator = ImprovedStoryGenerator()
        self.flux_generator = CleanLineFluxGenerator()
        self.pdf_generator = EnhancedPDFGenerator(str(self.output_dir))
        
        # Pipeline state
        self.running = False
        self.stats = {
            'stories_generated': 0,
            'images_generated': 0,
            'pdfs_created': 0,
            'errors': 0,
            'start_time': None,
            'last_generation': None
        }
        
        # Processing queue
        self.story_queue = Queue(maxsize=10)
        self.generation_queue = Queue(maxsize=5)
        
        # Settings
        self.settings = {
            'story_generation_interval': 60,  # Generate story every 60 minutes
            'max_concurrent_generations': 1,   # Process one at a time for memory management
            'retry_attempts': 3,
            'image_dimensions': (592, 840),    # A4 portrait FLUX-compatible
            'enable_covers': True,
            'enable_info_pages': True,
            'cleanup_temp_files': True
        }
        
        # Status tracking
        self.current_status = "Initializing"
        self.current_story = None
        self.current_progress = 0
        
    def initialize_components(self) -> bool:
        """Initialize all pipeline components"""
        
        logger.info("Loading FLUX model...")
        self.current_status = "Loading FLUX model"
        
        if not self.flux_generator.load_model():
            logger.error("Failed to load FLUX model")
            return False
        
        logger.info("✅ All components initialized successfully")
        self.current_status = "Ready"
        return True
    
    def generate_story_batch(self) -> Optional[Dict[str, Any]]:
        """Generate new story batch from story generator"""
        
        logger.info("Generating new story batch...")
        self.current_status = "Generating story"
        
        try:
            story_batch = self.story_generator.get_next_story_batch()
            
            self.stats['stories_generated'] += 1
            self.stats['last_generation'] = datetime.now().isoformat()
            
            logger.info(f"✅ Story generated: {story_batch['story_data']['title']}")
            logger.info(f"📚 Style: {story_batch['story_data']['art_style']['name']}")
            logger.info(f"🎨 Prompts: {len(story_batch['prompts'])}")
            
            return story_batch
            
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            self.stats['errors'] += 1
            return None
    
    def generate_images_for_story(self, story_batch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate all images (cover + coloring pages) for a story"""
        
        story_data = story_batch['story_data']
        prompts = story_batch['prompts']
        
        logger.info(f"Starting image generation for: {story_data['title']}")
        self.current_status = f"Generating images for {story_data['title']}"
        self.current_story = story_data['title']
        self.current_progress = 0
        
        generated_images = {
            'cover_image': None,
            'coloring_images': [],
            'failed_images': []
        }
        
        total_images = len(prompts)
        
        try:
            for i, prompt_data in enumerate(prompts):
                self.current_progress = int((i / total_images) * 100)
                
                logger.info(f"Generating image {i+1}/{total_images}: {prompt_data['type']}")
                
                # Retry logic for failed generations
                image = None
                for attempt in range(self.settings['retry_attempts']):
                    try:
                        if prompt_data['type'] == 'cover':
                            # Generate perfect cover with clean lines and title integration
                            image = self.flux_generator.generate_perfect_cover(
                                prompt_data=prompt_data,
                                story_data=story_data,
                                width=self.settings['image_dimensions'][0],
                                height=self.settings['image_dimensions'][1]
                            )
                        else:
                            # Generate ultra-clean B&W coloring page
                            image = self.flux_generator.generate_ultra_clean_coloring_page(
                                prompt_data=prompt_data,
                                story_data=story_data,
                                width=self.settings['image_dimensions'][0],
                                height=self.settings['image_dimensions'][1]
                            )
                        
                        if image:
                            break
                        else:
                            logger.warning(f"Attempt {attempt + 1} failed for image {i+1}")
                            
                    except Exception as e:
                        logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                        if attempt == self.settings['retry_attempts'] - 1:
                            logger.error(f"All attempts failed for image {i+1}")
                
                if image:
                    if prompt_data['type'] == 'cover':
                        generated_images['cover_image'] = image
                        logger.info(f"✅ Cover image generated")
                    else:
                        generated_images['coloring_images'].append(image)
                        logger.info(f"✅ Coloring page {len(generated_images['coloring_images'])} generated")
                    
                    self.stats['images_generated'] += 1
                else:
                    generated_images['failed_images'].append(i)
                    logger.error(f"❌ Failed to generate image {i+1}")
                    self.stats['errors'] += 1
                
                # Memory cleanup after each image
                self.flux_generator.cleanup_memory()
                time.sleep(1)  # Brief pause to prevent overheating
            
            self.current_progress = 100
            logger.info(f"✅ Image generation completed")
            logger.info(f"📊 Success: {len(generated_images['coloring_images']) + (1 if generated_images['cover_image'] else 0)}/{total_images}")
            
            return generated_images
            
        except Exception as e:
            logger.error(f"Image generation pipeline failed: {e}")
            traceback.print_exc()
            self.stats['errors'] += 1
            return None
    
    def create_pdf_book(self, story_batch: Dict[str, Any], 
                       generated_images: Dict[str, Any]) -> Optional[str]:
        """Create final PDF book"""
        
        story_data = story_batch['story_data']
        prompts = story_batch['prompts']
        
        logger.info(f"Creating PDF book for: {story_data['title']}")
        self.current_status = f"Creating PDF for {story_data['title']}"
        
        try:
            pdf_path = self.pdf_generator.generate_complete_book_pdf(
                story_data=story_data,
                cover_image=generated_images['cover_image'],
                coloring_images=generated_images['coloring_images'],
                prompts_data=prompts
            )
            
            self.stats['pdfs_created'] += 1
            logger.info(f"✅ PDF created: {pdf_path}")
            
            # Save generation metadata
            self.save_generation_metadata(story_batch, generated_images, pdf_path)
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF creation failed: {e}")
            self.stats['errors'] += 1
            return None
    
    def save_generation_metadata(self, story_batch: Dict[str, Any], 
                               generated_images: Dict[str, Any], 
                               pdf_path: str) -> None:
        """Save metadata about the generation process"""
        
        metadata = {
            'story': story_batch['story_data'],
            'generation_info': {
                'generated_at': datetime.now().isoformat(),
                'pdf_path': pdf_path,
                'total_prompts': len(story_batch['prompts']),
                'successful_images': len(generated_images['coloring_images']) + (1 if generated_images['cover_image'] else 0),
                'failed_images': len(generated_images['failed_images']),
                'pipeline_version': '2.0_improved_stories_clean_lines'
            },
            'stats': self.stats.copy()
        }
        
        # Save metadata file
        metadata_filename = Path(pdf_path).stem + '_metadata.json'
        metadata_path = self.output_dir / metadata_filename
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Metadata saved: {metadata_path}")
    
    def process_single_book(self) -> bool:
        """Process one complete book from story to PDF"""
        
        try:
            # Step 1: Generate story
            story_batch = self.generate_story_batch()
            if not story_batch:
                return False
            
            # Step 2: Generate images
            generated_images = self.generate_images_for_story(story_batch)
            if not generated_images or not generated_images['coloring_images']:
                logger.error("No coloring images generated, skipping PDF creation")
                return False
            
            # Step 3: Create PDF
            pdf_path = self.create_pdf_book(story_batch, generated_images)
            if not pdf_path:
                return False
            
            logger.info(f"🎉 Complete book generated successfully!")
            logger.info(f"📖 Title: {story_batch['story_data']['title']}")
            logger.info(f"🎨 Style: {story_batch['story_data']['art_style']['name']}")
            logger.info(f"📁 PDF: {pdf_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Book processing failed: {e}")
            traceback.print_exc()
            self.stats['errors'] += 1
            return False
    
    def start_automated_pipeline(self, story_interval_minutes: int = 60):
        """Start the automated 24/7 pipeline"""
        
        if not self.initialize_components():
            logger.error("Failed to initialize components")
            return False
        
        logger.info("🚀 Starting automated 24/7 coloring book pipeline")
        logger.info(f"📅 Story generation interval: {story_interval_minutes} minutes")
        logger.info(f"📊 Image dimensions: {self.settings['image_dimensions']}")
        
        self.running = True
        self.stats['start_time'] = datetime.now().isoformat()
        
        def pipeline_loop():
            while self.running:
                try:
                    self.current_status = "Waiting for next generation cycle"
                    
                    # Process one book
                    success = self.process_single_book()
                    
                    if success:
                        logger.info("✅ Book generation cycle completed successfully")
                    else:
                        logger.warning("⚠️  Book generation cycle had issues")
                    
                    # Wait before next cycle (allowing story generator to create new content)
                    wait_time = story_interval_minutes * 60  # Convert to seconds
                    logger.info(f"💤 Waiting {story_interval_minutes} minutes until next generation...")
                    
                    for i in range(wait_time):
                        if not self.running:
                            break
                        time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Pipeline loop error: {e}")
                    traceback.print_exc()
                    self.stats['errors'] += 1
                    time.sleep(300)  # Wait 5 minutes before retrying
        
        # Start pipeline thread
        self.pipeline_thread = threading.Thread(target=pipeline_loop, daemon=True)
        self.pipeline_thread.start()
        
        logger.info("🎨 Automated pipeline is now running 24/7!")
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        
        uptime = "Not started"
        if self.stats['start_time']:
            start = datetime.fromisoformat(self.stats['start_time'])
            uptime = str(datetime.now() - start)
        
        return {
            'running': self.running,
            'current_status': self.current_status,
            'current_story': self.current_story,
            'current_progress': self.current_progress,
            'stats': self.stats,
            'uptime': uptime,
            'queue_sizes': {
                'stories': self.story_queue.qsize(),
                'generation': self.generation_queue.qsize()
            }
        }
    
    def stop_pipeline(self):
        """Stop the automated pipeline"""
        
        logger.info("🛑 Stopping automated pipeline...")
        self.running = False
        self.current_status = "Stopped"
        
        # Cleanup
        self.flux_generator.cleanup_memory()
        
        logger.info("Pipeline stopped successfully")

def main():
    """Run the automated pipeline"""
    
    print("🎨 FLUX Automated Coloring Book Pipeline")
    print("=" * 50)
    
    pipeline = AutomatedColoringBookPipeline()
    
    try:
        # Start pipeline
        success = pipeline.start_automated_pipeline(story_interval_minutes=30)  # Generate every 30 minutes
        
        if not success:
            print("❌ Failed to start pipeline")
            return
        
        print("🚀 Pipeline started successfully!")
        print("📊 Status updates:")
        
        # Status monitoring loop
        while True:
            try:
                status = pipeline.get_status()
                
                print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"📊 Status: {status['current_status']}")
                if status['current_story']:
                    print(f"📖 Current: {status['current_story']} ({status['current_progress']}%)")
                print(f"📈 Stats: {status['stats']['stories_generated']} stories, {status['stats']['images_generated']} images, {status['stats']['pdfs_created']} PDFs")
                if status['stats']['errors'] > 0:
                    print(f"⚠️  Errors: {status['stats']['errors']}")
                print(f"⏳ Uptime: {status['uptime']}")
                
                time.sleep(60)  # Update every minute
                
            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested...")
                pipeline.stop_pipeline()
                break
            except Exception as e:
                print(f"Status update error: {e}")
                time.sleep(10)
    
    except Exception as e:
        print(f"Pipeline error: {e}")
        traceback.print_exc()
    
    print("👋 Pipeline shutdown complete")

if __name__ == "__main__":
    main()