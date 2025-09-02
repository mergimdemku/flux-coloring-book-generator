#!/usr/bin/env python3
"""
Book-Author Agent - Continuously generates diverse kids' story/coloring book JSONs
Inspired by ChatGPT stories but with AI creativity for endless variety
"""

import json
import time
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BOOK-AUTHOR] %(message)s')
logger = logging.getLogger(__name__)

class BookAuthorAgent:
    """AI Book Author - Creates endless variety of kids' coloring book stories"""
    
    def __init__(self):
        random.seed(int(time.time() * 1000000) % 2147483647)
        self.new_stories_dir = Path("new_stories")
        self.new_stories_dir.mkdir(exist_ok=True)
        
        self.generation_interval = 600  # 10 minutes between stories
        self.running = False
        self.stories_created = 0
        
        # Initialize story variety database
        self.init_story_elements()
        
    def init_story_elements(self):
        """Initialize massive variety of story elements for creativity"""
        
        # CHARACTER TYPES with specific visual traits
        self.character_types = {
            # ANIMALS
            "forest_animals": [
                {"name": "Bunny Pip", "desc": "cute bunny with floppy ears", "trait": "tiny blue bow", "personality": "curious"},
                {"name": "Fox Finn", "desc": "clever red fox with bushy tail", "trait": "green scarf", "personality": "adventurous"},
                {"name": "Bear Bruno", "desc": "friendly brown bear with round belly", "trait": "honey pot hat", "personality": "gentle"},
                {"name": "Owl Olivia", "desc": "wise owl with big round eyes", "trait": "tiny glasses", "personality": "smart"},
                {"name": "Squirrel Sam", "desc": "energetic squirrel with fluffy tail", "trait": "acorn backpack", "personality": "playful"},
                {"name": "Deer Daisy", "desc": "graceful deer with spots", "trait": "flower crown", "personality": "kind"},
                {"name": "Raccoon Rex", "desc": "mischievous raccoon with mask markings", "trait": "striped bandana", "personality": "funny"}
            ],
            
            "farm_animals": [
                {"name": "Pig Penelope", "desc": "pink pig with curly tail", "trait": "mud boots", "personality": "cheerful"},
                {"name": "Cow Bella", "desc": "spotted cow with big eyes", "trait": "flower hat", "personality": "sweet"},
                {"name": "Horse Henry", "desc": "brown horse with flowing mane", "trait": "western saddle", "personality": "brave"},
                {"name": "Chicken Clucky", "desc": "yellow chicken with red comb", "trait": "tiny apron", "personality": "busy"},
                {"name": "Duck Quacky", "desc": "white duck with orange beak", "trait": "sailor hat", "personality": "adventurous"},
                {"name": "Sheep Shelly", "desc": "fluffy white sheep", "trait": "rainbow wool", "personality": "dreamy"},
                {"name": "Goat Gary", "desc": "white goat with horns", "trait": "bell collar", "personality": "mischievous"}
            ],
            
            "ocean_animals": [
                {"name": "Dolphin Splash", "desc": "friendly dolphin with smile", "trait": "star on forehead", "personality": "playful"},
                {"name": "Turtle Shelly", "desc": "green sea turtle", "trait": "coral shell decorations", "personality": "wise"},
                {"name": "Octopus Ollie", "desc": "purple octopus with eight arms", "trait": "tiny crown", "personality": "helpful"},
                {"name": "Seahorse Sparkle", "desc": "colorful seahorse with curled tail", "trait": "glittery fins", "personality": "magical"},
                {"name": "Crab Snippy", "desc": "red crab with big claws", "trait": "pirate hat", "personality": "brave"},
                {"name": "Whale Wally", "desc": "blue whale with water spout", "trait": "captain's hat", "personality": "gentle giant"}
            ],
            
            "fantasy_creatures": [
                {"name": "Dragon Ember", "desc": "small friendly dragon", "trait": "rainbow scales", "personality": "kind"},
                {"name": "Unicorn Luna", "desc": "white unicorn with horn", "trait": "rainbow mane", "personality": "magical"},
                {"name": "Phoenix Flame", "desc": "colorful phoenix bird", "trait": "golden feathers", "personality": "brave"},
                {"name": "Griffin Gus", "desc": "eagle-lion hybrid", "trait": "golden wings", "personality": "noble"},
                {"name": "Fairy Sparkle", "desc": "tiny fairy with wings", "trait": "flower dress", "personality": "helpful"},
                {"name": "Gnome Gideon", "desc": "small gnome with beard", "trait": "pointy hat", "personality": "wise"}
            ],
            
            # HUMAN PROFESSIONS
            "professions": [
                {"name": "Chef Charlie", "desc": "young chef with apron", "trait": "chef's hat", "profession": "cooking"},
                {"name": "Doctor Lily", "desc": "kind doctor", "trait": "stethoscope", "profession": "healing"},
                {"name": "Firefighter Max", "desc": "brave firefighter", "trait": "red helmet", "profession": "rescue"},
                {"name": "Teacher Emma", "desc": "friendly teacher", "trait": "glasses and books", "profession": "teaching"},
                {"name": "Astronaut Alex", "desc": "space explorer", "trait": "space helmet", "profession": "exploration"},
                {"name": "Artist Aria", "desc": "creative artist", "trait": "paint palette", "profession": "art"},
                {"name": "Pilot Pete", "desc": "airplane pilot", "trait": "aviator goggles", "profession": "flying"}
            ]
        }
        
        # STORY THEMES
        self.story_themes = {
            "adventures": [
                "treasure hunt", "magical journey", "exploring new worlds", "time travel",
                "underwater expedition", "space adventure", "jungle exploration", "mountain climbing"
            ],
            
            "learning": [
                "counting fun", "alphabet discovery", "colors and shapes", "opposites",
                "seasons and weather", "healthy eating", "sharing and caring", "being brave"
            ],
            
            "collections": [
                "zoo animals", "wild animals", "farm animals", "ocean creatures",
                "vehicles and transport", "flowers and plants", "fruits and vegetables",
                "musical instruments", "sports and games", "tools and professions"
            ],
            
            "fantasy": [
                "fairy tale castle", "enchanted forest", "magical creatures", "princess adventure",
                "knight's quest", "wizard's school", "dragon friendship", "unicorn garden"
            ],
            
            "everyday": [
                "family fun", "playground games", "birthday party", "helping at home",
                "going to school", "visiting grandparents", "pet care", "neighborhood friends"
            ]
        }
        
        # SETTINGS with visual elements
        self.settings = {
            "nature": [
                {"name": "Enchanted Forest", "elements": ["tall trees with faces", "mushroom houses", "sparkly streams"]},
                {"name": "Flower Meadow", "elements": ["giant colorful flowers", "butterfly clouds", "rainbow arches"]},
                {"name": "Crystal Cave", "elements": ["glowing crystals", "underground pools", "gem formations"]},
                {"name": "Magic Garden", "elements": ["singing flowers", "fruit trees", "fountain center"]},
                {"name": "Sunny Beach", "elements": ["palm trees", "seashells", "sand castles"]}
            ],
            
            "fantasy": [
                {"name": "Cloud Kingdom", "elements": ["fluffy cloud platforms", "rainbow bridges", "star decorations"]},
                {"name": "Candy Land", "elements": ["lollipop trees", "gummy paths", "chocolate rivers"]},
                {"name": "Toy World", "elements": ["building blocks", "toy trains", "teddy bears"]},
                {"name": "Ice Palace", "elements": ["crystal walls", "frozen fountains", "snowflake patterns"]},
                {"name": "Underwater Palace", "elements": ["coral towers", "bubble windows", "seaweed gardens"]}
            ],
            
            "everyday": [
                {"name": "Cozy Village", "elements": ["small houses", "garden paths", "market squares"]},
                {"name": "Big City", "elements": ["tall buildings", "busy streets", "parks"]},
                {"name": "School Playground", "elements": ["swings and slides", "sandbox", "climbing frames"]},
                {"name": "Farm Countryside", "elements": ["red barn", "green fields", "wooden fences"]},
                {"name": "Neighborhood Park", "elements": ["duck pond", "walking paths", "picnic areas"]}
            ]
        }
    
    def generate_creative_story(self) -> Dict[str, Any]:
        """Generate a completely creative and unique story"""
        
        # Randomly select story type
        story_type = random.choice(list(self.story_themes.keys()))
        theme = random.choice(self.story_themes[story_type])
        
        # Select character type and character
        char_category = random.choice(list(self.character_types.keys()))
        character = random.choice(self.character_types[char_category])
        
        # Select setting
        setting_category = random.choice(list(self.settings.keys()))
        setting = random.choice(self.settings[setting_category])
        
        # Generate quest object or goal
        quest_objects = [
            {"name": "Rainbow Star", "desc": "star with rainbow colors"},
            {"name": "Golden Acorn", "desc": "glowing golden acorn"},
            {"name": "Crystal Heart", "desc": "heart-shaped crystal"},
            {"name": "Magic Feather", "desc": "feather with sparkles"},
            {"name": "Friendship Stone", "desc": "stone with heart symbol"},
            {"name": "Dream Bubble", "desc": "bubble with swirling colors"},
            {"name": "Wisdom Scroll", "desc": "rolled paper with symbols"},
            {"name": "Courage Badge", "desc": "shiny badge with star"},
            {"name": "Kindness Seed", "desc": "seed with glowing center"},
            {"name": "Adventure Map", "desc": "treasure map with X mark"}
        ]
        quest = random.choice(quest_objects)
        
        # Create title based on story type
        if story_type == "collections":
            title = f"{character['name']}'s {theme.title()} Collection"
        elif story_type == "adventures":
            title = f"{character['name']} and the {quest['name']}"
        elif story_type == "learning":
            title = f"{character['name']} Learns About {theme.title()}"
        else:
            title = f"{character['name']}'s {setting['name']} Adventure"
        
        # Generate story pages
        pages = self.generate_creative_pages(character, setting, theme, quest, story_type)
        
        # Create cover prompt with specific visuals
        cover_prompt = f"{character['desc']} with {character['trait']} in {setting['name']}; {quest['desc']} floating nearby; {setting['elements'][0]} in background; {setting['elements'][1]} at sides; simple composition, large shapes, kid-friendly"
        
        return {
            "book": {
                "title": title,
                "age_range": "4-7",
                "paper": {"size": "8.5x11in", "dpi": 300, "orientation": "portrait"},
                "style": "black-and-white coloring page, kid-friendly, thick clean outlines, minimal detail, high contrast, no grayscale, no text",
                "negative": "color, grey, shading, gradients, tiny patterns, cluttered backgrounds, logos, watermarks, photorealism, text, numbers, letters, words",
                "cover_prompt": cover_prompt,
                "back_blurb": f"Join {character['name']} on a wonderful {story_type} adventure in {setting['name']}!",
                "pages": pages,
                "metadata": {
                    "character_type": char_category,
                    "story_type": story_type,
                    "theme": theme,
                    "setting_type": setting_category,
                    "generated_by": "Book-Author-Agent",
                    "generation_time": datetime.now().isoformat()
                }
            }
        }
    
    def generate_creative_pages(self, character: Dict, setting: Dict, theme: str, quest: Dict, story_type: str) -> List[Dict]:
        """Generate 20 pages with creative variety based on story type"""
        
        pages = []
        char_name = character['name']
        char_desc = character['desc']
        char_trait = character['trait']
        setting_name = setting['name']
        setting_elements = setting['elements']
        
        if story_type == "collections":
            # Collection-type stories (like zoo animals, vehicles, etc.)
            collection_items = self.get_collection_items(theme)
            
            pages.append({
                "id": 1,
                "text": f"Welcome to {char_name}'s {theme} adventure!",
                "scene": f"{char_desc} with {char_trait} standing at entrance; welcome sign with pictures; {setting_elements[0]} framing scene"
            })
            
            # Show different items from collection (18 pages)
            for i, item in enumerate(collection_items[:18], start=2):
                pages.append({
                    "id": i,
                    "text": f"Look! {char_name} found a {item['name']}!",
                    "scene": f"{char_desc} pointing at {item['desc']}; {item['details']}; {char_trait} visible; simple background with {setting_elements[i % 3]}"
                })
            
            # Final page
            pages.append({
                "id": 20,
                "text": f"{char_name} learned about so many wonderful things!",
                "scene": f"{char_desc} surrounded by small versions of all the items; happy expression; {setting_elements[0]} in background"
            })
            
        else:
            # Adventure/learning type stories
            pages = self.generate_adventure_pages(character, setting, theme, quest)
        
        return pages
    
    def get_collection_items(self, theme: str) -> List[Dict]:
        """Get items for collection-type stories"""
        
        collections = {
            "zoo animals": [
                {"name": "Lion", "desc": "proud lion with mane", "details": "sitting on rock with tail swishing"},
                {"name": "Elephant", "desc": "grey elephant with trunk", "details": "spraying water playfully"},
                {"name": "Giraffe", "desc": "tall giraffe with spots", "details": "eating leaves from tall tree"},
                {"name": "Monkey", "desc": "playful monkey", "details": "swinging from branch with banana"},
                {"name": "Zebra", "desc": "striped zebra", "details": "running with flowing mane"},
                {"name": "Penguin", "desc": "cute penguin", "details": "sliding on ice with flippers out"},
                {"name": "Tiger", "desc": "orange tiger with stripes", "details": "stretching like a big cat"},
                {"name": "Hippo", "desc": "round hippo", "details": "yawning with big mouth open"},
                {"name": "Kangaroo", "desc": "hopping kangaroo", "details": "with baby in pouch"},
                {"name": "Panda", "desc": "black and white panda", "details": "eating bamboo stick"},
                {"name": "Flamingo", "desc": "pink flamingo", "details": "standing on one leg"},
                {"name": "Seal", "desc": "spotted seal", "details": "balancing ball on nose"},
                {"name": "Parrot", "desc": "colorful parrot", "details": "perched with wings spread"},
                {"name": "Snake", "desc": "friendly snake", "details": "coiled in sunny spot"},
                {"name": "Turtle", "desc": "old turtle", "details": "walking slowly with patient smile"},
                {"name": "Bear", "desc": "brown bear", "details": "fishing at stream"},
                {"name": "Wolf", "desc": "grey wolf", "details": "howling at moon"},
                {"name": "Owl", "desc": "wise owl", "details": "perched on branch with big eyes"}
            ],
            
            "vehicles and transport": [
                {"name": "Fire Truck", "desc": "red fire truck with ladder", "details": "with flashing lights and hose"},
                {"name": "Police Car", "desc": "police car with siren", "details": "with flashing blue lights"},
                {"name": "Ambulance", "desc": "white ambulance", "details": "with red cross symbol"},
                {"name": "School Bus", "desc": "yellow school bus", "details": "with happy children in windows"},
                {"name": "Garbage Truck", "desc": "green garbage truck", "details": "with lifting arm"},
                {"name": "Airplane", "desc": "passenger airplane", "details": "flying through puffy clouds"},
                {"name": "Helicopter", "desc": "rescue helicopter", "details": "with spinning rotors"},
                {"name": "Train", "desc": "steam train", "details": "with puffing smoke"},
                {"name": "Sailboat", "desc": "white sailboat", "details": "with billowing sail"},
                {"name": "Motorcycle", "desc": "red motorcycle", "details": "with rider waving"},
                {"name": "Bicycle", "desc": "blue bicycle", "details": "with basket and bell"},
                {"name": "Truck", "desc": "delivery truck", "details": "with packages in back"},
                {"name": "Tractor", "desc": "green farm tractor", "details": "pulling plow"},
                {"name": "Submarine", "desc": "yellow submarine", "details": "underwater with periscope up"},
                {"name": "Hot Air Balloon", "desc": "colorful hot air balloon", "details": "floating in sky"},
                {"name": "Rocket Ship", "desc": "silver rocket", "details": "blasting off to space"},
                {"name": "Bulldozer", "desc": "yellow bulldozer", "details": "pushing dirt pile"},
                {"name": "Ice Cream Truck", "desc": "colorful ice cream truck", "details": "with musical notes"}
            ]
        }
        
        return collections.get(theme, collections["zoo animals"])
    
    def generate_adventure_pages(self, character: Dict, setting: Dict, theme: str, quest: Dict) -> List[Dict]:
        """Generate adventure-style story pages"""
        
        char_desc = character['desc']
        char_trait = character['trait']
        char_name = character['name']
        setting_elements = setting['elements']
        
        pages = []
        
        # Introduction (pages 1-3)
        pages.extend([
            {
                "id": 1,
                "text": f"Good morning, {char_name}! A new day brings adventure!",
                "scene": f"{char_desc} with {char_trait} waking up; sunrise circle behind; {setting_elements[0]} visible through window"
            },
            {
                "id": 2,
                "text": f"The path to {setting['name']} opens before you.",
                "scene": f"arched entrance with {setting_elements[0]}; {char_desc} approaching with {char_trait}; {setting_elements[1]} framing sides"
            },
            {
                "id": 3,
                "text": f"A wise voice tells of the magical {quest['name']}.",
                "scene": f"owl on branch pointing wing; {quest['desc']} shown in thought bubble; {char_desc} listening with {char_trait}"
            }
        ])
        
        # Journey and friends (pages 4-12)
        friends = [
            "Butterfly Belle with rainbow wings",
            "Snail Speedy with spiral shell",
            "Mouse Tiny with big ears",
            "Bird Chirpy with musical notes",
            "Frog Hoppy on lily pad",
            "Bee Buzzy with stripes",
            "Squirrel Nutkin with acorn",
            "Rabbit Quick with cotton tail",
            "Fox Kit with fluffy tail"
        ]
        
        for i, friend in enumerate(friends[:9], start=4):
            pages.append({
                "id": i,
                "text": f"{char_name} meets {friend.split()[0]} {friend.split()[1]}!",
                "scene": f"{char_desc} with {char_trait} meeting {friend}; friendly handshake; {setting_elements[i % 3]} in background; smiles all around"
            })
        
        # Challenges and quest (pages 13-17)
        pages.extend([
            {
                "id": 13,
                "text": "A gentle stream blocks the way forward.",
                "scene": f"{char_desc} at stream edge with {char_trait}; stepping stones visible; first friend helping point the way"
            },
            {
                "id": 14,
                "text": "Three paths appear - which one leads to the treasure?",
                "scene": f"three winding paths splitting; {char_desc} thinking with {char_trait}; signpost with simple symbols; friends gathered around"
            },
            {
                "id": 15,
                "text": "A riddle door needs solving with friendship!",
                "scene": f"door with heart symbols; {char_desc} and friends working together; {char_trait} glowing; key shapes floating"
            },
            {
                "id": 16,
                "text": f"The magical {quest['name']} appears in a secret grove!",
                "scene": f"{quest['desc']} glowing on flower pedestal; {char_desc} reaching up with {char_trait}; sparkles everywhere; friends cheering"
            },
            {
                "id": 17,
                "text": "Everyone celebrates the wonderful discovery!",
                "scene": f"{char_desc} holding {quest['desc']} with {char_trait}; all friends dancing in circle; confetti shapes; happy expressions"
            }
        ])
        
        # Resolution (pages 18-20)
        pages.extend([
            {
                "id": 18,
                "text": f"The {quest['name']} grants a special wish for everyone!",
                "scene": f"{quest['desc']} glowing bright; wish bubbles showing happy scenes; {char_desc} with {char_trait} surrounded by friends"
            },
            {
                "id": 19,
                "text": "Time to share the magic with the whole world!",
                "scene": f"{char_desc} showing {quest['desc']} to group; rainbow connecting everyone; hearts floating; {char_trait} sparkling"
            },
            {
                "id": 20,
                "text": f"{char_name} returns home with heart full of friendship!",
                "scene": f"{char_desc} with {char_trait} waving goodbye; friend silhouettes waving back; sunset arc; cozy home visible in distance"
            }
        ])
        
        return pages
    
    def save_story(self, story: Dict[str, Any]) -> str:
        """Save generated story to new_stories folder"""
        
        timestamp = int(time.time())
        title_clean = story['book']['title'].replace(' ', '_').replace("'", "").replace(",", "")
        filename = f"story_{title_clean}_{timestamp}.json"
        filepath = self.new_stories_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(story, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📚 Created: {story['book']['title']}")
        logger.info(f"📁 Saved: {filepath}")
        logger.info(f"🎭 Type: {story['book']['metadata']['story_type']} - {story['book']['metadata']['theme']}")
        
        return str(filepath)
    
    def run_continuous(self):
        """Run continuously generating stories"""
        
        logger.info("🎨 Book-Author Agent Starting...")
        logger.info(f"📁 Output: {self.new_stories_dir}")
        logger.info(f"⏰ Interval: {self.generation_interval} seconds")
        logger.info("🚀 Generating endless variety of kids' stories!")
        
        self.running = True
        
        while self.running:
            try:
                # Generate a new creative story
                story = self.generate_creative_story()
                
                # Save to new_stories folder
                self.save_story(story)
                
                self.stories_created += 1
                logger.info(f"📊 Total stories created: {self.stories_created}")
                
                # Wait before next generation
                logger.info(f"😴 Resting for {self.generation_interval} seconds...")
                time.sleep(self.generation_interval)
                
            except KeyboardInterrupt:
                logger.info("⏹️  Book-Author Agent stopping (user interrupt)")
                break
            except Exception as e:
                logger.error(f"❌ Error generating story: {e}")
                time.sleep(30)  # Wait 30 seconds on error
        
        logger.info(f"📖 Book-Author Agent finished. Created {self.stories_created} stories total.")


if __name__ == "__main__":
    author = BookAuthorAgent()
    author.run_continuous()