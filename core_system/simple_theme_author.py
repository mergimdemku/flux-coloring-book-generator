#!/usr/bin/env python3
"""
Simple Theme Author - One theme per book, never repeats
For kids - simple, clear, no mixed themes
"""

import json
import random
import hashlib
from pathlib import Path
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleThemeAuthor:
    """
    Simple single-theme coloring books for kids
    One theme per book, never repeats themes or prompts
    """
    
    def __init__(self):
        self.data_dir = Path("generated_books")
        self.data_dir.mkdir(exist_ok=True)
        
        # Output directory for new stories (pipeline picks up from here)
        self.output_dir = Path("new_stories")
        self.output_dir.mkdir(exist_ok=True)
        
        # Old stories directory for duplicate checking
        self.old_stories_dir = Path("old_stories")
        self.old_stories_dir.mkdir(exist_ok=True)
        
        # Track what we've already used
        self.used_themes_file = self.data_dir / "used_themes.json"
        self.used_themes = self._load_used_themes()
        
        # Simple themes for kids - SINGLE THEMES ONLY
        self.theme_database = {
            # ANIMALS
            "dogs": {
                "title": "Dogs",
                "items": ["Husky", "Labrador", "Golden Retriever", "Poodle", "Beagle", 
                         "German Shepherd", "Bulldog", "Chihuahua", "Corgi", "Dalmatian",
                         "Boxer", "Pug", "Rottweiler", "Shih Tzu", "Yorkshire Terrier"]
            },
            "cats": {
                "title": "Cats", 
                "items": ["Persian cat", "Siamese cat", "Maine Coon", "British Shorthair",
                         "Ragdoll cat", "Bengal cat", "Sphynx cat", "Russian Blue",
                         "Scottish Fold", "Tabby cat", "Black cat", "White cat"]
            },
            "dogs_and_cats": {
                "title": "Dogs and Cats",
                "items": ["Friendly dog", "Playful cat", "Sleeping dog", "Jumping cat",
                         "Running dog", "Sitting cat", "Happy dog", "Curious cat",
                         "Big dog", "Small cat", "Fluffy dog", "Sleek cat"]
            },
            "farm_animals": {
                "title": "Farm Animals",
                "items": ["Cow", "Pig", "Sheep", "Goat", "Horse", "Chicken", "Duck",
                         "Turkey", "Donkey", "Rabbit", "Rooster", "Goose"]
            },
            "ocean_animals": {
                "title": "Ocean Animals",
                "items": ["Dolphin", "Whale", "Shark", "Octopus", "Sea turtle", "Jellyfish",
                         "Seahorse", "Starfish", "Crab", "Lobster", "Seal", "Penguin"]
            },
            "birds": {
                "title": "Birds",
                "items": ["Eagle", "Parrot", "Owl", "Peacock", "Flamingo", "Swan",
                         "Robin", "Cardinal", "Blue jay", "Hummingbird", "Dove", "Crow"]
            },
            
            # NATURE
            "flowers": {
                "title": "Flowers",
                "items": ["Sunflower", "Rose", "Tulip", "Daisy", "Lily", "Orchid",
                         "Iris", "Daffodil", "Carnation", "Chrysanthemum", "Peony", "Violet"]
            },
            "roses": {
                "title": "Roses",
                "items": ["Red rose", "Pink rose", "White rose", "Yellow rose", "Orange rose",
                         "Rose bud", "Open rose", "Rose garden", "Single rose", "Rose bouquet",
                         "Climbing rose", "Wild rose"]
            },
            "trees": {
                "title": "Trees",
                "items": ["Oak tree", "Pine tree", "Apple tree", "Cherry tree", "Palm tree",
                         "Willow tree", "Maple tree", "Birch tree", "Christmas tree",
                         "Bonsai tree", "Banana tree", "Orange tree"]
            },
            
            # FOOD
            "fruits": {
                "title": "Fruits",
                "items": ["Apple", "Banana", "Orange", "Strawberry", "Grape", "Watermelon",
                         "Pineapple", "Mango", "Peach", "Cherry", "Pear", "Kiwi"]
            },
            "vegetables": {
                "title": "Vegetables",
                "items": ["Carrot", "Tomato", "Potato", "Cucumber", "Lettuce", "Corn",
                         "Broccoli", "Pepper", "Onion", "Pumpkin", "Eggplant", "Cabbage"]
            },
            "desserts": {
                "title": "Desserts",
                "items": ["Ice cream", "Cake", "Cupcake", "Cookie", "Donut", "Pie",
                         "Chocolate", "Candy", "Lollipop", "Pudding", "Brownie", "Muffin"]
            },
            "mexican_food": {
                "title": "Mexican Food",
                "items": ["Taco", "Burrito", "Quesadilla", "Nachos", "Enchilada", "Tamale",
                         "Guacamole", "Salsa", "Tortilla", "Fajita", "Churro", "Empanada"]
            },
            "japanese_food": {
                "title": "Japanese Food",
                "items": ["Sushi", "Ramen", "Tempura", "Miso soup", "Bento box", "Onigiri",
                         "Udon", "Soba", "Mochi", "Dango", "Takoyaki", "Gyoza"]
            },
            
            # HOME
            "kitchen": {
                "title": "Kitchen",
                "items": ["Kitchen counter", "Dining table", "Refrigerator", "Oven", "Microwave",
                         "Dishwasher", "Sink", "Coffee maker", "Toaster", "Blender",
                         "Kettle", "Mixer"]
            },
            "bedroom": {
                "title": "Bedroom",
                "items": ["Bed", "Pillow", "Blanket", "Nightstand", "Lamp", "Closet",
                         "Dresser", "Mirror", "Window", "Curtains", "Rug", "Chair"]
            },
            "bathroom": {
                "title": "Bathroom",
                "items": ["Bathtub", "Shower", "Toilet", "Sink", "Mirror", "Towel",
                         "Soap", "Shampoo", "Toothbrush", "Bath mat", "Cabinet", "Faucet"]
            },
            
            # VEHICLES
            "cars": {
                "title": "Cars",
                "items": ["Race car", "Police car", "Fire truck", "Ambulance", "School bus",
                         "Taxi", "Truck", "Van", "Sports car", "Electric car", "Jeep", "Convertible"]
            },
            "trains": {
                "title": "Trains",
                "items": ["Steam train", "Bullet train", "Subway train", "Freight train",
                         "Passenger train", "Train engine", "Train car", "Caboose",
                         "Train station", "Train tracks", "Train tunnel", "Train bridge"]
            },
            "airplanes": {
                "title": "Airplanes",
                "items": ["Passenger plane", "Fighter jet", "Helicopter", "Hot air balloon",
                         "Glider", "Seaplane", "Biplane", "Rocket", "Space shuttle",
                         "Drone", "Paper airplane", "Cargo plane"]
            },
            
            # SPORTS
            "sports_balls": {
                "title": "Sports Balls",
                "items": ["Soccer ball", "Basketball", "Football", "Baseball", "Tennis ball",
                         "Golf ball", "Volleyball", "Bowling ball", "Rugby ball",
                         "Cricket ball", "Beach ball", "Ping pong ball"]
            },
            
            # DINOSAURS
            "dinosaurs": {
                "title": "Dinosaurs",
                "items": ["T-Rex", "Triceratops", "Stegosaurus", "Brachiosaurus", "Velociraptor",
                         "Pterodactyl", "Ankylosaurus", "Diplodocus", "Allosaurus",
                         "Parasaurolophus", "Spinosaurus", "Pachycephalosaurus"]
            },
            
            # SPACE
            "space": {
                "title": "Space",
                "items": ["Moon", "Sun", "Earth", "Mars", "Jupiter", "Saturn", "Star",
                         "Comet", "Asteroid", "Space rocket", "Astronaut", "Space station"]
            },
            
            # SEASONS
            "summer": {
                "title": "Summer",
                "items": ["Beach", "Sandcastle", "Beach ball", "Sunglasses", "Ice cream",
                         "Swimming pool", "Beach umbrella", "Flip flops", "Surfboard",
                         "Picnic basket", "Watermelon", "Lemonade"]
            },
            "winter": {
                "title": "Winter",
                "items": ["Snowman", "Snowflake", "Ski", "Sled", "Ice skate", "Mittens",
                         "Scarf", "Winter hat", "Hot chocolate", "Fireplace", "Igloo", "Penguin"]
            },
            
            # CHARACTER THEMES
            "the_dog_benji": {
                "title": "The Dog Benji",
                "items": ["Dog Benji swimming", "Dog Benji eating", "Dog Benji sleeping",
                         "Dog Benji playing", "Dog Benji running", "Dog Benji jumping",
                         "Dog Benji sitting", "Dog Benji barking", "Dog Benji digging",
                         "Dog Benji with ball", "Dog Benji in park", "Dog Benji happy"]
            },
            "princess_lily": {
                "title": "Princess Lily",
                "items": ["Princess Lily in castle", "Princess Lily with crown", "Princess Lily dancing",
                         "Princess Lily reading", "Princess Lily in garden", "Princess Lily with flowers",
                         "Princess Lily at tea party", "Princess Lily with horse", "Princess Lily singing",
                         "Princess Lily with friends", "Princess Lily at ball", "Princess Lily sleeping"]
            },
            
            # CULTURES
            "world_cultures": {
                "title": "World Cultures",
                "items": ["Japanese kimono", "Mexican sombrero", "Indian sari", "Scottish kilt",
                         "Native American headdress", "Chinese dragon", "Egyptian pyramid",
                         "Greek temple", "Italian pizza", "French Eiffel Tower",
                         "Russian matryoshka", "African drum"]
            }
        }
    
    def _load_used_themes(self) -> set:
        """Load list of already used themes"""
        if self.used_themes_file.exists():
            try:
                with open(self.used_themes_file, 'r') as f:
                    data = json.load(f)
                return set(data.get('used_themes', []))
            except:
                pass
        return set()
    
    def _save_used_theme(self, theme_key: str):
        """Mark a theme as used"""
        self.used_themes.add(theme_key)
        with open(self.used_themes_file, 'w') as f:
            json.dump({'used_themes': list(self.used_themes)}, f, indent=2)
    
    def generate_unique_book(self, pages: int = 12) -> Dict[str, Any]:
        """
        Generate a unique single-theme coloring book
        Never repeats themes or uses same prompts
        """
        
        # Find an unused theme
        available_themes = [k for k in self.theme_database.keys() if k not in self.used_themes]
        
        if not available_themes:
            logger.warning("All themes used! Starting fresh rotation.")
            self.used_themes = set()
            available_themes = list(self.theme_database.keys())
        
        # Pick a theme
        theme_key = random.choice(available_themes)
        theme_data = self.theme_database[theme_key]
        
        # Generate unique ID
        book_id = hashlib.md5(f"{theme_key}-{len(self.used_themes)}".encode()).hexdigest()[:8].upper()
        
        # Build the book
        book = {
            "title": f"{theme_data['title']} Coloring Book {book_id}",
            "theme": theme_key,
            "theme_title": theme_data['title'],
            "total_pages": pages,
            "unique_id": book_id,
            "prompts": []
        }
        
        # Shuffle items for this book
        items = theme_data['items'].copy()
        random.shuffle(items)
        
        # COVER PROMPT - Pipeline format
        cover_items = items[:4] if len(items) >= 4 else items
        cover_prompt = {
            "type": "cover",
            "character": f"{theme_data['title']} collection",
            "scene": f"{', '.join(cover_items)} together",
            "negative": "text, words, letters, writing, numbers, watermark",
            "scene_description": "Cover"
        }
        book['prompts'].append(cover_prompt)
        
        # CONTENT PAGES - Simple, clear prompts
        for i in range(min(pages - 1, len(items))):
            item = items[i]
            
            # Simple, clear prompt for each item
            if "dog" in theme_key.lower() or "cat" in theme_key.lower():
                # Animal themes get action/location
                actions = ["playing", "sleeping", "eating", "running", "sitting", "jumping"]
                locations = ["in garden", "at home", "in park", "on grass", "near tree", "with toy"]
                prompt_text = f"{item} {random.choice(actions)} {random.choice(locations)}"
            else:
                # Object themes are just the object
                prompt_text = f"{item}"
            
            content_prompt = {
                "type": "coloring_page",
                "page_number": i + 1,
                "character": item,
                "scene": prompt_text,
                "scene_objects": [],
                "negative": "text, words, letters, shading, gray, colors, complex details",
                "scene_description": f"Page {i + 1}: {item}",
                "scene_visual": prompt_text
            }
            book['prompts'].append(content_prompt)
        
        # Mark theme as used
        self._save_used_theme(theme_key)
        
        # Save book as JSON file for pipeline processing
        self._save_book_file(book)
        
        logger.info(f"✅ Generated: {book['title']} ({pages} pages)")
        return book
    
    def _save_book_file(self, book: Dict[str, Any]):
        """Save generated book as JSON file in new_stories for pipeline pickup"""
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{book['theme']}_{book['unique_id']}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Create pipeline-compatible format
        pipeline_data = {
            'story': book,
            'prompts': book['prompts']
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(pipeline_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved: {filepath}")
        return str(filepath)
    
    def _check_existing_stories(self) -> set:
        """Check both new_stories and old_stories for existing titles/themes"""
        existing_stories = set()
        
        # Check new_stories folder
        for json_file in self.output_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'story' in data and 'title' in data['story']:
                    title = data['story']['title']
                    theme = data['story'].get('theme', 'unknown')
                    existing_stories.add(f"{theme}_{title}")
            except:
                continue
        
        # Check old_stories folder  
        for json_file in self.old_stories_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'story' in data and 'title' in data['story']:
                    title = data['story']['title']
                    theme = data['story'].get('theme', 'unknown')
                    existing_stories.add(f"{theme}_{title}")
            except:
                continue
                
        logger.info(f"Found {len(existing_stories)} existing stories across both folders")
        return existing_stories
    
    def _is_duplicate_story(self, book: Dict[str, Any]) -> bool:
        """Check if this book would be a duplicate"""
        existing = self._check_existing_stories()
        book_identifier = f"{book['theme']}_{book['title']}"
        return book_identifier in existing
    
    def run_continuous_generation(self, interval_minutes: int = 10):
        """Run continuous story generation every X minutes"""
        import time
        
        logger.info(f"🚀 Starting Continuous Simple Theme Author")
        logger.info(f"📁 Output: {self.output_dir}")
        logger.info(f"⏰ Generation interval: {interval_minutes} minutes")
        logger.info(f"🎨 Available themes: {len(self.theme_database)}")
        
        generation_count = 0
        
        while True:
            try:
                logger.info(f"📚 Starting generation #{generation_count + 1}")
                
                # Generate new book
                book = self.generate_unique_book(12)
                
                if book:
                    generation_count += 1
                    logger.info(f"✅ Generated #{generation_count}: {book['title']}")
                    logger.info(f"📊 Total themes used: {len(self.used_themes)}/{len(self.theme_database)}")
                else:
                    logger.warning("❌ Failed to generate book")
                
                # Wait for next generation
                wait_seconds = interval_minutes * 60
                logger.info(f"💤 Waiting {interval_minutes} minutes until next generation...")
                time.sleep(wait_seconds)
                
            except KeyboardInterrupt:
                logger.info(f"⏹️  Stopping continuous generation (user interrupt)")
                logger.info(f"📊 Final stats: {generation_count} books generated")
                break
                
            except Exception as e:
                logger.error(f"❌ Error in continuous generation: {e}")
                logger.info("⏰ Waiting 2 minutes before retry...")
                time.sleep(120)  # Wait 2 minutes on error

# Global instance
simple_author = SimpleThemeAuthor()

def generate_simple_book(pages: int = 12) -> Dict[str, Any]:
    """Generate a simple single-theme coloring book"""
    return simple_author.generate_unique_book(pages)

def run_continuous_author(interval_minutes: int = 10):
    """Run the continuous simple theme author"""
    simple_author.run_continuous_generation(interval_minutes)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "continuous":
        # Continuous mode - generate every 10 minutes
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print(f"Starting continuous generation every {interval} minutes...")
        print("Press Ctrl+C to stop")
        run_continuous_author(interval)
    else:
        # Single generation test
        book = generate_simple_book(12)
        print(f"Generated: {book['title']}")
        print(f"Theme: {book['theme_title']}")
        print(f"Pages: {book['total_pages']}")
        print("\nSample prompts:")
        print(f"Cover: {book['prompts'][0]['character']} - {book['prompts'][0]['scene']}")
        print(f"Page 1: {book['prompts'][1]['character']} - {book['prompts'][1]['scene']}")
        print("\nTo run continuous generation:")
        print("python3 core_system/simple_theme_author.py continuous [minutes]")