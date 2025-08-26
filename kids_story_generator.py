#!/usr/bin/env python3
"""
24/7 Kids Story Generator with Prompt Creation
Continuously generates kid-friendly stories and converts them to coloring book prompts
"""

import os
import random
import time
import threading
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import logging

# Story generation without external LLM dependency - using template-based approach
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KidsStoryGenerator:
    """24/7 Kids story generator with themed story creation"""
    
    def __init__(self):
        self.current_style_index = 0
        self.story_count = 0
        self.running = False
        
        # Art styles rotation - black/white for coloring + cover styles
        self.art_styles = [
            {
                'name': 'Manga',
                'coloring_style': 'manga style black and white line art',
                'cover_style': 'manga anime style with vibrant colors',
                'complexity': 'detailed line art with expressive characters'
            },
            {
                'name': 'Anime', 
                'coloring_style': 'anime style black and white line art',
                'cover_style': 'anime style with bright vivid colors',
                'complexity': 'clean lines with large expressive eyes'
            },
            {
                'name': 'Disney',
                'coloring_style': 'Disney style black and white line art',
                'cover_style': 'Disney animation style with magical colors',
                'complexity': 'classic Disney character design with flowing lines'
            },
            {
                'name': 'Pixar',
                'coloring_style': 'Pixar 3D style black and white line art',
                'cover_style': 'Pixar 3D animation style with warm colors',
                'complexity': 'rounded friendly characters with smooth lines'
            },
            {
                'name': 'Cartoon',
                'coloring_style': 'cartoon style black and white line art',
                'cover_style': 'cartoon style with bright primary colors',
                'complexity': 'simple bold lines perfect for young children'
            },
            {
                'name': 'Ghibli',
                'coloring_style': 'Studio Ghibli style black and white line art',
                'cover_style': 'Studio Ghibli style with natural earth colors',
                'complexity': 'detailed nature scenes with magical elements'
            },
            {
                'name': 'Simple',
                'coloring_style': 'simple black and white line art',
                'cover_style': 'simple illustration with soft pastel colors',
                'complexity': 'very simple lines for toddlers, minimal details'
            },
            {
                'name': 'Pixel',
                'coloring_style': 'pixel art style black and white line art',
                'cover_style': 'pixel art style with retro 8-bit colors',
                'complexity': 'blocky pixel-style characters and scenes'
            },
            {
                'name': 'Modern_KPop',
                'coloring_style': 'modern K-pop style black and white line art',
                'cover_style': 'modern K-pop style with trendy neon colors',
                'complexity': 'stylish modern characters with fashion elements'
            }
        ]
        
        # Story templates and themes
        self.story_themes = [
            "friendship_adventure", "animal_helpers", "magical_journey", 
            "brave_hero", "kindness_wins", "nature_adventure", "space_exploration",
            "underwater_adventure", "fairy_tale_twist", "robot_friends",
            "dragon_friendship", "princess_adventure", "pirate_treasure",
            "jungle_explorer", "arctic_adventure", "castle_mystery",
            "garden_magic", "toy_come_alive", "superhero_kid", "time_travel"
        ]
        
        # Character archetypes for consistency
        self.character_types = {
            "brave_kid": ["Alex", "Sam", "Jordan", "Casey", "Morgan"],
            "animal_friend": ["Buddy the Dog", "Whiskers the Cat", "Chirpy the Bird", "Hoppy the Rabbit"],
            "magical_creature": ["Sparkle the Unicorn", "Glimmer the Fairy", "Wise the Owl", "Crystal the Dragon"],
            "helper_robot": ["Robo-Friend", "Beep-Bot", "Helpful AI", "Friendly Robot"]
        }
        
        # Output directory
        self.output_dir = Path("generated_stories")
        self.output_dir.mkdir(exist_ok=True)
        
        # Story queue for continuous generation
        self.story_queue = []
        self.max_queue_size = 5
        
    def generate_kid_story(self, theme: str, target_age: str = "5-8") -> Dict[str, Any]:
        """Generate a complete kid-friendly story with metadata"""
        
        # Select characters based on theme
        main_character = random.choice(self.character_types["brave_kid"])
        companion = random.choice(self.character_types["animal_friend"])
        
        # Get current art style
        current_style = self.art_styles[self.current_style_index]
        
        # Generate story based on theme
        story_data = self._create_story_by_theme(theme, main_character, companion)
        
        # Add metadata
        story_data.update({
            'id': f"story_{int(time.time())}_{self.story_count}",
            'theme': theme,
            'target_age': target_age,
            'art_style': current_style,
            'main_character': main_character,
            'companion': companion,
            'generated_at': datetime.now().isoformat(),
            'page_count': 20,  # 20 coloring pages + 1 cover
            'consistent_character': True
        })
        
        self.story_count += 1
        return story_data
    
    def _create_story_by_theme(self, theme: str, main_character: str, companion: str) -> Dict[str, Any]:
        """Create story content based on theme"""
        
        story_templates = {
            "friendship_adventure": {
                "title": f"{main_character} and {companion}'s Great Adventure",
                "summary": f"{main_character} meets {companion} and together they go on an amazing adventure, learning about friendship and helping others along the way.",
                "scenes": [
                    f"{main_character} waking up on a sunny morning, excited for adventure",
                    f"{main_character} meeting {companion} in the garden", 
                    f"{main_character} and {companion} discovering a magical path",
                    f"The friends helping a lost butterfly find its family",
                    f"Building a bridge to help forest creatures cross a stream",
                    f"Having a picnic under a big friendly tree",
                    f"Meeting wise old owl who gives them advice",
                    f"Solving a puzzle to unlock a treasure chest",
                    f"Finding magical seeds to plant a flower garden",
                    f"Dancing with woodland creatures in celebration",
                    f"Teaching young animals about sharing and kindness",
                    f"Building a treehouse for forest friends",
                    f"Having a fun race through flower meadows",
                    f"Discovering a secret waterfall behind vines",
                    f"Making friends with shy forest creatures",
                    f"Creating beautiful art with natural materials", 
                    f"Helping clean up the forest environment",
                    f"Having a magical feast with all their new friends",
                    f"Watching beautiful sunset from their favorite hill",
                    f"{main_character} and {companion} promising to be best friends forever"
                ]
            },
            
            "magical_journey": {
                "title": f"{main_character}'s Magical Quest with {companion}",
                "summary": f"{main_character} discovers they have magical powers and with {companion}'s help, they learn to use magic to help others and save their enchanted village.",
                "scenes": [
                    f"{main_character} discovering they can make flowers bloom with their touch",
                    f"{companion} teaching {main_character} about their magical gift",
                    f"Visiting the wise fairy who explains about good magic",
                    f"Learning to create rainbow bridges in the sky",
                    f"Helping sick animals with healing magic",
                    f"Making it rain gently during a drought",
                    f"Creating magical lights to guide lost travelers",
                    f"Building an ice castle for summer fun",
                    f"Turning mean giant into a gentle friend with kindness magic",
                    f"Planting magical garden that grows instantly",
                    f"Creating flying carpets for elderly villagers",
                    f"Making musical flowers that sing happy songs",
                    f"Conjuring warm clothes for cold winter animals",
                    f"Creating magical library where books read themselves",
                    f"Making time slow down for perfect moments with friends",
                    f"Painting the sky with northern lights",
                    f"Creating magical mirror that shows people's good hearts",
                    f"Making magical feast that never runs out",
                    f"Building bridge between human and fairy worlds", 
                    f"{main_character} and {companion} becoming guardians of the magical realm"
                ]
            },
            
            "animal_helpers": {
                "title": f"{main_character} and the Amazing Animal Friends",
                "summary": f"{main_character} learns to communicate with animals and helps them solve problems while {companion} translates and guides the way.",
                "scenes": [
                    f"{main_character} discovering they can understand animal language",
                    f"{companion} introducing {main_character} to forest community",
                    f"Helping mama bird find her lost babies",
                    f"Teaching young bear cubs about forest safety", 
                    f"Organizing animal olympics in the meadow",
                    f"Building homes for animals before winter",
                    f"Creating peace between cats and dogs in town",
                    f"Helping elephant family cross dangerous river",
                    f"Teaching penguins new games to play",
                    f"Saving dolphins from ocean pollution",
                    f"Helping butterflies navigate migration route",
                    f"Creating animal hospital for injured creatures",
                    f"Organizing big animal parade through town",
                    f"Teaching farm animals about friendship",
                    f"Helping zoo animals feel happy and loved",
                    f"Creating playground specifically designed for animals",
                    f"Building communication network between all animals",
                    f"Hosting inter-species talent show",
                    f"Establishing animal-human friendship council",
                    f"{main_character} becoming official animal ambassador"
                ]
            }
        }
        
        # Get template or create generic adventure
        template = story_templates.get(theme, {
            "title": f"{main_character} and {companion}'s Adventure", 
            "summary": f"A wonderful adventure story about {main_character} and their friend {companion}.",
            "scenes": [f"Adventure scene {i+1} with {main_character} and {companion}" for i in range(20)]
        })
        
        return template
    
    def create_coloring_prompts(self, story_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Convert story scenes into detailed coloring book prompts"""
        
        art_style = story_data['art_style']
        main_character = story_data['main_character']
        companion = story_data['companion']
        target_age = story_data['target_age']
        
        # Age-appropriate complexity
        complexity_map = {
            '2-4': 'very simple shapes, thick lines, minimal details',
            '3-6': 'simple shapes, clear outlines, basic details', 
            '5-8': 'moderate detail, defined shapes, some intricate elements',
            '7-10': 'detailed features, complex shapes, fine lines',
            '10+': 'intricate patterns, complex compositions, detailed artwork'
        }
        
        complexity = complexity_map.get(target_age, complexity_map['5-8'])
        
        prompts = []
        
        # Cover prompt (colored)
        cover_prompt = {
            'type': 'cover',
            'prompt': f"children's book cover, {story_data['title']}, {art_style['cover_style']}, {main_character} and {companion}, magical adventure scene, vibrant colors, title text space at top, {complexity}, professional book cover design",
            'scene_description': f"Cover for {story_data['title']}"
        }
        prompts.append(cover_prompt)
        
        # Coloring page prompts (black and white)
        for i, scene in enumerate(story_data['scenes']):
            coloring_prompt = {
                'type': 'coloring_page',
                'page_number': i + 1,
                'prompt': f"coloring book page, {scene}, {art_style['coloring_style']}, {art_style['complexity']}, {complexity}, black and white line art only, pure white background, no shading, no gray areas, thick black outlines, perfect for coloring, high contrast, suitable for ages {target_age}, consistent character design for {main_character} and {companion}",
                'scene_description': scene
            }
            prompts.append(coloring_prompt)
        
        return prompts
    
    def save_story_data(self, story_data: Dict[str, Any], prompts: List[Dict[str, str]]) -> str:
        """Save story and prompts to JSON file"""
        
        complete_data = {
            'story': story_data,
            'prompts': prompts,
            'generation_info': {
                'generator_version': '1.0',
                'total_prompts': len(prompts),
                'cover_prompts': 1,
                'coloring_prompts': len(prompts) - 1
            }
        }
        
        filename = f"story_{story_data['id']}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Story data saved to {filepath}")
        return str(filepath)
    
    def get_next_story_batch(self) -> Dict[str, Any]:
        """Generate next story with prompts using current art style"""
        
        # Select random theme
        theme = random.choice(self.story_themes)
        
        # Generate story
        logger.info(f"Generating story with theme: {theme}, style: {self.art_styles[self.current_style_index]['name']}")
        story_data = self.generate_kid_story(theme)
        
        # Create prompts  
        prompts = self.create_coloring_prompts(story_data)
        
        # Save to file
        filepath = self.save_story_data(story_data, prompts)
        
        # Rotate to next art style
        self.current_style_index = (self.current_style_index + 1) % len(self.art_styles)
        
        return {
            'story_data': story_data,
            'prompts': prompts, 
            'filepath': filepath,
            'ready_for_generation': True
        }
    
    def start_continuous_generation(self, interval_minutes: int = 30):
        """Start 24/7 continuous story generation"""
        
        logger.info(f"Starting 24/7 story generation (every {interval_minutes} minutes)")
        self.running = True
        
        def generation_loop():
            while self.running:
                try:
                    # Generate new story batch if queue not full
                    if len(self.story_queue) < self.max_queue_size:
                        batch = self.get_next_story_batch()
                        self.story_queue.append(batch)
                        logger.info(f"Generated new story batch. Queue size: {len(self.story_queue)}")
                    
                    # Sleep for specified interval
                    time.sleep(interval_minutes * 60)
                    
                except Exception as e:
                    logger.error(f"Error in generation loop: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        # Start generation thread
        self.generation_thread = threading.Thread(target=generation_loop, daemon=True)
        self.generation_thread.start()
        logger.info("24/7 story generation started!")
    
    def get_next_batch_from_queue(self) -> Dict[str, Any]:
        """Get next story batch for image generation"""
        if self.story_queue:
            return self.story_queue.pop(0)
        else:
            # Generate one immediately if queue is empty
            logger.info("Queue empty, generating story batch immediately")
            return self.get_next_story_batch()
    
    def stop_generation(self):
        """Stop continuous generation"""
        self.running = False
        logger.info("Story generation stopped")

def test_story_generator():
    """Test the story generator"""
    
    print("🧪 Testing Kids Story Generator...")
    
    generator = KidsStoryGenerator()
    
    # Generate a test story
    batch = generator.get_next_story_batch()
    
    story = batch['story_data']
    prompts = batch['prompts']
    
    print(f"\n📖 Generated Story:")
    print(f"Title: {story['title']}")
    print(f"Theme: {story['theme']}")  
    print(f"Art Style: {story['art_style']['name']}")
    print(f"Characters: {story['main_character']}, {story['companion']}")
    
    print(f"\n🎨 Generated {len(prompts)} prompts:")
    print(f"Cover prompt: {prompts[0]['prompt'][:100]}...")
    print(f"First coloring prompt: {prompts[1]['prompt'][:100]}...")
    
    print(f"\n✅ Story saved to: {batch['filepath']}")
    print("🎉 Test completed successfully!")

if __name__ == "__main__":
    test_story_generator()