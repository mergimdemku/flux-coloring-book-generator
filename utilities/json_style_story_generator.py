#!/usr/bin/env python3
"""
JSON-Style Story Generator - Creates stories with SPECIFIC visual descriptions like magic_garden.json
"""

import random
import time
import json
from typing import Dict, List, Any
from pathlib import Path

class JsonStyleStoryGenerator:
    """Generates stories with concrete, visual scene descriptions"""
    
    def __init__(self):
        random.seed(int(time.time() * 1000000) % 2147483647)
        
        # Fixed style for consistency (like magic_garden.json)
        self.coloring_style = "black-and-white coloring page, kid-friendly, thick clean outlines, minimal detail, high contrast, no grayscale, no text"
        self.negative_style = "color, grey, shading, gradients, tiny patterns, cluttered backgrounds, logos, watermarks, photorealism, text, numbers, letters, words"
        
        # Character types with specific visual traits
        self.characters = [
            {"name": "Bunny Pip", "desc": "cute bunny with floppy ears", "trait": "tiny blue bow"},
            {"name": "Bear Milo", "desc": "friendly bear with round belly", "trait": "honey pot"},
            {"name": "Fox Luna", "desc": "clever fox with bushy tail", "trait": "little satchel"},
            {"name": "Mouse Tiny", "desc": "small mouse with big eyes", "trait": "cheese wedge hat"},
            {"name": "Cat Whiskers", "desc": "fluffy cat with long whiskers", "trait": "yarn ball"},
            {"name": "Dog Buddy", "desc": "happy dog with wagging tail", "trait": "collar with star"},
            {"name": "Owl Hoot", "desc": "wise owl with big round eyes", "trait": "tiny glasses"},
            {"name": "Rabbit Hoppy", "desc": "energetic rabbit with long ears", "trait": "carrot backpack"},
            {"name": "Duck Waddles", "desc": "yellow duck with orange beak", "trait": "sailor hat"},
            {"name": "Pig Oinky", "desc": "pink pig with curly tail", "trait": "mud boots"}
        ]
        
        # Settings with specific visual elements
        self.settings = [
            {"name": "Rainbow Valley", "elements": ["curved rainbow arch", "puffy clouds", "rolling hills"]},
            {"name": "Crystal Cave", "elements": ["sparkling crystals", "stone formations", "glowing pools"]},
            {"name": "Candy Forest", "elements": ["lollipop trees", "gummy bushes", "chocolate path"]},
            {"name": "Cloud Kingdom", "elements": ["fluffy cloud platforms", "rainbow bridges", "star decorations"]},
            {"name": "Underwater Palace", "elements": ["coral towers", "bubble windows", "seaweed curtains"]},
            {"name": "Toy Land", "elements": ["building blocks", "toy train tracks", "teddy bear houses"]},
            {"name": "Garden Paradise", "elements": ["giant flowers", "mushroom seats", "butterfly paths"]},
            {"name": "Moon Base", "elements": ["crater homes", "star windows", "rocket ships"]},
            {"name": "Tree Village", "elements": ["tree houses", "rope bridges", "leaf umbrellas"]},
            {"name": "Desert Oasis", "elements": ["palm trees", "sand dunes", "water springs"]}
        ]
        
        # Quest objects with visual descriptions
        self.quest_objects = [
            {"name": "Golden Star", "desc": "five-pointed star with sparkles"},
            {"name": "Magic Flower", "desc": "flower with glowing petals"},
            {"name": "Crystal Heart", "desc": "heart-shaped crystal"},
            {"name": "Rainbow Gem", "desc": "round gem with rainbow swirls"},
            {"name": "Moon Pearl", "desc": "glowing round pearl"},
            {"name": "Sun Diamond", "desc": "diamond with sun rays"},
            {"name": "Wish Seed", "desc": "seed with spiral pattern"},
            {"name": "Dream Feather", "desc": "large feather with stars"},
            {"name": "Music Bell", "desc": "bell with musical notes"},
            {"name": "Friendship Ring", "desc": "ring with connected hearts"}
        ]
        
        # Friends to meet (specific visual descriptions)
        self.friends = [
            {"name": "Butterfly Belle", "desc": "butterfly with big patterned wings"},
            {"name": "Snail Shelly", "desc": "snail with spiral shell"},
            {"name": "Frog Freddy", "desc": "green frog on lily pad"},
            {"name": "Bird Chirpy", "desc": "small bird with musical notes"},
            {"name": "Squirrel Nutkin", "desc": "squirrel holding acorn"},
            {"name": "Turtle Tuck", "desc": "turtle with geometric shell"},
            {"name": "Ladybug Dot", "desc": "ladybug with seven spots"},
            {"name": "Bee Buzzy", "desc": "bee with striped body"},
            {"name": "Ant Andy", "desc": "ant carrying leaf piece"},
            {"name": "Spider Webby", "desc": "friendly spider on web"}
        ]
    
    def generate_story(self) -> Dict[str, Any]:
        """Generate a complete story in magic_garden.json style"""
        
        # Select random elements
        character = random.choice(self.characters)
        setting = random.choice(self.settings)
        quest_object = random.choice(self.quest_objects)
        
        # Create title
        title = f"{character['name']}'s {setting['name']} Adventure"
        
        # Generate pages with SPECIFIC visual descriptions
        pages = self.generate_visual_pages(character, setting, quest_object)
        
        # Create cover prompt (SPECIFIC, not generic)
        cover_prompt = f"{character['desc']} with {character['trait']} standing in {setting['name']}; {quest_object['desc']} floating above; {setting['elements'][0]} in background; {setting['elements'][1]} at sides; simple composition, large shapes"
        
        return {
            "book": {
                "title": title,
                "age_range": "4-7",
                "paper": {"size": "8.5x11in", "dpi": 300, "orientation": "portrait"},
                "style": self.coloring_style,
                "negative": self.negative_style,
                "cover_prompt": cover_prompt,
                "back_blurb": f"Join {character['name']} on a magical quest through {setting['name']} to find the {quest_object['name']}!",
                "pages": pages
            }
        }
    
    def generate_visual_pages(self, character: Dict, setting: Dict, quest: Dict) -> List[Dict]:
        """Generate 20 pages with SPECIFIC visual scene descriptions"""
        
        pages = []
        friends = random.sample(self.friends, 6)  # Select 6 random friends to meet
        
        # Page 1-3: Introduction
        pages.append({
            "id": 1, 
            "text": f"Good morning, {character['name']}! A new adventure awaits.",
            "scene": f"{character['desc']} with {character['trait']} waking up; sun circle behind; {setting['elements'][0]} visible through window"
        })
        
        pages.append({
            "id": 2,
            "text": f"The path to {setting['name']} opens before you.",
            "scene": f"arched entrance with {setting['elements'][0]}; {character['desc']} approaching; {setting['elements'][1]} framing sides"
        })
        
        pages.append({
            "id": 3,
            "text": f"A wise voice speaks of the {quest['name']}.",
            "scene": f"owl on branch pointing wing; {quest['desc']} shown in thought bubble; {character['desc']} listening below"
        })
        
        # Pages 4-9: Meeting friends
        for i, friend in enumerate(friends[:6], start=4):
            pages.append({
                "id": i,
                "text": f"{friend['name'].split()[0]} offers to help.",
                "scene": f"{friend['desc']}; {character['desc']} shaking hands/paws; {setting['elements'][i % 3]} in background"
            })
        
        # Pages 10-15: Challenges and puzzles
        pages.append({
            "id": 10,
            "text": "A river blocks the way forward.",
            "scene": f"{character['desc']} at river edge; stepping stones visible; {friends[0]['desc']} pointing across"
        })
        
        pages.append({
            "id": 11,
            "text": "Three paths appear - which one to choose?",
            "scene": f"three simple paths splitting; {character['desc']} thinking; signpost with symbols"
        })
        
        pages.append({
            "id": 12,
            "text": "A gentle giant needs a friend.",
            "scene": f"large sad creature sitting; {character['desc']} offering {character['trait']}; tears becoming smiles"
        })
        
        pages.append({
            "id": 13,
            "text": "The bridge of kindness appears.",
            "scene": f"rainbow bridge forming; {character['desc']} and friends holding hands; hearts floating"
        })
        
        pages.append({
            "id": 14,
            "text": "Dancing lights show the way.",
            "scene": f"fireflies in spiral pattern; {character['desc']} following; {setting['elements'][2]} glowing"
        })
        
        pages.append({
            "id": 15,
            "text": "A puzzle door needs solving.",
            "scene": f"door with shape slots; {character['desc']} holding shapes; friends helping"
        })
        
        # Pages 16-18: Finding the quest object
        pages.append({
            "id": 16,
            "text": f"The {quest['name']} glows in a secret place.",
            "scene": f"{quest['desc']} on pedestal; {character['desc']} reaching up; magical sparkles around"
        })
        
        pages.append({
            "id": 17,
            "text": "Friends celebrate the discovery!",
            "scene": f"{character['desc']} holding {quest['desc']}; all friends dancing in circle; confetti shapes"
        })
        
        pages.append({
            "id": 18,
            "text": f"The {quest['name']} grants a special wish.",
            "scene": f"{quest['desc']} glowing bright; wish bubbles showing happy scenes; {character['desc']} smiling"
        })
        
        # Pages 19-20: Return home
        pages.append({
            "id": 19,
            "text": "Time to share the magic with everyone.",
            "scene": f"{character['desc']} showing {quest['desc']} to group; rainbow connecting everyone; hearts floating"
        })
        
        pages.append({
            "id": 20,
            "text": f"{character['name']} returns home with new friends.",
            "scene": f"{character['desc']} waving goodbye; friend silhouettes waving back; sunset arc; home visible"
        })
        
        return pages


if __name__ == "__main__":
    generator = JsonStyleStoryGenerator()
    
    # Generate a story
    story = generator.generate_story()
    
    # Save to file
    output_path = Path("generated_stories") / f"story_{int(time.time())}.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(story, f, indent=2, ensure_ascii=False)
    
    print(f"Generated story: {story['book']['title']}")
    print(f"Saved to: {output_path}")
    print(f"\nCover prompt: {story['book']['cover_prompt']}")
    print(f"\nFirst scene: {story['book']['pages'][0]['scene']}")
    print(f"\nThis style is MUCH BETTER for AI generation!")