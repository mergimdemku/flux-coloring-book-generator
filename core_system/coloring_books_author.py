#!/usr/bin/env python3
"""
Coloring Books Author - Generates simple theme-based coloring books
No complex stories - just themed collections of individual images
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [COLORING-BOOKS-AUTHOR] %(message)s')
logger = logging.getLogger(__name__)

class ColoringBooksAuthor:
    """Coloring Books Author - Creates simple theme-based coloring books"""
    
    def __init__(self):
        random.seed(int(time.time() * 1000000) % 2147483647)
        self.new_stories_dir = Path("new_stories")
        self.new_stories_dir.mkdir(exist_ok=True)
        
        self.generation_interval = 300  # 5 minutes between books
        self.running = False
        self.books_created = 0
        
        # Initialize theme database
        self.init_themes()
        
    def init_themes(self):
        """Initialize simple theme-based coloring book elements"""
        
        # SIMPLE THEMES - Each book focuses on ONE theme only
        self.themes = {
            "farm_animals": {
                "title": "Farm Animals Coloring Book",
                "cover_desc": "friendly farm with barn and animals",
                "items": [
                    "cow standing in meadow",
                    "pig rolling in mud", 
                    "chicken pecking grain",
                    "horse running in field",
                    "sheep grazing grass",
                    "duck swimming in pond",
                    "goat climbing rock",
                    "rabbit eating carrot",
                    "cat sleeping in barn",
                    "dog herding sheep"
                ]
            },
            
            "wild_animals": {
                "title": "Wild Animals Coloring Book", 
                "cover_desc": "jungle scene with various wild animals",
                "items": [
                    "lion sitting proudly",
                    "elephant spraying water",
                    "giraffe eating leaves", 
                    "tiger stretching body",
                    "bear catching fish",
                    "wolf howling at moon",
                    "fox in forest",
                    "deer drinking water",
                    "monkey swinging branch",
                    "zebra running plains"
                ]
            },
            
            "ocean_life": {
                "title": "Ocean Life Coloring Book",
                "cover_desc": "underwater scene with coral and sea creatures",
                "items": [
                    "whale swimming deep",
                    "dolphin jumping waves",
                    "shark patrolling waters", 
                    "octopus hiding rocks",
                    "seahorse floating seaweed",
                    "starfish on beach",
                    "crab walking sand",
                    "turtle swimming coral",
                    "fish schooling together",
                    "jellyfish drifting current"
                ]
            },
            
            "kitchen_items": {
                "title": "Kitchen Items Coloring Book",
                "cover_desc": "cozy kitchen with cooking utensils and appliances",
                "items": [
                    "teapot on stove",
                    "mixing bowl with spoon",
                    "cutting board with knife",
                    "frying pan on burner", 
                    "coffee mug steaming",
                    "plate with fork",
                    "glass with juice",
                    "pot with lid",
                    "toaster with bread",
                    "blender with fruit"
                ]
            },
            
            "vehicles": {
                "title": "Vehicles Coloring Book", 
                "cover_desc": "busy street with different vehicles",
                "items": [
                    "car driving road",
                    "truck hauling cargo",
                    "bus picking passengers",
                    "motorcycle racing street",
                    "bicycle in park",
                    "train on tracks",
                    "airplane in sky",
                    "boat on water",
                    "helicopter flying",
                    "tractor in field"
                ]
            },
            
            "flowers": {
                "title": "Beautiful Flowers Coloring Book",
                "cover_desc": "colorful garden with blooming flowers",
                "items": [
                    "rose in garden",
                    "sunflower facing sun",
                    "tulip in spring",
                    "daisy in meadow", 
                    "lily by pond",
                    "orchid in pot",
                    "poppy in field",
                    "iris blooming",
                    "carnation bouquet",
                    "daffodil yellow bright"
                ]
            },
            
            "desert_life": {
                "title": "Desert Life Coloring Book",
                "cover_desc": "desert landscape with cacti and desert animals",
                "items": [
                    "cactus with flowers",
                    "camel walking sand",
                    "snake coiled rock",
                    "lizard on stone",
                    "scorpion hiding",
                    "roadrunner bird",
                    "prairie dog burrow",
                    "owl in cactus",
                    "butterfly on bloom",
                    "desert fox prowling"
                ]
            },
            
            "space_objects": {
                "title": "Space Objects Coloring Book", 
                "cover_desc": "space scene with planets and stars",
                "items": [
                    "rocket ship flying",
                    "planet with rings",
                    "shooting star trail",
                    "astronaut floating",
                    "satellite orbiting",
                    "moon with craters",
                    "space station",
                    "alien spaceship",
                    "comet blazing",
                    "solar system planets"
                ]
            }
        }
    
    def create_theme_based_book(self, theme_name: str) -> Dict[str, Any]:
        """Create a simple theme-based coloring book"""
        
        theme = self.themes[theme_name]
        timestamp = int(time.time())
        
        # Select 10-12 items from theme
        selected_items = random.sample(theme["items"], min(10, len(theme["items"])))
        
        # Create book structure
        book_data = {
            "book": {
                "title": theme["title"],
                "age_range": "4-8",
                "paper": {
                    "size": "8.5x11in",
                    "dpi": 300,
                    "orientation": "portrait"
                },
                "style": "simple black and white line drawing, thick outlines, no shading",
                "negative": "",  # No negative prompts - FLUX.1-schnell doesn't support them
                "cover_prompt": theme["cover_desc"],
                "back_blurb": f"Fun {theme_name.replace('_', ' ')} coloring book for kids!",
                "pages": []
            }
        }
        
        # Create pages - each page is one simple item
        for i, item in enumerate(selected_items, 1):
            page = {
                "id": i,
                "text": f"Color the {item.split()[0]}!",  # Simple text like "Color the cow!"
                "scene": item  # Direct, simple description
            }
            book_data["book"]["pages"].append(page)
        
        # Add metadata
        book_data["book"]["metadata"] = {
            "theme": theme_name,
            "book_type": "theme_based_coloring", 
            "generated_by": "Coloring-Books-Author",
            "generation_time": datetime.now().isoformat()
        }
        
        return book_data
    
    def generate_random_book(self) -> str:
        """Generate a random theme-based coloring book"""
        
        # Pick random theme
        theme_name = random.choice(list(self.themes.keys()))
        
        logger.info(f"Creating {theme_name} themed coloring book...")
        
        # Create book
        book_data = self.create_theme_based_book(theme_name)
        
        # Save to file
        timestamp = int(time.time())
        filename = f"theme_{theme_name}_{timestamp}.json"
        filepath = self.new_stories_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, indent=2, ensure_ascii=False)
        
        self.books_created += 1
        logger.info(f"✅ Created {book_data['book']['title']} -> {filename}")
        logger.info(f"📄 {len(book_data['book']['pages'])} pages generated")
        
        return str(filepath)
    
    def run_continuous_generation(self):
        """Run continuous book generation"""
        logger.info("🚀 Starting Coloring Books Author")
        logger.info(f"📁 Output directory: {self.new_stories_dir}")
        logger.info(f"⏰ Generation interval: {self.generation_interval} seconds")
        
        self.running = True
        
        while self.running:
            try:
                # Generate a book
                self.generate_random_book()
                
                logger.info(f"📊 Total books created: {self.books_created}")
                logger.info(f"💤 Waiting {self.generation_interval} seconds until next book...")
                
                # Wait for next generation
                time.sleep(self.generation_interval)
                
            except KeyboardInterrupt:
                logger.info("⏹️  Stopping Coloring Books Author (user interrupt)")
                self.running = False
                break
                
            except Exception as e:
                logger.error(f"❌ Error generating book: {e}")
                time.sleep(30)  # Wait 30 seconds on error
        
        logger.info(f"🏁 Final count: {self.books_created} books created")


if __name__ == "__main__":
    author = ColoringBooksAuthor()
    author.run_continuous_generation()