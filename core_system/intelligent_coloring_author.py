#!/usr/bin/env python3
"""
Intelligent Coloring Books Author - Self-learning with infinite themes
Generates unique coloring books with NO TEXT and infinite variety
"""

import json
import time
import random
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set
import logging
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [INTELLIGENT-AUTHOR] %(message)s')
logger = logging.getLogger(__name__)

class IntelligentColoringAuthor:
    """Self-learning coloring book author with infinite unique themes"""
    
    def __init__(self):
        random.seed(int(time.time() * 1000000) % 2147483647)
        self.new_stories_dir = Path("new_stories")
        self.new_stories_dir.mkdir(exist_ok=True)
        
        # Database storage
        self.theme_database_file = Path("theme_database.json")
        self.used_combinations_file = Path("used_combinations.json")
        
        self.generation_interval = 120  # 2 minutes between books
        self.running = False
        self.books_created = 0
        
        # Load or initialize databases
        self.theme_database = self.load_theme_database()
        self.used_combinations = self.load_used_combinations()
        
        # If database is empty, initialize with massive variety
        if not self.theme_database or len(self.theme_database.get('all_themes', [])) < 1000:
            logger.info("Building massive theme database...")
            self.build_massive_database()
    
    def load_theme_database(self) -> Dict:
        """Load existing theme database"""
        if self.theme_database_file.exists():
            with open(self.theme_database_file, 'r') as f:
                return json.load(f)
        return {'all_themes': [], 'categories': {}}
    
    def load_used_combinations(self) -> Set[str]:
        """Load used combinations to ensure uniqueness"""
        if self.used_combinations_file.exists():
            with open(self.used_combinations_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def save_databases(self):
        """Save theme database and used combinations"""
        with open(self.theme_database_file, 'w') as f:
            json.dump(self.theme_database, f, indent=2)
        
        with open(self.used_combinations_file, 'w') as f:
            json.dump(list(self.used_combinations), f)
    
    def build_massive_database(self):
        """Build a massive database of unique themes"""
        
        # MASSIVE THEME CATEGORIES
        self.theme_database = {
            'categories': {
                # POKEMON (Generation 1-9)
                'pokemon_gen1': ['Pikachu', 'Charizard', 'Bulbasaur', 'Squirtle', 'Charmander', 'Mewtwo', 'Mew', 'Gengar', 'Dragonite', 'Snorlax', 'Lapras', 'Eevee', 'Vaporeon', 'Jolteon', 'Flareon', 'Articuno', 'Zapdos', 'Moltres', 'Dratini', 'Meowth'],
                'pokemon_gen2': ['Cyndaquil', 'Totodile', 'Chikorita', 'Typhlosion', 'Feraligatr', 'Meganium', 'Espeon', 'Umbreon', 'Lugia', 'Ho-Oh', 'Celebi', 'Suicune', 'Raikou', 'Entei', 'Tyranitar', 'Heracross', 'Scizor', 'Ampharos', 'Crobat', 'Togepi'],
                'pokemon_legendary': ['Arceus', 'Dialga', 'Palkia', 'Giratina', 'Rayquaza', 'Groudon', 'Kyogre', 'Zekrom', 'Reshiram', 'Kyurem', 'Xerneas', 'Yveltal', 'Zygarde', 'Solgaleo', 'Lunala', 'Necrozma', 'Zacian', 'Zamazenta', 'Eternatus', 'Calyrex'],
                
                # DIGIMON
                'digimon_rookie': ['Agumon', 'Gabumon', 'Patamon', 'Gatomon', 'Veemon', 'Guilmon', 'Renamon', 'Terriermon', 'Lopmon', 'Impmon', 'Palmon', 'Tentomon', 'Gomamon', 'Biyomon', 'Hawkmon', 'Armadillomon', 'Wormmon', 'Takato', 'Henry', 'Rika'],
                'digimon_champion': ['Greymon', 'Garurumon', 'Angemon', 'Angewomon', 'ExVeemon', 'Growlmon', 'Kyubimon', 'Gargomon', 'Turuiemon', 'Devimon', 'Togemon', 'Kabuterimon', 'Ikkakumon', 'Birdramon', 'Aquilamon', 'Ankylomon', 'Stingmon', 'Leomon', 'Ogremon', 'Meramon'],
                'digimon_mega': ['WarGreymon', 'MetalGarurumon', 'Omnimon', 'Gallantmon', 'Sakuyamon', 'MegaGargomon', 'Beelzemon', 'Seraphimon', 'Ophanimon', 'Imperialdramon', 'ShineGreymon', 'MirageGaogamon', 'Rosemon', 'Vikemon', 'HerculesKabuterimon', 'Phoenixmon', 'MetalSeadramon', 'Puppetmon', 'Machinedramon', 'Piedmon'],
                
                # DOG BREEDS
                'small_dogs': ['Chihuahua', 'Pomeranian', 'Yorkshire Terrier', 'Maltese', 'Papillon', 'Shih Tzu', 'Pug', 'Boston Terrier', 'French Bulldog', 'Cavalier King Charles', 'Havanese', 'Bichon Frise', 'Cocker Spaniel', 'Miniature Schnauzer', 'Dachshund', 'Corgi', 'Jack Russell', 'Westie', 'Scottish Terrier', 'Toy Poodle'],
                'large_dogs': ['German Shepherd', 'Golden Retriever', 'Labrador', 'Rottweiler', 'Doberman', 'Great Dane', 'Saint Bernard', 'Bernese Mountain Dog', 'Mastiff', 'Newfoundland', 'Irish Wolfhound', 'Akita', 'Alaskan Malamute', 'Siberian Husky', 'Belgian Malinois', 'Rhodesian Ridgeback', 'Weimaraner', 'Vizsla', 'Pointer', 'Setter'],
                
                # CAT BREEDS
                'cat_breeds': ['Persian', 'Maine Coon', 'Siamese', 'Ragdoll', 'Bengal', 'British Shorthair', 'Scottish Fold', 'Sphynx', 'Russian Blue', 'Norwegian Forest', 'Abyssinian', 'Oriental Shorthair', 'Devon Rex', 'Cornish Rex', 'Birman', 'Himalayan', 'Exotic Shorthair', 'Turkish Angora', 'Manx', 'Bombay'],
                
                # WILD CATS
                'wild_cats': ['Lion', 'Tiger', 'Leopard', 'Jaguar', 'Cheetah', 'Cougar', 'Snow Leopard', 'Clouded Leopard', 'Lynx', 'Bobcat', 'Caracal', 'Serval', 'Ocelot', 'Margay', 'Fishing Cat', 'Sand Cat', 'Black-footed Cat', 'Pallas Cat', 'Jungle Cat', 'Wildcat'],
                
                # BIRDS
                'tropical_birds': ['Macaw', 'Toucan', 'Cockatoo', 'Lorikeet', 'Hornbill', 'Quetzal', 'Bird of Paradise', 'Kingfisher', 'Sunbird', 'Hummingbird', 'Flamingo', 'Pelican', 'Ibis', 'Stork', 'Crane', 'Heron', 'Spoonbill', 'Cassowary', 'Kookaburra', 'Lyrebird'],
                'raptors': ['Eagle', 'Hawk', 'Falcon', 'Owl', 'Buzzard', 'Kite', 'Harrier', 'Osprey', 'Secretary Bird', 'Condor', 'Vulture', 'Kestrel', 'Merlin', 'Goshawk', 'Sparrowhawk', 'Peregrine', 'Gyrfalcon', 'Red-tailed Hawk', 'Cooper Hawk', 'Sharp-shinned Hawk'],
                
                # MARINE LIFE
                'sharks': ['Great White', 'Hammerhead', 'Tiger Shark', 'Bull Shark', 'Whale Shark', 'Nurse Shark', 'Reef Shark', 'Mako Shark', 'Thresher Shark', 'Lemon Shark', 'Blue Shark', 'Blacktip Shark', 'Sandbar Shark', 'Goblin Shark', 'Basking Shark', 'Megamouth Shark', 'Cookiecutter Shark', 'Zebra Shark', 'Wobbegong', 'Angel Shark'],
                'whales': ['Blue Whale', 'Humpback Whale', 'Orca', 'Sperm Whale', 'Gray Whale', 'Right Whale', 'Bowhead Whale', 'Minke Whale', 'Fin Whale', 'Sei Whale', 'Bryde Whale', 'Pilot Whale', 'Beluga Whale', 'Narwhal', 'Beaked Whale', 'False Killer Whale', 'Melon-headed Whale', 'Pygmy Sperm Whale', 'Dwarf Sperm Whale', 'Killer Whale'],
                'coral_reef': ['Clownfish', 'Angelfish', 'Butterflyfish', 'Parrotfish', 'Surgeonfish', 'Triggerfish', 'Pufferfish', 'Boxfish', 'Moorish Idol', 'Mandarin Fish', 'Lionfish', 'Seahorse', 'Sea Dragon', 'Pipefish', 'Moray Eel', 'Garden Eel', 'Octopus', 'Cuttlefish', 'Nautilus', 'Sea Turtle'],
                
                # INSECTS
                'butterflies': ['Monarch', 'Swallowtail', 'Blue Morpho', 'Admiral', 'Painted Lady', 'Peacock', 'Tortoiseshell', 'Comma', 'Fritillary', 'Copper', 'Skipper', 'Hairstreak', 'Brimstone', 'Orange Tip', 'Clouded Yellow', 'Holly Blue', 'Common Blue', 'Silver-studded Blue', 'Purple Emperor', 'White Admiral'],
                'beetles': ['Stag Beetle', 'Rhinoceros Beetle', 'Hercules Beetle', 'Goliath Beetle', 'Titan Beetle', 'Scarab Beetle', 'Ladybug', 'Firefly', 'Ground Beetle', 'Tiger Beetle', 'Longhorn Beetle', 'Weevil', 'Click Beetle', 'Dung Beetle', 'Jewel Beetle', 'Bark Beetle', 'Rove Beetle', 'Blister Beetle', 'Leaf Beetle', 'Water Beetle'],
                
                # DINOSAURS
                'carnivore_dinos': ['T-Rex', 'Velociraptor', 'Allosaurus', 'Spinosaurus', 'Giganotosaurus', 'Carnotaurus', 'Dilophosaurus', 'Utahraptor', 'Deinonychus', 'Baryonyx', 'Megalosaurus', 'Ceratosaurus', 'Albertosaurus', 'Daspletosaurus', 'Gorgosaurus', 'Tarbosaurus', 'Acrocanthosaurus', 'Carcharodontosaurus', 'Mapusaurus', 'Megaraptor'],
                'herbivore_dinos': ['Triceratops', 'Stegosaurus', 'Brachiosaurus', 'Diplodocus', 'Ankylosaurus', 'Parasaurolophus', 'Pachycephalosaurus', 'Iguanodon', 'Hadrosaurus', 'Apatosaurus', 'Argentinosaurus', 'Styracosaurus', 'Centrosaurus', 'Protoceratops', 'Psittacosaurus', 'Therizinosaurus', 'Plateosaurus', 'Massospondylus', 'Oviraptor', 'Gallimimus'],
                'flying_dinos': ['Pteranodon', 'Pterodactyl', 'Quetzalcoatlus', 'Dimorphodon', 'Rhamphorhynchus', 'Archaeopteryx', 'Microraptor', 'Yi Qi', 'Anchiornis', 'Confuciusornis', 'Caudipteryx', 'Sinornithosaurus', 'Zhenyuanlong', 'Changyuraptor', 'Ambopteryx', 'Scansoriopteryx', 'Epidexipteryx', 'Pedopenna', 'Jeholornis', 'Sapeornis'],
                
                # MYTHICAL CREATURES
                'dragons': ['Chinese Dragon', 'European Dragon', 'Wyvern', 'Drake', 'Hydra', 'Amphiptere', 'Lindworm', 'Wyrm', 'Lung Dragon', 'Fafnir', 'Smaug-type', 'Ice Dragon', 'Fire Dragon', 'Storm Dragon', 'Earth Dragon', 'Shadow Dragon', 'Crystal Dragon', 'Bone Dragon', 'Fairy Dragon', 'Sea Serpent'],
                'mythical_beasts': ['Phoenix', 'Griffin', 'Pegasus', 'Unicorn', 'Chimera', 'Manticore', 'Basilisk', 'Kraken', 'Cerberus', 'Sphinx', 'Centaur', 'Minotaur', 'Cyclops', 'Medusa', 'Harpy', 'Siren', 'Banshee', 'Valkyrie', 'Fenrir', 'Jormungandr'],
                
                # ROBOTS AND MECHS
                'robots': ['Humanoid Robot', 'Industrial Robot', 'Service Robot', 'Battle Mech', 'Space Robot', 'Underwater Robot', 'Flying Drone', 'Spider Robot', 'Tank Robot', 'Transformer-style', 'Gundam-style', 'EVA Unit', 'Pacific Rim Jaeger', 'Iron Giant type', 'Wall-E type', 'R2D2 type', 'C3PO type', 'Terminator type', 'RoboCop type', 'Optimus Prime type'],
                
                # SPACE
                'planets': ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Exoplanet', 'Gas Giant', 'Rocky Planet', 'Ice Planet', 'Desert Planet', 'Ocean Planet', 'Lava Planet', 'Forest Planet', 'Crystal Planet', 'Ring Planet', 'Binary Planet'],
                'spacecraft': ['Space Shuttle', 'Rocket', 'Space Station', 'Lunar Module', 'Mars Rover', 'Satellite', 'Space Probe', 'Colony Ship', 'Fighter Ship', 'Cargo Ship', 'Explorer Ship', 'Alien UFO', 'Flying Saucer', 'Mothership', 'Space Pod', 'Escape Pod', 'Mining Ship', 'Science Vessel', 'Battlecruiser', 'Starfighter'],
                
                # FANTASY CHARACTERS
                'fantasy_races': ['Elf Warrior', 'Dwarf Fighter', 'Orc Barbarian', 'Goblin Scout', 'Troll Berserker', 'Fairy Queen', 'Dark Elf', 'Wood Elf', 'High Elf', 'Halfling Rogue', 'Gnome Wizard', 'Dragonborn', 'Tiefling', 'Aasimar', 'Genasi', 'Tabaxi', 'Kenku', 'Aarakocra', 'Lizardfolk', 'Kobold'],
                'fantasy_classes': ['Knight', 'Wizard', 'Archer', 'Rogue', 'Paladin', 'Necromancer', 'Druid', 'Ranger', 'Barbarian', 'Monk', 'Cleric', 'Warlock', 'Sorcerer', 'Bard', 'Artificer', 'Alchemist', 'Summoner', 'Death Knight', 'Demon Hunter', 'Shadow Priest'],
                
                # VEHICLES
                'race_cars': ['Formula 1', 'NASCAR', 'Rally Car', 'Drag Racer', 'Le Mans Prototype', 'IndyCar', 'Sprint Car', 'Stock Car', 'Touring Car', 'GT Car', 'Drift Car', 'Hill Climb Car', 'Kart', 'Midget Car', 'Late Model', 'Modified', 'Super Late Model', 'Legends Car', 'Bandolero', 'Trophy Truck'],
                'motorcycles': ['Sport Bike', 'Cruiser', 'Touring Bike', 'Adventure Bike', 'Dirt Bike', 'Supermoto', 'Cafe Racer', 'Bobber', 'Chopper', 'Scrambler', 'Naked Bike', 'Dual Sport', 'Trials Bike', 'Enduro', 'Speedway Bike', 'Drag Bike', 'Street Fighter', 'Bagger', 'Trike', 'Sidecar'],
                'aircraft': ['Fighter Jet', 'Bomber', 'Cargo Plane', 'Passenger Jet', 'Private Jet', 'Helicopter', 'Attack Helicopter', 'Biplane', 'Glider', 'Seaplane', 'Amphibious Plane', 'VTOL', 'Stealth Fighter', 'Drone', 'Airship', 'Blimp', 'Hot Air Balloon', 'Gyrocopter', 'Ultralight', 'Aerobatic Plane'],
                'military': ['Tank', 'APC', 'IFV', 'Artillery', 'MLRS', 'Anti-Aircraft', 'Missile Launcher', 'Armored Car', 'MRAP', 'Humvee', 'Technical', 'Self-Propelled Gun', 'Tank Destroyer', 'Scout Vehicle', 'Command Vehicle', 'Recovery Vehicle', 'Bridge Layer', 'Mine Clearer', 'Amphibious Vehicle', 'Hovercraft'],
                
                # FLOWERS AND PLANTS
                'exotic_flowers': ['Orchid', 'Bird of Paradise', 'Protea', 'Hibiscus', 'Plumeria', 'Bougainvillea', 'Passion Flower', 'Lotus', 'Water Lily', 'Calla Lily', 'Anthurium', 'Heliconia', 'Ginger Flower', 'Frangipani', 'Jasmine', 'Gardenia', 'Magnolia', 'Camellia', 'Azalea', 'Rhododendron'],
                'cacti': ['Saguaro', 'Barrel Cactus', 'Prickly Pear', 'Christmas Cactus', 'Moon Cactus', 'Bunny Ears', 'Old Man Cactus', 'Bishop Cap', 'Star Cactus', 'Pincushion Cactus', 'Hedgehog Cactus', 'Organ Pipe', 'Cholla', 'Fishhook Cactus', 'Golden Barrel', 'Peruvian Apple', 'Rat Tail Cactus', 'Fairy Castle', 'Totem Pole', 'Silver Torch'],
                'trees': ['Oak', 'Maple', 'Pine', 'Birch', 'Willow', 'Cherry Blossom', 'Redwood', 'Sequoia', 'Baobab', 'Banyan', 'Mangrove', 'Joshua Tree', 'Dragon Blood Tree', 'Rainbow Eucalyptus', 'Jacaranda', 'Wisteria Tree', 'Magnolia Tree', 'Dogwood', 'Redbud', 'Ginkgo'],
                
                # FOOD ITEMS
                'fruits': ['Dragon Fruit', 'Star Fruit', 'Durian', 'Rambutan', 'Mangosteen', 'Lychee', 'Passion Fruit', 'Guava', 'Papaya', 'Jackfruit', 'Persimmon', 'Pomegranate', 'Fig', 'Date', 'Quince', 'Elderberry', 'Gooseberry', 'Currant', 'Mulberry', 'Boysenberry'],
                'desserts': ['Macaron', 'Croissant', 'Eclair', 'Tiramisu', 'Cannoli', 'Baklava', 'Mochi', 'Dorayaki', 'Taiyaki', 'Crepe', 'Waffle', 'Churro', 'Beignet', 'Profiterole', 'Madeleine', 'Financier', 'Opera Cake', 'Mont Blanc', 'Pavlova', 'Eton Mess'],
                'sushi': ['Salmon Nigiri', 'Tuna Nigiri', 'California Roll', 'Rainbow Roll', 'Dragon Roll', 'Spider Roll', 'Philadelphia Roll', 'Tempura Roll', 'Sashimi Platter', 'Chirashi Bowl', 'Unagi', 'Ikura', 'Uni', 'Tamago', 'Inari', 'Temaki', 'Maki Roll', 'Inside-out Roll', 'Futomaki', 'Hosomaki'],
                
                # SPORTS EQUIPMENT
                'ball_sports': ['Soccer Ball', 'Basketball', 'Football', 'Baseball', 'Tennis Ball', 'Golf Ball', 'Volleyball', 'Rugby Ball', 'Cricket Ball', 'Bowling Ball', 'Ping Pong Ball', 'Lacrosse Ball', 'Field Hockey Ball', 'Water Polo Ball', 'Handball', 'Squash Ball', 'Racquetball', 'Bocce Ball', 'Croquet Ball', 'Polo Ball'],
                'winter_sports': ['Ski', 'Snowboard', 'Ice Skates', 'Hockey Stick', 'Curling Stone', 'Bobsled', 'Luge', 'Skeleton Sled', 'Snowshoes', 'Ice Axe', 'Crampons', 'Ski Poles', 'Ski Boots', 'Snowboard Boots', 'Hockey Puck', 'Figure Skates', 'Speed Skates', 'Ski Goggles', 'Ski Helmet', 'Snow Tube'],
                
                # MUSICAL INSTRUMENTS
                'string_instruments': ['Electric Guitar', 'Acoustic Guitar', 'Bass Guitar', 'Violin', 'Viola', 'Cello', 'Double Bass', 'Harp', 'Ukulele', 'Banjo', 'Mandolin', 'Lute', 'Sitar', 'Balalaika', 'Koto', 'Guzheng', 'Pipa', 'Shamisen', 'Oud', 'Bouzouki'],
                'brass_instruments': ['Trumpet', 'Trombone', 'French Horn', 'Tuba', 'Cornet', 'Flugelhorn', 'Euphonium', 'Baritone Horn', 'Sousaphone', 'Piccolo Trumpet', 'Bass Trombone', 'Wagner Tuba', 'Ophicleide', 'Serpent', 'Alphorn', 'Didgeridoo', 'Shofar', 'Vuvuzela', 'Bugle', 'Post Horn'],
                'drums': ['Snare Drum', 'Bass Drum', 'Tom-tom', 'Floor Tom', 'Timpani', 'Bongo', 'Conga', 'Djembe', 'Tabla', 'Taiko', 'Cajón', 'Hang Drum', 'Steel Drum', 'Frame Drum', 'Bodhrán', 'Darbuka', 'Ashiko', 'Talking Drum', 'Dhol', 'Surdo'],
                
                # ARCHITECTURE
                'famous_buildings': ['Eiffel Tower', 'Statue of Liberty', 'Big Ben', 'Taj Mahal', 'Great Wall', 'Colosseum', 'Pyramids', 'Sphinx', 'Machu Picchu', 'Christ Redeemer', 'Sydney Opera House', 'Burj Khalifa', 'Empire State', 'Golden Gate Bridge', 'Tower Bridge', 'Notre Dame', 'Sagrada Familia', 'St Basils', 'Forbidden City', 'Angkor Wat'],
                'castles': ['Medieval Castle', 'Japanese Castle', 'Scottish Castle', 'German Castle', 'French Chateau', 'Irish Castle', 'Welsh Castle', 'Spanish Alcazar', 'Russian Kremlin', 'Indian Fort', 'Moorish Palace', 'Crusader Castle', 'Hill Fort', 'Water Castle', 'Sand Castle', 'Ice Castle', 'Fairy Tale Castle', 'Ruined Castle', 'Cliff Castle', 'Island Castle'],
                
                # ABSTRACT PATTERNS
                'mandalas': ['Flower Mandala', 'Geometric Mandala', 'Celtic Mandala', 'Tibetan Mandala', 'Hindu Mandala', 'Buddhist Mandala', 'Crystal Mandala', 'Nature Mandala', 'Animal Mandala', 'Chakra Mandala', 'Sacred Geometry', 'Zentangle Pattern', 'Kaleidoscope', 'Spiral Pattern', 'Fractal Design', 'Islamic Pattern', 'Moroccan Tile', 'Indian Rangoli', 'Native Pattern', 'Dream Catcher'],
                
                # SEASONAL
                'halloween': ['Jack-o-lantern', 'Witch', 'Ghost', 'Vampire', 'Werewolf', 'Zombie', 'Skeleton', 'Mummy', 'Frankenstein', 'Black Cat', 'Bat', 'Spider', 'Haunted House', 'Graveyard', 'Cauldron', 'Broomstick', 'Spell Book', 'Crystal Ball', 'Scarecrow', 'Candy Corn'],
                'christmas': ['Santa Claus', 'Reindeer', 'Snowman', 'Christmas Tree', 'Present', 'Candy Cane', 'Gingerbread Man', 'Snow Globe', 'Wreath', 'Stocking', 'Ornament', 'Angel', 'Star', 'Bells', 'Holly', 'Mistletoe', 'Elf', 'Sleigh', 'Fireplace', 'Nutcracker'],
                'easter': ['Easter Bunny', 'Easter Egg', 'Chick', 'Lamb', 'Spring Flowers', 'Basket', 'Chocolate Bunny', 'Peeps', 'Egg Hunt', 'Spring Garden', 'Butterfly', 'Daffodil', 'Tulip', 'Baby Animals', 'Pastel Eggs', 'Jelly Beans', 'Hot Cross Bun', 'Spring Bonnet', 'Easter Lily', 'Carrot'],
                
                # PROFESSIONS
                'heroes': ['Firefighter', 'Police Officer', 'Paramedic', 'Doctor', 'Nurse', 'Soldier', 'Pilot', 'Astronaut', 'Scientist', 'Teacher', 'Lifeguard', 'Park Ranger', 'Coast Guard', 'Mountain Rescue', 'Search Dog', 'Rescue Helicopter', 'EMT', 'Surgeon', 'Veterinarian', 'Marine Biologist'],
                'workers': ['Construction Worker', 'Mechanic', 'Electrician', 'Plumber', 'Carpenter', 'Welder', 'Painter', 'Roofer', 'Landscaper', 'Farmer', 'Miner', 'Logger', 'Fisherman', 'Factory Worker', 'Truck Driver', 'Train Engineer', 'Ship Captain', 'Air Traffic Controller', 'Crane Operator', 'Forklift Driver'],
                
                # ANIME/MANGA STYLE
                'anime_archetypes': ['Magical Girl', 'Mecha Pilot', 'Ninja', 'Samurai', 'Shrine Maiden', 'School Student', 'Idol Singer', 'Cat Girl', 'Fox Spirit', 'Demon Lord', 'Hero', 'Princess', 'Knight', 'Witch', 'Alchemist', 'Gunslinger', 'Swordsman', 'Martial Artist', 'Summoner', 'Time Traveler'],
                
                # SUPERHEROES (Generic types, not copyrighted)
                'hero_types': ['Flying Hero', 'Strong Hero', 'Fast Hero', 'Tech Hero', 'Magic Hero', 'Archer Hero', 'Shield Hero', 'Hammer Hero', 'Web Hero', 'Claw Hero', 'Fire Hero', 'Ice Hero', 'Lightning Hero', 'Wind Hero', 'Earth Hero', 'Water Hero', 'Mind Hero', 'Time Hero', 'Space Hero', 'Shadow Hero']
            },
            'all_themes': []
        }
        
        # Flatten all themes into one massive list
        for category, items in self.theme_database['categories'].items():
            for item in items:
                self.theme_database['all_themes'].append({
                    'name': item,
                    'category': category,
                    'full_desc': f"{item} from {category.replace('_', ' ')}"
                })
        
        # Save the massive database
        self.save_databases()
        logger.info(f"✅ Built database with {len(self.theme_database['all_themes'])} unique items across {len(self.theme_database['categories'])} categories")
    
    def generate_unique_book(self) -> Dict[str, Any]:
        """Generate a completely unique coloring book"""
        
        # Select random category or mix categories
        if random.random() < 0.3:  # 30% chance of mixed theme
            # Mix 2-3 random categories
            num_categories = random.randint(2, 3)
            selected_categories = random.sample(list(self.theme_database['categories'].keys()), num_categories)
            
            items = []
            for cat in selected_categories:
                items.extend(random.sample(self.theme_database['categories'][cat], min(5, len(self.theme_database['categories'][cat]))))
            
            title = f"Mixed Adventure {random.randint(1, 9999)}"
        else:
            # Single category book
            category = random.choice(list(self.theme_database['categories'].keys()))
            items = random.sample(self.theme_database['categories'][category], min(10, len(self.theme_database['categories'][category])))
            
            # Generate unique title
            category_clean = category.replace('_', ' ').title()
            title = f"{category_clean} Collection {random.randint(1, 9999)}"
        
        # Ensure uniqueness
        book_hash = hashlib.md5(f"{title}_{items}".encode()).hexdigest()
        if book_hash in self.used_combinations:
            # Recursively try again
            return self.generate_unique_book()
        
        self.used_combinations.add(book_hash)
        
        # Create book structure - NO TEXT ANYWHERE
        timestamp = int(time.time())
        book_data = {
            "book": {
                "title": title,
                "age_range": "4-99",  # Everyone can color!
                "paper": {
                    "size": "8.5x11in",
                    "dpi": 300,
                    "orientation": "portrait"
                },
                "style": "clean black white line art, thick outlines only, no shading, no text, no words, no letters",
                "negative": "",  # Empty - doesn't work with FLUX.1-schnell anyway
                "cover_prompt": f"collection of {', '.join(items[:3])}",
                "back_blurb": "",  # NO TEXT
                "pages": []
            }
        }
        
        # Create pages - NO TEXT, just pure scenes
        for i, item in enumerate(items[:20], 1):  # Up to 20 pages
            page = {
                "id": i,
                "text": "",  # ABSOLUTELY NO TEXT
                "scene": f"{item} in natural pose"  # Simple, clear description
            }
            book_data["book"]["pages"].append(page)
        
        # Add metadata
        book_data["book"]["metadata"] = {
            "unique_hash": book_hash,
            "categories": selected_categories if 'selected_categories' in locals() else [category],
            "book_type": "unique_theme_coloring",
            "generated_by": "Intelligent-Coloring-Author",
            "generation_time": datetime.now().isoformat()
        }
        
        return book_data
    
    def run_continuous_generation(self):
        """Run continuous unique book generation"""
        logger.info("🚀 Starting Intelligent Coloring Author")
        logger.info(f"📊 Database: {len(self.theme_database['all_themes'])} unique items")
        logger.info(f"📁 Output directory: {self.new_stories_dir}")
        logger.info(f"⏰ Generation interval: {self.generation_interval} seconds")
        
        self.running = True
        
        while self.running:
            try:
                # Generate unique book
                book_data = self.generate_unique_book()
                
                # Save to file
                timestamp = int(time.time())
                safe_title = "".join(c for c in book_data['book']['title'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '_')[:30]
                filename = f"unique_{safe_title}_{timestamp}.json"
                filepath = self.new_stories_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(book_data, f, indent=2, ensure_ascii=False)
                
                self.books_created += 1
                logger.info(f"✅ Created unique book #{self.books_created}: {book_data['book']['title']}")
                logger.info(f"📄 {len(book_data['book']['pages'])} pages, Categories: {book_data['book']['metadata']['categories']}")
                logger.info(f"🔒 Unique combinations used: {len(self.used_combinations)}")
                
                # Save databases periodically
                if self.books_created % 10 == 0:
                    self.save_databases()
                
                logger.info(f"💤 Waiting {self.generation_interval} seconds...")
                time.sleep(self.generation_interval)
                
            except KeyboardInterrupt:
                logger.info("⏹️  Stopping Intelligent Author")
                self.running = False
                break
                
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                time.sleep(30)
        
        # Final save
        self.save_databases()
        logger.info(f"🏁 Created {self.books_created} unique books")
        logger.info(f"📊 Used {len(self.used_combinations)} unique combinations")


if __name__ == "__main__":
    author = IntelligentColoringAuthor()
    author.run_continuous_generation()