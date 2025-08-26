#!/usr/bin/env python3
"""
IMPROVED Story Generator with Real Narratives
Creates actual stories with beginning, middle, end and unique scenes
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedStoryGenerator:
    """Generates REAL stories with actual narrative progression"""
    
    def __init__(self):
        self.current_style_index = 0
        self.story_count = 0
        self.running = False
        
        # Art styles rotation
        self.art_styles = [
            {
                'name': 'Manga',
                'coloring_style': 'manga style black and white line art, clean sharp lines, high contrast',
                'cover_style': 'manga anime style with vibrant colors, professional cover art',
                'complexity': 'detailed clean line art with expressive characters'
            },
            {
                'name': 'Anime', 
                'coloring_style': 'anime style black and white line art, crisp clean lines, perfect outlines',
                'cover_style': 'anime style with bright vivid colors, professional anime cover',
                'complexity': 'clean precise lines with large expressive eyes'
            },
            {
                'name': 'Disney',
                'coloring_style': 'Disney style black and white line art, smooth clean lines, classic style',
                'cover_style': 'Disney animation style with magical colors, professional Disney cover',
                'complexity': 'classic Disney character design with flowing clean lines'
            },
            {
                'name': 'Pixar',
                'coloring_style': 'Pixar 3D style black and white line art, clean smooth lines',
                'cover_style': 'Pixar 3D animation style with warm colors, professional 3D cover',
                'complexity': 'rounded friendly characters with clean smooth lines'
            },
            {
                'name': 'Cartoon',
                'coloring_style': 'cartoon style black and white line art, bold clean lines',
                'cover_style': 'cartoon style with bright primary colors, fun cartoon cover',
                'complexity': 'simple bold clean lines perfect for young children'
            },
            {
                'name': 'Ghibli',
                'coloring_style': 'Studio Ghibli style black and white line art, delicate clean lines',
                'cover_style': 'Studio Ghibli style with natural earth colors, magical Ghibli cover',
                'complexity': 'detailed nature scenes with magical elements, clean line work'
            },
            {
                'name': 'Simple',
                'coloring_style': 'simple black and white line art, very clean thick lines',
                'cover_style': 'simple illustration with soft pastel colors, clean simple cover',
                'complexity': 'very simple clean lines for toddlers, minimal details, thick outlines'
            },
            {
                'name': 'Pixel',
                'coloring_style': 'pixel art style black and white line art, blocky clean edges',
                'cover_style': 'pixel art style with retro 8-bit colors, pixel art cover',
                'complexity': 'blocky pixel-style characters with clean pixel edges'
            },
            {
                'name': 'Modern_KPop',
                'coloring_style': 'modern K-pop style black and white line art, stylish clean lines',
                'cover_style': 'modern K-pop style with trendy neon colors, fashionable cover',
                'complexity': 'stylish modern characters with fashion elements, clean trendy lines'
            }
        ]
        
        # REAL story templates with actual narrative progression
        self.complete_stories = {
            "dragon_friendship": {
                "title": "The Friendly Dragon's New Home",
                "summary": "Little Emma discovers a lonely dragon in the forest and helps him find a new home where he can be happy and make friends.",
                "scenes": [
                    "Emma walking through the enchanted forest picking flowers",
                    "Emma discovering a sad dragon hiding behind a large tree", 
                    "Emma and the dragon sitting together as she listens to his problem",
                    "The dragon showing Emma his old cave that became too small",
                    "Emma and the dragon searching for a perfect new home together",
                    "They find a beautiful mountain cave with a crystal lake",
                    "Emma helping the dragon decorate his new cave with colorful gems",
                    "The dragon practicing flying around his new mountain home",
                    "Village children meeting the friendly dragon for the first time",
                    "The dragon giving the children rides around the mountain",
                    "Emma and friends having a picnic with the dragon by the lake",
                    "The dragon teaching the children about nature and magic",
                    "Everyone working together to plant a beautiful garden",
                    "The dragon using his fire breath to help cook a feast",
                    "All the forest animals coming to welcome the dragon",
                    "The dragon and Emma reading stories under the stars",
                    "The dragon protecting the village from a terrible storm",
                    "The grateful villagers throwing a celebration party",
                    "Emma and the dragon watching the sunset from the mountain top",
                    "The dragon and all his new friends living happily together"
                ]
            },
            
            "ocean_adventure": {
                "title": "Marina's Underwater Treasure Hunt",
                "summary": "Young Marina discovers she can breathe underwater and embarks on an amazing ocean adventure to find a lost treasure and help sea creatures in need.",
                "scenes": [
                    "Marina playing on the beach and finding a magical seashell",
                    "The seashell glowing and giving Marina the power to breathe underwater",
                    "Marina diving into the ocean for the first time and meeting colorful fish",
                    "A wise old turtle telling Marina about the lost treasure of friendship",
                    "Marina swimming through a beautiful coral reef garden",
                    "Meeting a family of dolphins who need help finding their lost baby",
                    "Marina and the dolphins searching through underwater caves",
                    "Finding the baby dolphin trapped in old fishing nets",
                    "Marina carefully freeing the baby dolphin with help from sea horses",
                    "The grateful dolphin family showing Marina a secret underwater city",
                    "Marina meeting the seahorse king who guards the treasure",
                    "The king explaining that the real treasure is helping others",
                    "Marina helping to clean plastic from the ocean with whale friends",
                    "Building a new home for hermit crabs using clean shells",
                    "Teaching young fish how to stay safe from dangerous currents",
                    "Marina discovering she can talk to all sea creatures",
                    "Organizing a grand underwater parade with all her new friends",
                    "The seahorse king giving Marina a special pearl of kindness",
                    "Marina promising to protect the ocean and visit often",
                    "Marina returning to the beach as the ocean waves goodbye"
                ]
            },
            
            "space_explorer": {
                "title": "Captain Luna's Cosmic Quest",
                "summary": "Brave Captain Luna builds a rocket ship and travels to different planets to help alien friends solve problems and bring peace to the galaxy.",
                "scenes": [
                    "Luna in her backyard workshop building a rocket ship from cardboard and dreams",
                    "The rocket magically coming to life and taking Luna to space",
                    "Luna's first view of Earth from space, seeing how beautiful it is",
                    "Landing on the Moon and meeting friendly Moon rabbits",
                    "The Moon rabbits asking Luna to help find their lost Moon cheese",
                    "Luna and the rabbits exploring Moon craters and space caves",
                    "Discovering the cheese was stolen by grumpy space pirates",
                    "Luna cleverly trading Earth carrots for the Moon cheese",
                    "Flying to Mars and meeting red rock creatures who are very sad",
                    "Learning that Mars creatures miss having water and plants",
                    "Luna bringing Earth seeds and helping plant the first Mars garden",
                    "The Mars creatures learning to care for their new plants",
                    "Traveling to Jupiter and meeting cloud dancers in the storm",
                    "The cloud dancers teaching Luna how to dance among the stars",
                    "Luna helping resolve a conflict between Mars and Jupiter friends",
                    "Organizing a peaceful meeting between all the planet creatures",
                    "Everyone working together to build a friendship space station",
                    "Luna teaching Earth games to all her new alien friends",
                    "A big celebration party with creatures from every planet",
                    "Luna returning home with a heart full of cosmic friendships"
                ]
            },
            
            "forest_magic": {
                "title": "Willow and the Enchanted Grove",
                "summary": "Young Willow discovers she can understand animals and must help save the magical forest from losing its colors and magic.",
                "scenes": [
                    "Willow walking in the forest when she hears animals talking",
                    "A worried squirrel telling Willow that the forest magic is fading",
                    "Willow seeing that flowers and trees are losing their bright colors",
                    "Meeting the wise owl who explains about the missing Rainbow Crystal",
                    "Willow and her animal friends beginning their quest to find the crystal",
                    "Following a trail of sparkling dust through the deep forest",
                    "Crossing a babbling brook with help from friendly beavers",
                    "Climbing a tall mountain with encouragement from mountain goats",
                    "Finding a dark cave where the crystal might be hidden",
                    "Meeting a lonely troll who has been guarding the crystal",
                    "Learning that the troll took the crystal because he was sad and alone",
                    "Willow befriending the troll and inviting him to join the forest community",
                    "The troll happily returning the Rainbow Crystal to its proper place",
                    "The crystal's light immediately restoring color to the forest",
                    "All the flowers blooming brighter and more beautiful than before",
                    "The forest animals celebrating with a joyful dance party",
                    "Willow teaching the troll how to make friends with other creatures",
                    "The troll becoming the forest's official crystal guardian",
                    "Willow promising to visit and help whenever the forest needs her",
                    "The magical forest thriving with Willow as its special friend"
                ]
            },
            
            "superhero_kid": {
                "title": "Super Sam's First Day",
                "summary": "Sam discovers he has superpowers on his first day at a new school and learns that the greatest power is being kind and helping others.",
                "scenes": [
                    "Sam waking up nervous about his first day at a new school",
                    "Accidentally using super strength to open his bedroom door too wide",
                    "Sam's mom helping him practice controlling his new powers",
                    "Arriving at school and trying to act normal around other kids",
                    "Sam's super hearing picking up someone crying for help",
                    "Finding a cat stuck high up in the school playground tree",
                    "Carefully using his flying power to rescue the scared cat",
                    "The other kids amazed and wanting to be Sam's friend",
                    "Sam helping a classmate who dropped all their books",
                    "Using super speed to help clean up after art class",
                    "A school bully picking on smaller children at recess",
                    "Sam standing up to the bully using words instead of powers",
                    "Teaching the bully that being kind is much better than being mean",
                    "The former bully apologizing and asking to join their games",
                    "Sam organizing a fun superhero play time for everyone",
                    "Helping the teacher carry heavy boxes without showing his strength",
                    "Sam learning that small acts of kindness are the best superpowers",
                    "Making three new best friends who accept him just as he is",
                    "Sam's mom proud of how he used his powers to help others",
                    "Sam going to bed happy, excited for tomorrow's adventures"
                ]
            }
        }
        
        # Character pools for variety
        self.character_names = {
            "girls": ["Emma", "Luna", "Marina", "Willow", "Aria", "Nova", "Sage", "Dawn"],
            "boys": ["Sam", "Leo", "Oliver", "Finn", "Max", "Kai", "River", "Atlas"],
            "animals": ["Buddy the Dog", "Whiskers the Cat", "Hopper the Rabbit", "Chirpy the Bird", "Zippy the Squirrel"]
        }
        
        self.output_dir = Path("generated_stories")
        self.output_dir.mkdir(exist_ok=True)
        self.story_queue = []
        self.max_queue_size = 5
        
    def select_story_and_customize(self) -> Dict[str, Any]:
        """Select a story template and customize it with random characters"""
        
        # Select random story template
        story_key = random.choice(list(self.complete_stories.keys()))
        base_story = self.complete_stories[story_key].copy()
        
        # Customize with random characters if needed
        if story_key == "dragon_friendship":
            main_char = random.choice(self.character_names["girls"])
            base_story["title"] = f"{main_char} and the Friendly Dragon"
            # Replace Emma with chosen character in all scenes
            base_story["scenes"] = [scene.replace("Emma", main_char) for scene in base_story["scenes"]]
            
        elif story_key == "ocean_adventure":
            main_char = random.choice(self.character_names["girls"])
            base_story["title"] = f"{main_char}'s Underwater Treasure Hunt"
            base_story["scenes"] = [scene.replace("Marina", main_char) for scene in base_story["scenes"]]
            
        elif story_key == "space_explorer":
            main_char = random.choice(self.character_names["girls"] + self.character_names["boys"])
            base_story["title"] = f"Captain {main_char}'s Cosmic Quest"
            base_story["scenes"] = [scene.replace("Luna", main_char) for scene in base_story["scenes"]]
            
        elif story_key == "forest_magic":
            main_char = random.choice(self.character_names["girls"])
            base_story["title"] = f"{main_char} and the Enchanted Grove"
            base_story["scenes"] = [scene.replace("Willow", main_char) for scene in base_story["scenes"]]
            
        elif story_key == "superhero_kid":
            main_char = random.choice(self.character_names["boys"])
            base_story["title"] = f"Super {main_char}'s First Day"
            base_story["scenes"] = [scene.replace("Sam", main_char) for scene in base_story["scenes"]]
        
        # Add companion if needed
        companion = random.choice(self.character_names["animals"])
        
        return {
            "story_template": base_story,
            "main_character": main_char,
            "companion": companion,
            "story_type": story_key
        }
    
    def create_enhanced_prompts(self, story_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create enhanced prompts with NO TEXT on coloring pages"""
        
        art_style = story_data['art_style']
        main_character = story_data['main_character']
        companion = story_data.get('companion', '')
        target_age = story_data.get('target_age', '5-8')
        
        # Age-appropriate complexity
        complexity_map = {
            '2-4': 'very simple shapes, extra thick clean lines, minimal details, toddler-friendly',
            '3-6': 'simple shapes, thick clean outlines, basic details, preschool-friendly', 
            '5-8': 'moderate detail, clean defined shapes, some intricate elements, school-age appropriate',
            '7-10': 'detailed features, complex clean shapes, fine precise lines, older children',
            '10+': 'intricate patterns, complex compositions, detailed clean artwork, advanced'
        }
        
        complexity = complexity_map.get(target_age, complexity_map['5-8'])
        
        prompts = []
        
        # Cover prompt with title integration (COLORED)
        title = story_data['title']
        cover_prompt = {
            'type': 'cover',
            'prompt': f"professional children's book cover, {title} integrated as beautiful clean text in the image, {art_style['cover_style']}, {main_character} and {companion}, magical adventure scene, vibrant colors, title as part of the artwork, {complexity}, high quality cover design, clean typography, full page layout",
            'scene_description': f"Cover for {title} with integrated title text"
        }
        prompts.append(cover_prompt)
        
        # Coloring page prompts (BLACK AND WHITE, NO TEXT)
        for i, scene in enumerate(story_data['scenes']):
            coloring_prompt = {
                'type': 'coloring_page',
                'page_number': i + 1,
                'prompt': f"coloring book page, {scene}, {art_style['coloring_style']}, {art_style['complexity']}, {complexity}, black and white line art only, pure white background, no text, no words, no letters, no page numbers, no shading, no gray areas, thick black outlines, perfect for coloring, high contrast, ultra clean lines, professional line art, suitable for ages {target_age}, consistent character design for {main_character}",
                'scene_description': scene
            }
            prompts.append(coloring_prompt)
        
        return prompts
    
    def generate_complete_story(self) -> Dict[str, Any]:
        """Generate a complete story with real narrative"""
        
        # Get current art style
        current_style = self.art_styles[self.current_style_index]
        
        # Select and customize story
        story_setup = self.select_story_and_customize()
        story_template = story_setup["story_template"]
        
        # Create complete story data
        story_data = {
            'id': f"story_{int(time.time())}_{self.story_count}",
            'title': story_template['title'],
            'summary': story_template['summary'],
            'scenes': story_template['scenes'],
            'theme': story_setup['story_type'],
            'target_age': '5-8',  # Default age range
            'art_style': current_style,
            'main_character': story_setup['main_character'],
            'companion': story_setup['companion'],
            'generated_at': datetime.now().isoformat(),
            'page_count': 20,
            'consistent_character': True,
            'story_type': 'complete_narrative'
        }
        
        return story_data
    
    def get_next_story_batch(self) -> Dict[str, Any]:
        """Generate next complete story batch"""
        
        logger.info(f"Generating complete story with style: {self.art_styles[self.current_style_index]['name']}")
        
        # Generate real story
        story_data = self.generate_complete_story()
        
        # Create enhanced prompts
        prompts = self.create_enhanced_prompts(story_data)
        
        # Save to file
        filepath = self.save_story_data(story_data, prompts)
        
        # Rotate to next art style
        self.current_style_index = (self.current_style_index + 1) % len(self.art_styles)
        self.story_count += 1
        
        return {
            'story_data': story_data,
            'prompts': prompts, 
            'filepath': filepath,
            'ready_for_generation': True
        }
    
    def save_story_data(self, story_data: Dict[str, Any], prompts: List[Dict[str, str]]) -> str:
        """Save story and prompts to JSON file"""
        
        complete_data = {
            'story': story_data,
            'prompts': prompts,
            'generation_info': {
                'generator_version': '2.0_improved',
                'total_prompts': len(prompts),
                'cover_prompts': 1,
                'coloring_prompts': len(prompts) - 1,
                'story_type': 'complete_narrative',
                'features': ['real_story_progression', 'no_text_on_coloring_pages', 'clean_lines', 'integrated_cover_title']
            }
        }
        
        filename = f"improved_story_{story_data['id']}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Improved story data saved to {filepath}")
        return str(filepath)

def test_improved_generator():
    """Test the improved story generator"""
    
    print("🧪 Testing Improved Story Generator...")
    
    generator = ImprovedStoryGenerator()
    
    # Generate a test story
    batch = generator.get_next_story_batch()
    
    story = batch['story_data']
    prompts = batch['prompts']
    
    print(f"\n📖 Generated REAL Story:")
    print(f"Title: {story['title']}")
    print(f"Theme: {story['theme']}")  
    print(f"Type: {story['story_type']}")
    print(f"Art Style: {story['art_style']['name']}")
    print(f"Characters: {story['main_character']}, {story['companion']}")
    print(f"Summary: {story['summary'][:100]}...")
    
    print(f"\n📄 First 3 Story Scenes:")
    for i, scene in enumerate(story['scenes'][:3]):
        print(f"  {i+1}. {scene}")
    
    print(f"\n🎨 Generated {len(prompts)} prompts:")
    print(f"Cover prompt includes title integration: {'title' in prompts[0]['prompt'].lower()}")
    print(f"Coloring pages have no text: {'no text' in prompts[1]['prompt']}")
    print(f"Clean lines emphasized: {'clean lines' in prompts[1]['prompt']}")
    
    print(f"\n✅ Improved story saved to: {batch['filepath']}")
    print("🎉 Test completed successfully!")

if __name__ == "__main__":
    test_improved_generator()